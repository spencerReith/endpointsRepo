import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import src.libraries.setterLib as setterLib
import src.libraries.cencorshipLib as cencorshipLib
import src.libraries.getterLib as getterLib
import src.libraries.analyticsLib as analyticsLib


from flask import Flask, render_template, request

app = Flask(__name__)



## home
@app.route('/', methods=["GET"])
def home():
    return "sample home page, will lead to login or register"


## register
@app.route('/register', methods=["GET", "POST"])
def form():
    if request.method == "POST":
        email = request.form.get("email")
        sex = request.form.get("sex")
        prefSex = request.form.get("prefSex")
        major = request.form.get("major")
        minor = request.form.get("minor")
        skills = [request.form.get("skill1"), request.form.get("skill2"), request.form.get("skill3")]
        interests = [request.form.get("interest1"), request.form.get("interest2"), request.form.get("interest3")]
        blurbEntries = [request.form.get("noun1"), request.form.get("noun2"), request.form.get("noun3"), request.form.get("verb1"), request.form.get("verb2"), request.form.get("verb3"), request.form.get("adj1"), request.form.get("adj2"), request.form.get("adj3")]
        gpa = float(request.form.get("gpa"))
        ricePurity = float(request.form.get("ricePurity"))
        tindarIndex = analyticsLib.calcTindarIndex(gpa, ricePurity)

        
        if cencorshipLib.is_banned(email):
            return "this user is banned they should not be trying to log in"
        if getterLib.overCharLimit('skills', skills):
            return "over char limit for skills"
        if getterLib.overCharLimit('interests', interests):
            return "over char limit for interests"
        if cencorshipLib.contains_prof(skills):
            return "no profanity is allowed in skills"
        if cencorshipLib.contains_prof(interests):
            return "no profanity is allowed in interests"
        if cencorshipLib.contains_prof(blurbEntries):
            return "no profanity is allowed in your resume entries"
        
        userID = setterLib.createUser(email, 2026, sex, prefSex)
        setterLib.createProfile(userID, major, minor, skills, interests, blurbEntries)
        analyticsLib.addTindarIndexToDB(userID, tindarIndex)

        return render_template("register.html")
    else:
        return render_template("register.html")

