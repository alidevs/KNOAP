import json
import os
import fnmatch
from dotenv import load_dotenv
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
import datetime
from api.Database import Database

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
def testLogin(request):
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
<<<<<<< HEAD
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
				RETURNING *;""" % (
		first_name, last_name, gender, birthday, phone, street, city, zip_code, patient_email, date, notes, doctor,
		date)

		records = database.query(query)
		if type(records) is not JsonResponse:
			return JsonResponse({'records': records}, content_type="application/json")
	# return records

	# return JsonResponse(data)
	# return render(request, "Home.html")
	# return render(request, "Home.html", {"message": "Could not add patient"})
	return JsonResponse({"message": "Could not add patient"})
=======
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
        doctor = request.session['user']['id']
        notes = ""
        grade = 5

        query = """INSERT INTO KNOAP.patient (fname, lname, gender, birthday, phone, street, city, zipcode, email, registered, notes, assigned_doctor, last_activity,grade)
								VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s')
								RETURNING *;""" % (first_name, last_name, gender, birthday, phone, street, city, zip_code, patient_email, date, notes, doctor,date,grade)
        records = database.query(query)
        if type(records) is not JsonResponse:
           return redirect("/")

    # return JsonResponse(data)
    # return render(request, "Home.html")
    # return render(request, "Home.html", {"message": "Could not add patient"})
    return render(request, 'add_patient.html')
>>>>>>> 4d20f221ecd5a78f3bc079644513837a21183408


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
		# file = request.POST.get('image', False)
		file = request.FILES['image']

		full_path = f"{current_dir}\\TF_MODEL\\patient_saved_diagnosis\\{patient_id}.png"
		file_name = default_storage.save(full_path, file)

		result = tf_test_model(file_name)
		inserted_diagnosis = database.insert_new_patient_diagnosis(patient_id, result['prediction'],
																   result['confidence'], result['index'])

		new_path = f"{current_dir}\\TF_MODEL\\patient_saved_diagnosis\\{patient_id}_{inserted_diagnosis['id']}.png"
		os.rename(full_path, new_path)

		# images_dictionary = {k: v for v, k in enumerate(list_of_images)}
		# images_dictionary = dict(zip(range(len(list_of_images)), list_of_images))

		patient = database.get_patient_by_id(patient_id)

		data_to_send = {
			"name": f"{patient_id}_{inserted_diagnosis['id']}.png",
			"content-type": file.content_type,
			"size": file.size,
			"current_dir": current_dir,
			"results": result,
			"inserted_row": inserted_diagnosis,
			"doctor": request.session['user'],
			"patient": patient
		}

		return to_patient(request, patient_id, data_to_send)
		# return render(request, "Patient-detail.html", data_to_send)
	# return JsonResponse({"name": file.name, "content-type": file.content_type, "size": file.size, "current_dir": current_dir, "results": result, "inserted_row": inserted_diagnosis})
	else:
		return JsonResponse({"error": "No image uploaded OR GET request"})


def home(request):
<<<<<<< HEAD
	# GET /
	if request.session.has_key("user"):
		email = request.session['user']['email']
		id = request.session['user']['id']
		query = """SELECT * FROM KNOAP.patient where assigned_doctor ='%s';""" % (id)
		records = database.query(query)
		stri = json.dumps(records['records'], indent=4, sort_keys=True, default=str)
		count = records['count']
		patients_list = eval(stri)
		print(f"Going home with {email}")
		return render(request, 'main.html', {'patient': patients_list, 'count': count})
	else:
		print("You need to login")
		return redirect("/login/")


def to_patient(request, id, data=None):
	if request.session.has_key("user"):
		print(id)
		query = """SELECT * FROM KNOAP.patient where id ='%s';""" % (id)
		records = database.query(query)
		if (records['count'] == 0):
			raise Http404
		stri = json.dumps(records['records'], indent=4, sort_keys=True, default=str)
=======
    # GET /
    if request.session.has_key("user"):
        email = request.session['user']['email']
        id = request.session['user']['id']
        query = """SELECT * FROM KNOAP.patient where assigned_doctor ='%s';""" % (id)
        records = database.query(query)
        print(records['records'])
        stri = json.dumps(records['records'], indent=1, sort_keys=True, default=str)
        count = records['count']
        print(stri)
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
>>>>>>> 4d20f221ecd5a78f3bc079644513837a21183408

		patient = eval(stri)

		current_dir = os.path.dirname(__file__)
		list_of_images = fnmatch.filter(os.listdir(f"{current_dir}\\TF_MODEL\\patient_saved_diagnosis"),
										f'{id}_*.png')
		images_dictionary = dict()
		for item in list_of_images:
			images_dictionary[item] = humanbytes(
				os.path.getsize(f"{current_dir}\\TF_MODEL\\patient_saved_diagnosis\\{item}"))

		patient_diagnosis = database.get_patient_diagnosis(id)

		print(type(patient_diagnosis))
		print(patient_diagnosis)
		print(type(images_dictionary))
		print(images_dictionary)

		if data is not None:
			print(f"Data -> {data}")
			return render(request, 'Patient-detail.html', data)
		return render(request, 'Patient-detail.html', {'patient': patient, 'doctor': request.session['user'], "files": images_dictionary, "diagnosis": patient_diagnosis})
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
