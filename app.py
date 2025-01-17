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
def create_user(email, password, username, zone):
    login_session["user"] = auth.create_user_with_email_and_password(email, password)
    db.child("users").child(login_session["user"]["localId"]).set({
        "email": email,
        "password": password,
        "username": username,
        "zone" : zone
    })

#check if the user is loged in
def is_loged_in():
    return "user" in login_session and login_session["user"] is not None
    
#logout a user
def logout():
  login_session["user"] = None
  auth.current_user = None
  
def get_user_data(data):
    #check if a user exist and if it does retrun the user name
    if is_loged_in():
        return db.child("users").child(login_session["user"]["localId"]).get().val()[data]
    
    return "x"

def get_calander():
    zone = get_user_data("zone")
    if db.child("calander_events").child(zone).get().val() is not None:
        return json.dumps(list(db.child("calander_events").child(zone).get().val().values()))
    
    return []

# for the home page
@app.route("/", methods=['GET', 'POST'])
def home():
    if request.form == "POST" and is_loged_in():
        if request.args.get("f") == "f2":
            db.child("contact info").push({
            "name": request.form["name"],
            "email": get_user_data("email"),
            "msg": request.form["msg"]
            })
        else:
          db.child("event request").push({
            "name": request.form["name"],
            "email": get_user_data("email"),
            "region": request.form["region"],
            "number": request.form["number"],
            "date": request.form["date"]
            })  
    else:
        return render_template("index.html",
                           signedin=is_loged_in(),
                           username=get_user_data("username"))

#about page
@app.route("/about")
def about():
    #render the page with parameters
    return render_template("about.html",
                           signedin=is_loged_in(),
                           username=get_user_data("username"))

#page for content
@app.route("/events")
def contact():
    #render the page with parameters
    return render_template("events.html",
                           signedin=is_loged_in(),
                           username=get_user_data("username"))

#page for jobs
@app.route("/ranks")
def jobs():
    #render the page with parameters
    return render_template("ranks.html",
                           signedin=is_loged_in(),
                           username=get_user_data("username"))

#page for profile
@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if request.method == "POST":
        logout()
        return redirect(url_for("signin"))
    #render the page with parameters
    return render_template("profile.html",
                           signedin=is_loged_in(),
                           username=get_user_data("username"))

@app.route("/meme_of_the_day")
def meme_of_the_day():
    return render_template("MemeOfTheDay.html",
                           signedin=is_loged_in(),
                           username=get_user_data("username"))

#calander page
@app.route("/calander", methods=['GET', 'POST'])
def calander():
    #if post add new event to calander
    zone = get_user_data("zone")
    if request.method == "POST":
        event_data = request.get_json()
        db.child("calander_events").child(zone).push(event_data)
    
    
    #render the page
    return render_template("calander.html", events=get_calander(),
                           signedin=is_loged_in(),
                           username=get_user_data("username"))
    
    

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
        create_user(request.form["email"],request.form["password"], request.form["username"], request.form["zone"])
        return redirect(url_for('home'))
    except:
        return render_template("signup.html", error="something went wrong pls try again!")

#run the app    
if __name__ == "__main__":
    app.run(debug=True)