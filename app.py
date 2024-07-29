#imports
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session 
import pyrebase
import json

#app set up
app = Flask(__name__)
app.config['SECRET_KEY']="*******"

#config for the firebase
firebaseConfig = {
  "apiKey": "AIzaSyAaK61ppL38gxmjhYV07B51HgIHqvoukaY",
  "authDomain": "case-study-c956e.firebaseapp.com",
  "projectId": "case-study-c956e",
  "storageBucket": "case-study-c956e.appspot.com",
  "messagingSenderId": "40920472506",
  "appId": "1:40920472506:web:2a608ea576f7dd8a2cdb83",
  "measurementId": "G-8VBBNDK5MF",
  "databaseURL": "https://case-study-c956e-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

#create a new user using parameters
def create_user(email, password, username):
    login_session["user"] = auth.create_user_with_email_and_password(email, password)
    db.child("users").child(login_session["user"]["localId"]).set({
        "email": email,
        "password": password,
        "username": username,
        "questions_id": []
    })
    
#logout a user
def logout():
  login_session["user"] = None
  auth.current_user = None
  
def get_username():
    #check if a user exist and if it does retrun the user name
    user = db.child("users").child(login_session["user"]["localId"]).get().val()
    if user is not None:
        return user["username"]
    
    return "x"

# for the home page
@app.route("/")
def home():
    return render_template("index.html",
                           signedin=db.child("users").child(login_session["user"]["localId"]).get().val() is not None,
                           username=get_username())

#about page
@app.route("/about")
def about():
    #render the page with parameters
    return render_template("about.html",
                           signedin=db.child("users").child(login_session["user"]["localId"]).get().val() is not None,
                           username=get_username())

#page for content
@app.route("/events")
def contact():
    #render the page with parameters
    return render_template("events.html",
                           signedin=db.child("users").child(login_session["user"]["localId"]).get().val() is not None,
                           username=get_username())

#page for jobs
@app.route("/jobs")
def jobs():
    #render the page with parameters
    return render_template("jobs.html",
                           signedin=db.child("users").child(login_session["user"]["localId"]).get().val() is not None,
                           username=get_username())

#page for profile
@app.route("/profile")
def profile():
    #render the page with parameters
    return render_template("profile.html",
                           signedin=db.child("users").child(login_session["user"]["localId"]).get().val() is not None,
                           username=get_username())

#calander page
@app.route("/calander", methods=['GET', 'POST'])
def calander():
    if request.method == "POST":
        event_data = request.get_json()
        # Process the event data as needed
        db.child("calander_events").push(event_data)
    
    # For GET request, render the page with sample events
    
    return render_template("calander.html", events=db.child("calander_events").get().val())
    
    

#sign in page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    #render the page
    if request.method == "GET":
        return render_template("signin.html")
    
    #if method is post sign in the user
    try:
        login_session["user"] = auth.sign_in_with_email_and_password(request.form["email"], request.form["password"])
        return redirect(url_for('home'))
    except:
        return render_template("signin.html", error="something went wrong pls try again!")
    
#sign up page   
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #render the page
    if request.method == "GET":
        return render_template("signup.html")
    
    #if method is post create a new user
    try:
        create_user(request.form["email"],request.form["password"], request.form["username"])
        return redirect(url_for('home'))
    except:
        return render_template("signup.html", error="something went wrong pls try again!")

#run the app    
if __name__ == "__main__":
    app.run(debug=True)