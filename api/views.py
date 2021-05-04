import json
import os
import fnmatch
from dotenv import load_dotenv
from django.http import JsonResponse, Http404
import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt

from api.Database import Database
from api.TF_MODEL.TestModel import tf_test_model
import psycopg2
from psycopg2.extras import RealDictCursor
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

database = Database()


@csrf_exempt
def login(request):
    # GET /login
    if request.method == "GET":
        if request.session.has_key('email'):
            return JsonResponse({"email": request.session['email']})
        else:
            return render(request, 'Login_register.html')

    # POST /login
    elif request.method == "POST":
        input_email = request.POST.get('email')
        input_password = request.POST.get('password')
        print(f'Email {input_email}\t\tPassword {input_password}')

        query = """	SELECT * FROM KNOAP.doctor
                    WHERE email = '%s'
                    AND password = '%s';
        """ % (input_email, input_password)
        records = database.query(query)

        if type(records) is not JsonResponse:
            if records['count'] > 0:
                request.session['user'] = records['records'][0]
                return redirect("/", {"email": input_email})
            else:
                return JsonResponse({'error': 'Email or password may be incorrect'})
        return records


def logout(request):
    # GET /logout
    if request.method == "GET":
        try:
            # print(f"Logging out of {request.session['email']}")
            del request.session['user']
            return redirect("/login/")

        except Exception as e:
            # print(f"Failed to logout\n{query_str(e)}")
            return JsonResponse({"error": e})


@csrf_exempt
def register(request):
    # GET /register
    if request.method == "GET":
        return render(request, "login.html")

    # POST /register
    elif request.method == "POST":
        input_fname = request.POST.get('firstname')
        input_lname = request.POST.get('lastname')
        input_email = request.POST.get('email')
        input_password = request.POST.get('password')

        query = """INSERT INTO KNOAP.doctor (fname, lname, email, password,authorized)
                        VALUES ('%s', '%s', '%s', '%s', '%s')
                        returning *;""" % (input_fname, input_lname, input_email, input_password, 'n')
        records = database.query(query)
        if type(records) is not JsonResponse:
            return redirect("/login/")

        return records


# def reset(request):
# 	# GET /reset
# 	if request.method == "GET":
# 		return render(request, "Reset.html")
#
# 	# POST /reset
# 	elif request.method == "POST":
# 		email = request.POST.get('email')
# 		try:
# 			auth.send_password_reset_email(email)
# 			message = "An email to reset password is successfully sent"
# 			return render(request, "Reset.html", {"msg": message})
# 		except:
# 			message = "Something went wrong, Please check the email you provided is registered or not"
# 			return render(request, "Reset.html", {"msg": message})


@csrf_exempt
def add_patient(request):
    if request.method == "POST":
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        gender = request.POST.get('gender')
        birthday = request.POST.get('birthday')
        city = request.POST.get('city')
        phone = request.POST.get('phone')
        street = request.POST.get('street')
        zip_code = request.POST.get('zipCode')
        patient_email = request.POST.get('email')
        doctor = request.session['user']['id']
        notes = ""
        grade = 5

        query = f"""INSERT INTO KNOAP.patient (fname, lname, gender, birthday, phone, street, city, zipcode, email, notes, assigned_doctor)
                                VALUES ('{first_name}', '{last_name}', '{gender}', '{birthday}', '{phone}', '{street}', '{city}', '{zip_code}', '{patient_email}', '{notes}', '{doctor}')
                                RETURNING *;"""
        records = database.query(query)
        if type(records) is not JsonResponse:
            return redirect("/")
    return render(request, 'add_patient.html')


def list_all_doctors(request):
    print(os.environ.get("HOST"))
    print(request.session.has_key('user'))
    records = database.query('SELECT * FROM KNOAP.doctor;')
    return JsonResponse({'records': records})


@csrf_exempt
def add_patient_file(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        patient_does_exist = database.does_patient_exist(patient_id)
        if not patient_does_exist:
            return JsonResponse({"error": f"No patient exist with id {patient_id}"})

        current_dir = os.path.dirname(__file__)
        file = request.FILES['image']

        full_path = os.path.join(current_dir, "TF_MODEL", "patient_saved_diagnosis", f"{patient_id}.png")
        file_name = default_storage.save(full_path, file)

        result = tf_test_model(file_name)
        inserted_diagnosis = database.insert_new_patient_diagnosis(patient_id, result['prediction'],
                                                                   result['confidence'], result['index'])

        new_path = os.path.join(current_dir, "TF_MODEL", "patient_saved_diagnosis",
                                f"{patient_id}_{inserted_diagnosis['id']}.png")
        os.rename(full_path, new_path)


        return redirect(f'/patient/{patient_id}/')
    else:
        return JsonResponse({"error": "No image uploaded OR GET request"})


def home(request, patients=None):
    # GET /
    if request.session.has_key("user"):
        email = request.session['user']['email']
        id = request.session['user']['id']
        query = """SELECT * FROM KNOAP.patient where assigned_doctor ='%s';""" % (id)
        records = database.query(query)
        stri = json.dumps(records['records'], indent=4, sort_keys=True, default=str)
        count = records['count']
        patients_list = eval(stri)
        if patients is not None:
            return render(request, 'main.html', {'patient': patients, 'count': count})
        return render(request, 'main.html', {'patient': patients_list, 'count': count})
    else:
        return redirect("/login/")


def to_patient(request, id, data=None):
    if request.session.has_key("user"):
        print(id)
        query = """SELECT * FROM KNOAP.patient where id ='%s';""" % (id)
        records = database.query(query)
        if (records['count'] == 0):
            raise Http404
        stri = json.dumps(records['records'], indent=4, sort_keys=True, default=str)

        patient = eval(stri)

        current_dir = os.path.dirname(__file__)
        list_of_images = fnmatch.filter(os.listdir(os.path.join(current_dir, "TF_MODEL", "patient_saved_diagnosis")),
                                        f'{id}_*.png')
        images_dictionary = dict()
        for item in list_of_images:
            images_dictionary[item] = humanbytes(
                os.path.getsize(os.path.join(current_dir, "TF_MODEL", "patient_saved_diagnosis", item)))

        patient_diagnosis = database.get_patient_diagnosis(id)

        if data is not None:
            print(f"Data -> {data}")
            return render(request, 'Patient-detail.html', data)
        default_data = {'patient': patient, 'doctor': request.session['user'], "files": images_dictionary,
                       "diagnosis": patient_diagnosis}
        print(f"Default data -> {default_data}")
        return render(request, 'Patient-detail.html', default_data)
    else:
        return redirect("/login/")


@csrf_exempt
def edit_patient(request, id):
    if request.method == "POST":
        patient_id = id

        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        gender = request.POST.get('gender')
        birthday = request.POST.get('birthday')
        city = request.POST.get('city')
        phone = request.POST.get('phone')
        street = request.POST.get('street')
        zip_code = request.POST.get('zipcode')
        patient_email = request.POST.get('email')
        notes = request.POST.get('notes')
        query = f"""UPDATE KNOAP.patient set (fname, lname, gender, birthday, phone, street, city, zipcode, email, notes)
                                        = ('{first_name}', '{last_name}', '{gender}', '{birthday}', '{phone}', '{street}', '{city}', '{zip_code}', '{patient_email}', '{notes}') where id ='{patient_id}'
                                        RETURNING *;"""

        records = database.query(query)
        if type(records) is not JsonResponse:
            return to_patient(request, patient_id)


        return to_patient(request, patient_id)


    elif request.method == "GET":
        if request.session.has_key("user"):
            print(id)
            query = """SELECT * FROM KNOAP.patient where id ='%s';""" % (id)
            records = database.query(query)
            if (records['count'] == 0):
                raise Http404
            stri = json.dumps(records['records'], indent=4, sort_keys=True, default=str)

        patient = eval(stri)
        print(type(patient))
        return render(request, 'edit_patient.html', {'patient': patient, 'doctor': request.session['user']})
    else:
        print("You need to login")
        return redirect("/login/")


@csrf_exempt
def search(request):
    if request.method == "POST":
        query = request.POST.get('query')
        print(f"Searching {query} ..")

        if query is not None:
            records = database.search_for_patient(query)
            return home(request, records)
        return home(request)


def humanbytes(B):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)


def delete_patient(id, request):
    if request.session.has_key("user"):
        print(id)
        doctor = request.session['user']['id']
        query1 = """DELETE FROM KNOAP.diagnosis where patient_id ='%s' RETURNING *;""" % (id)
        database.query(query1)
        query = """DELETE FROM KNOAP.patient where id ='%s' RETURNING *;""" % (id)
        database.query(query)

        return redirect("/")
