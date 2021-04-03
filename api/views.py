from django.shortcuts import render, redirect
import pyrebase
import datetime

config = {
	"apiKey": "AIzaSyAEF7iVukPX1i3uN046xcisF0lQSMe-YqA",
	"authDomain": "knoap-a1063.firebaseapp.com",
	"databaseURL": "https://knoap-a1063-default-rtdb.europe-west1.firebasedatabase.app",
	"projectId": "knoap-a1063",
	"storageBucket": "knoap-a1063.appspot.com",
	"messagingSenderId": "631782163056",
	"appId": "1:631782163056:web:457b4d40ea69c1b8d0eab5",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database = firebase.database()


def home(request):
	if request.session.has_key("email"):
		email = request.session['email']
		print(f"Signed in as {email}")
		return render(request, 'Home.html', {"email": email})
	else:
		print("You need to login")
		return redirect("/login/")


def login(request):
	# GET /login
	if request.method == "GET":
		if request.session.has_key('email'):
			print(f"Session key {request.session['email']}")
			return redirect('/', {"email": request.session['email']})
		else:
			return render(request, 'Login.html')

	# POST /login
	elif request.method == "POST":
		input_email = request.POST.get('email')
		input_password = request.POST.get('password')
		print(f'Email {input_email}\t\tPassword {input_password}')

		try:
			user = auth.sign_in_with_email_and_password(input_email, input_password)
			request.session["email"] = input_email
		except Exception as e:
			message = str(e)
			print(f'Failed to login {e}')
			return render("Login.html", {"message": message})

		return redirect("/", {"email": request.session["email"]})


def logout(request):
	try:
		print(f"Logging out of {request.session['email']}")
		del request.session['email']
	except Exception as e:
		print(f"Failed to logout\n{str(e)}")
	return redirect("/login/")


def register(request):
	# GET /register
	if request.method == "GET":
		return render(request, "Register.html")

	# POST /register
	elif request.method == "POST":
		input_email = request.POST.get('email')
		input_password = request.POST.get('password')

		try:
			user = auth.create_user_with_email_and_password(input_email, input_password)
			uid = user['localId']
			idtoken = request.session['email']
			print(f'UID\n{uid}\nToken\n{idtoken}')
		except Exception as e:
			print(str(e))
			return render(request, "Register.html")
		return render(request, "Login.html")


def reset(request):
	# GET /reset
	if request.method == "GET":
		return render(request, "Reset.html")

	# POST /reset
	elif request.method == "POST":
		email = request.POST.get('email')
		try:
			auth.send_password_reset_email(email)
			message = "An email to reset password is successfully sent"
			return render(request, "Reset.html", {"msg": message})
		except:
			message = "Something went wrong, Please check the email you provided is registered or not"
			return render(request, "Reset.html", {"msg": message})


def add_patient(request):
	"""

		:type request: object
		"""
	firstName = request.POST.get('fname')
	lastName = request.POST.get('lname')
	gender = request.POST.get('gender')
	birth = request.POST.get('Birthday')
	city = request.POST.get('City')
	phone = request.POST.get('Mobile')
	street = request.POST.get('Street')
	zipCode = request.POST.get('zip')
	patientEmail = request.POST.get('email')
	date = datetime.date.today()
	doctor = request.session["email"]

	data = {'firstName': firstName
		, 'lastName': lastName
		, 'gender': gender
		, 'birth': birth
		, 'city': city
		, 'phone': phone
		, 'street': street
		, 'zipCode': zipCode
		, 'email': patientEmail
		, 'date': date
		, 'doctorEmail': doctor}
	database.child("patients").path(data)

	return render(request, "Home.html")
