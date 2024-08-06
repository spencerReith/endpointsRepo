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
import src.libraries.authenticationLib as authenticationLib
import src.libraries.messagingLib as messagingLib


from flask import Flask, render_template, request, redirect, session



app = Flask(__name__)
app.secret_key = "inspector"


## home
@app.route('/', methods=["GET"])
def home():
    return "sample home page, will lead to login or register"



## create resume
@app.route('/register', methods=["GET", "POST"])
def createResume():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        sex = request.form.get("sex")
        prefSex = request.form.get("prefSex")
        major = request.form.get("major")
        minor = request.form.get("minor")
        skills = [request.form.get("skill1"), request.form.get("skill2"), request.form.get("skill3")]
        interests = [request.form.get("interest1"), request.form.get("interest2"), request.form.get("interest3")]
        blurbEntries = [request.form.get("noun1"), request.form.get("noun2"), request.form.get("noun3"), request.form.get("verb1"), request.form.get("verb2"), request.form.get("verb3"), request.form.get("adj1"), request.form.get("adj2"), request.form.get("adj3")]
        try:
            gpa = float(request.form.get("gpa"))
            ricePurity = float(request.form.get("ricePurity"))
            tindarIndex = analyticsLib.calcTindarIndex(gpa, ricePurity)
        except:
            return "you need to fill in values in all fields"
        
        ## ensure all fields are filled out
        for key in request.form:
            value = request.form.get(key)
            if not value:
                return "you need to fill in all fields"
        
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
        if authenticationLib.emailInDB(email):
            return "this email is already in use."
        
        userID = setterLib.createUser(email, 2026, sex, prefSex)
        authenticationLib.insert_passcode(userID, email, password)
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
        try:
            if authenticationLib.passwordIsAccurate(email, password) == True:
                userID = int(authenticationLib.pullUserID(email))
                session["userID"] = userID
                session["email"] = email
                newDeck = getterLib.getDeck(userID)
                session["deck"] = newDeck
                return redirect('/recruiting')
            else:
                return "incorrect password"
        except:
            return "critical system failure"
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
def profile():
    userID = session["userID"]
    if request.method == "POST":
        print("method is post")
        emailEND = request.form.get("emailEND")
        message = request.form.get("message")
        emailA = request.form.get("emailA")
        emailB = request.form.get("emailB")
        
        if emailEND != None and message != None:
            if cencorshipLib.contains_prof(message):
                return "message contains profanity, this is not allowed"
            print("making endorsement")
            endorsementLib.attemptEndorsement(userID, emailEND, message)
        print("success")
        print("email a", emailA)
        print("email b", emailB)
        if emailA != None and emailB != None:
            print("attempting ref")
            if len(emailA) > 0 and len(emailB) > 0:    
                print('succes through here')
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
def recruiting():
    userID = session["userID"]
    
    if request.method == "POST":
        choice = request.form.get("choice")
    print("here's the deck", session["deck"])
    return render_template("recruiting.html", deck=session["deck"])


## recruiting
@app.route('/leaderboard', methods=["GET"])
def leaderboard():    
    leaderboardDict = getterLib.getLeaderboard()
    profilesDict = {}
    i = 1
    for leaderID in leaderboardDict:
        leader = getterLib.getProfile(leaderID)
        profilesDict[i] = leader
        i+=1

    return render_template("leaderboard.html", profilesDict=profilesDict)

## connections
@app.route('/connections', methods=["GET"])
def connections(userID):    
    connectionsDict = getterLib.getConnections(userID)
    return render_template("connections.html", connectionsDict=connectionsDict)

@app.route('/messaging', methods=["GET", "POST"])
def messaging():
    self_userID = session["userID"]
    email = "a.26@dartmouth.edu"
    if request.method == "POST":
        provided_message = request.form.get("message")
        messagingLib.sendMessage(session["email"], email, provided_message)

    mTupleList = messagingLib.retrieveMessages(self_userID, email)
    return render_template("messaging.html", email=email, mTupleList=mTupleList)