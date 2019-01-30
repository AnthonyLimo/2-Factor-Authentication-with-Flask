import os
import africastalking
from flask import Flask, request, render_template, url_for, session, redirect, g
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

username = "sandbox"
api_key = "c73616e0eb2e292cf0590ee111097f726dc71ca4ae2d20bd38d79a49564d5d4b"
user_phone_number = "+254727545805"
global config_code
config_code = None

africastalking.initialize(username, api_key)

sms = africastalking.SMS

def send_verification_code():
	random_number = random.randint(1,10001)
	config_code = random_number

	message = "Your login verification code is: " + str(config_code)

	#check if this function executed properly

	def on_finish(error, response):
		if error is not None:
			raise error

		print(response)

	sms.send(message, [user_phone_number], callback=on_finish)


#add the new user to the session object
@app.before_request
def before_request():
	g.user = None
	if "user" in session:
		g.user = session["user"]



#main page that contains the login path
@app.route("/", methods=["POST","GET"])
def index(): 
	session.pop("user", None)
	if request.method == "POST":
		if request.form["password"] == "password":
			session["user"] = request.form["username"]
			return redirect(url_for("verify"))

	return render_template("index.html") 


#verification path, if the code is accepted, then we can verify its the same one generated
@app.route("/verify", methods=["POST","GET"])
def verify():
	if request.method == "GET":
		send_verification_code()
	elif request.method == "POST":
		code = request.form["code"]
		code_string = str(code)
		config_code_string = str(config_code)
		if code_string == config_code_string:
			print(config_code)
			return redirect(url_for("home"))
		else: 
			return redirect(url_for("index"))
	else:
		redirect(url_for("index"))
	
	return render_template("verification.html")



@app.route("/home", methods=["GET","POST"])
def home():
	if request.method == "GET":
		if g.user:
			return render_template("home.html")
		else:
			return render_template("index.html")



if __name__ == "__main__":
	app.run(debug=True)