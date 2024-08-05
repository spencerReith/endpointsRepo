import os
import matplotlib as plt
import io
import base64
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import src.libraries.setterLib as setterLib
import src.libraries.cencorshipLib as cencorshipLib
import src.libraries.getterLib as getterLib
import src.libraries.analyticsLib as analyticsLib
import src.libraries.endorsementLib as endorsementLib
import src.libraries.referralLib as referralLib



from flask import Flask, render_template, request

app = Flask(__name__)



## home
@app.route('/', methods=["GET"])
def home():
    return "sample home page, will lead to login or register"


## register
@app.route('/register', methods=["GET", "POST"])
def register():
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

## register
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email, password)

        return recruiting(49400)
    else:
        return render_template("login.html")

## other user's profile
@app.route('/otherProfile', methods=["GET", "POST"])
def other_profile(userID):
    profileDict = getterLib.getProfile(userID)
    name = profileDict['name']
    email = profileDict['email']
    major = profileDict['major']
    minor = profileDict['minor']
    skills = profileDict['skills']
    interests = profileDict['interests']
    tindarIndex = round(profileDict['tindarIndex'], 4)
    endorsements = profileDict['endorsements']
    blurb = profileDict['blurb']

    html_str = analyticsLib.getHistogram(userID)

    return render_template("otherProfile.html", name=name, email=email, major=major, minor=minor, skills=skills, interests=interests, tindarIndex=tindarIndex, endorsements=endorsements, blurb=blurb, html_str=html_str)
    # return render_template("otherProfile.html", name=name, email=email, major=major, minor=minor, skills=skills, interests=interests, tindarIndex=tindarIndex, endorsements=endorsements, blurb=blurb, img_data=img_data)


## personal profile
@app.route('/profile', methods=["GET", "POST"])
def profile(userID):
    if request.method == "POST":
        emailEND = request.form.get("emailEND")
        message = request.form.get("message")
        emailA = request.form.get("emailA")
        emailB = request.form.get("emailB")
        
        if emailEND != None and message != None:
            if cencorshipLib.contains_prof(message):
                return "message contains profanity, this is not allowed"
            print("making endorsement")
            endorsementLib.attemptEndorsement(userID, emailEND, message)
            
        if emailA != None and emailB != None:
            if len(emailA) > 0 and len(emailB) > 0:    
                print("making referral")
                referralLib.attemptReferral(userID, emailA, emailB)
        
        
    profileDict = getterLib.getProfile(userID)
    name = profileDict['name']
    print("name is right here: ", name)
    email = profileDict['email']
    major = profileDict['major']
    minor = profileDict['minor']
    skills = profileDict['skills']
    interests = profileDict['interests']
    tindarIndex = round(profileDict['tindarIndex'], 4)
    endorsements = profileDict['endorsements']
    blurb = profileDict['blurb']

    endRefs = getterLib.getEndRefs(userID)
    endorsementsRemaining = endRefs['remainingEndorsements']
    referralsRemaining = endRefs['remainingReferrals']

    return render_template("profile.html", name=name, email=email, major=major, minor=minor, skills=skills, interests=interests, tindarIndex=tindarIndex, endorsements=endorsements, blurb=blurb, endorsementsRemaining=endorsementsRemaining, referralsRemaining=referralsRemaining)



## recruiting
@app.route('/recruiting', methods=["GET", "POST"])
def recruiting(userID):
    if request.method == "POST":
        choice = request.form.get("choice")
    
    deck = getterLib.getDeck(userID)
    return render_template("recruiting.html", deck=deck)


## recruiting
@app.route('/leaderboard', methods=["GET"])
def leaderboard():    
    leaderboardDict = getterLib.getLeaderboard()
    return render_template("leaderboard.html", leaderboardDict=leaderboardDict)

## connections
@app.route('/connections', methods=["GET"])
def connections(userID):    
    connectionsDict = getterLib.getConnections(userID)
    return render_template("connections.html", connectionsDict=connectionsDict)


