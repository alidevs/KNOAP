import json
import os
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

from django.views.decorators.csrf import csrf_exempt

database = Database()


def addP(request):
    # GET /
    if request.session.has_key("user"):
        email = request.session['user']['email']
        print(f"Signed in as {email}")
        return render(request, 'Home.html', {"email": email})
    else:
        print("You need to login")
        return redirect("/login/")


# def home(request):
# 		# GET /
# 		if request.session.has_key("user"):
# 			email = request.session['user']['email']
# 			print(f"Signed in as {email}")
# 			return render(request, 'main.html')
# 			#return render(request, 'main.html', {"email": email})
# 		else:
# 			print("You need to login")
# 			return redirect("/login/")
#

@csrf_exempt
def login(request):
    # GET /login
    if request.method == "GET":
        if request.session.has_key('email'):
            return JsonResponse({"email": request.session['email']})
        else:
            return render(request, 'Login.html')

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
            return JsonResponse({"message": "Logged out successfully"})
        except Exception as e:
            # print(f"Failed to logout\n{query_str(e)}")
            return JsonResponse({"error": e})


# return redirect("/login/")


@csrf_exempt
def register(request):
    # GET /register
    if request.method == "GET":
        return render(request, "Register.html")

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
            request.session['user'] = records[0]
            return JsonResponse({'records': records}, content_type="application/json")
        return records


# return render(request, "Login.html")


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
        date = datetime.date.today()
        doctor = request.POST.get('doctorEmail')
        notes = request.POST.get('notes')

        data = {'firstName': first_name,
                'lastName': last_name,
                'gender': gender,
                'birthday': birthday,
                'city': city,
                'phone': phone,
                'street': street,
                'zipCode': zip_code,
                'email': patient_email,
                'date': date,
                'doctorEmail': doctor,
                'notes': notes}

        query = """INSERT INTO KNOAP.patient (fname, lname, gender, birthday, phone, street, city, zipcode, email, registered, notes, assigned_doctor, last_activity)
								VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s')
								RETURNING *;""" % (first_name, last_name, gender, birthday, phone, street, city, zip_code, patient_email, date, notes, doctor, date)
		records = database.query(query)
		if type(records) is not JsonResponse:
			return JsonResponse({'records': records}, content_type="application/json")
		return records

	# return JsonResponse(data)
	# return render(request, "Home.html")
	# return render(request, "Home.html", {"message": "Could not add patient"})
	return JsonResponse({"message": "Could not add patient"})


def list_all_doctors(request):
    print(os.environ.get("HOST"))
    print(request.session.has_key('user'))
    records = database.query('SELECT * FROM KNOAP.doctor;')
    return JsonResponse({'records': records})


@csrf_exempt
def add_patient_file(request):
	patient_id = request.POST.get("patient_id")
	patient_does_exist = database.does_patient_exist(patient_id)
	if not patient_does_exist:
		return JsonResponse({"error": f"No patient exist with id {patient_id}"})

	current_dir = os.path.dirname(__file__)
	file = request.FILES['image']

	full_path = f"{current_dir}\\TF_MODEL\\patient_saved_diagnosis\\{patient_id}.png"
	file_name = default_storage.save(full_path, file)

	result = tf_test_model(file_name)
	inserted_diagnosis = database.insert_new_patient_diagnosis(patient_id, result['prediction'], result['confidence'], result['index'])

	new_path = f"{current_dir}\\TF_MODEL\\patient_saved_diagnosis\\{patient_id}_{inserted_diagnosis['id']}.png"
	os.rename(full_path, new_path)

	return JsonResponse({"name": file.name, "content-type": file.content_type, "size": file.size, "current_dir": current_dir, "results": result, "inserted_row": inserted_diagnosis})


# def test_model(request):
# 	return JsonResponse({"success": tf_test_model()}, content_type="application/json")


def home(request):
    # GET /
    if request.session.has_key("user"):
        email = request.session['user']['email']
        id = request.session['user']['id']
        query = """SELECT * FROM KNOAP.patient where assigned_doctor ='%s';""" % (id)
        records = database.query(query)
        stri = json.dumps(records['records'], indent=4, sort_keys=True, default=str)
        count = records['count']
        patients_list = eval(stri)
        return render(request, 'main.html', {'patient': patients_list, 'count': count})
    else:
        print("You need to login")
        return redirect("/login/")


def to_patient(request, id):
    if request.session.has_key("user"):
        print(id)
        query = """SELECT * FROM KNOAP.patient where id ='%s';""" % (id)
        records = database.query(query)
        if (records['count'] == 0):
            raise Http404
        stri = json.dumps(records['records'], indent=4, sort_keys=True, default=str)

        patient = eval(stri)
        print(type(patient))
        return render(request, 'Patient-detail.html', {'patient': patient, 'doctor': request.session['user']})
    else:
        print("You need to login")
        return redirect("/login/")

def edit_patient(request, id):
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

