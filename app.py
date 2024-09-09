import os
import matplotlib as plt
import io
import base64
import sys
import json


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
import src.libraries.snsLib as snsLib


from flask import Flask, render_template, request, session, redirect, jsonify
# from flask_session import Session
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'inspector'
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for API endpoints


## home
@app.route('/', methods=["GET"])
def home():
    return "sample home page, will lead to login or register"

@app.route('/api/verifyEmail-1', methods=['POST'])
def verifyEmail1():
    data = request.get_json()
    email = data.get('email')
    session['emailKey'] = snsLib.send_verification_email(email)
    return jsonify({"redirect": "/verifyEmail2"})


@app.route('/api/verifyEmail-2', methods=['POST'])
def verifyEmail2():
    print("inside of verifyEmail2")
    data = request.get_json()
    given_key = data.get('emailKey')
    print("User gave key:", given_key)
    print("Actual key: ", session['emailKey'])
    if given_key != session['emailKey']:
        return jsonify({'error': 'Key Incorrect'}), 400
    else:
        return jsonify({'res': 'Valid Login'}), 200


## create resume
@app.route('/api/register', methods=["GET", "POST"])
def createResume():
    if request.method == "POST":
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        sex = data.get('sex')
        prefSex = data.get('prefSex')
        major = data.get('major')
        minor = data.get('minor')
        skill1 = data.get('skill1')
        skill2 = data.get('skill2')
        skill3 = data.get('skill3')
        skills = [skill1, skill2, skill3]
        interest1 = data.get('interest1')
        interest2 = data.get('interest2')
        interest3 = data.get('interest3')
        interests = [interest1, interest2, interest3]
        rawGPA = data.get('gpa')
        rawRP = data.get('ricePurity')
        try:
            gpa = float(rawGPA)
            ricePurity = float(rawRP)
            tindarIndex = analyticsLib.calcTindarIndex(gpa, ricePurity)
        except:
            return jsonify({'error': 'Registration error'}), 400
       
        if cencorshipLib.is_banned(email):
            return jsonify({'error': 'Registration error: User is Banned'}), 400
        if getterLib.overCharLimit('skills', skills):
            return jsonify({'error': 'Registration error: Skills over Char Limit'}), 400
        if getterLib.overCharLimit('interests', interests):
            return jsonify({'error': 'Registration error: Interests over Char Limit'}), 400
        if cencorshipLib.contains_prof(skills):
            return jsonify({'error': 'Registration error: Profanity in Skills'}), 400
        if cencorshipLib.contains_prof(interests):
            return jsonify({'error': 'Registration error: Profanity in Interests'}), 400
        if authenticationLib.emailInDB(email):
            return jsonify({'error': 'Registration error: Email Already Registered'}), 400
        
        userID = setterLib.createUser(email, 2026, sex, prefSex)
        authenticationLib.insert_passcode(userID, email, password)
        setterLib.createProfile(userID, major, minor, skills, interests)
        analyticsLib.addTindarIndexToDB(userID, tindarIndex)
        
        session['userID'] = userID
        session['email'] = email
        newDeck = getterLib.getDeck(userID)
        session['deck'] = newDeck

        return jsonify({'message': 'Registration successful'})
    else:
        return jsonify({'error': 'Registration error'}), 400

@app.route('/api/login', methods=["POST"])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if request.method == "POST":
        try:
            if authenticationLib.passwordIsAccurate(email, password):
                userID = int(authenticationLib.pullUserID(email))
                session['userID'] = userID
                session['email'] = email
                newDeck = getterLib.getDeck(userID)
                session['deck'] = newDeck
                # Serialize the session data to a JSON string
                session_data = json.dumps(dict(session))
    
                # Calculate the size of the session data in bytes
                session_size = len(session_data.encode('utf-8'))
                
                print("session_size:", session_size)
                # Return a JSON response with the redirect URL
                 # This should show all the session variables
                return jsonify({"redirect": "/recruiting"})
            else:
                return jsonify({"error": "Incorrect password"}), 401
        except Exception as e:
            print(e)
            return jsonify({"error": "Email not found"}), 404
    else:
        return render_template("login.html")

## other user's profile
@app.route('/api/otherProfile', methods=["GET"])
def other_profile():
    userID = request.args.get('userID')
    print("UserID as stated:", userID)
    profileDict = getterLib.getProfile(userID)
    endRefs = getterLib.getEndRefs(userID)

    return jsonify({
            "user": {
                "name": profileDict['name'],
                "email": profileDict['email'],
                "major": profileDict['major'],
                "minor": profileDict['minor'],
                "skills": profileDict['skills'],
                "interests": profileDict['interests'],
                "tindarIndex": profileDict['tindarIndex'],
                "endorsements": profileDict['endorsements'],
                "endorsementsRemaining": endRefs['remainingEndorsements'],
                "referralsRemaining": endRefs['remainingReferrals'],
            }
        })

## personal profile
@app.route('/api/userProfile', methods=["GET"])
def profile():
    print("inside of profile")
    userID = session['userID']            
    profileDict = getterLib.getProfile(userID)
    endRefs = getterLib.getEndRefs(userID)
    print("\n\nRetrieved Profile:\n")
    print(profileDict)
   
    return jsonify({
            "user": {
                "name": profileDict['name'],
                "email": profileDict['email'],
                "major": profileDict['major'],
                "minor": profileDict['minor'],
                "skills": profileDict['skills'],
                "interests": profileDict['interests'],
                "tindarIndex": profileDict['tindarIndex'],
                "endorsements": profileDict['endorsements'],
                "endorsementsRemaining": endRefs['remainingEndorsements'],
                "referralsRemaining": endRefs['remainingReferrals']
            }
        })



## recruiting
@app.route('/api/recruiting', methods=["GET"])
def recruiting():
    
    print("\n\nRedirected to Recruiting.\n\n")
    print("\n\nession: \n", session)    
    # Log all the cookies sent with the request
    print("\nCookies sent with the request:\n", request.cookies)
    
    if session['userID']:
        userID = session['userID']
        print("\n\n\nhere's the deck", session["deck"])
        return jsonify(session['deck'])
        # return render_template("recruiting.html", deck=session["deck"])
    else:
        return jsonify({"error": "User not logged in"}), 402

## recruiting
@app.route('/api/leaderboard', methods=["GET"])
def leaderboard():
    leaderboardDict = getterLib.getLeaderboard()
    profilesDict = {}
    i = 1
    for leaderID in leaderboardDict:
        leader = getterLib.getProfile(leaderID)
        profilesDict[i] = leader
        i+=1

    return jsonify(profilesDict)

## connections
@app.route('/api/connections', methods=["GET"])
def connections():    
    userID = session['userID']
    connectionsDict = getterLib.getConnections(userID)
    print(connectionsDict)
    print("\n\nConnections Dict: ", connectionsDict)

    swipeMatchProfiles = {}
    refMatchProfiles = {}
    for swipeUserID in connectionsDict['swipingMatches']:
        swipeMatchProfiles[swipeUserID] = getterLib.getProfile(swipeUserID)
    for refUserID in connectionsDict['referrals']:
        refMatchProfiles[refUserID] = getterLib.getProfile(refUserID)
    ## return full profiles of connections
    connectionProfiles = {
        'selfID':userID,
        'swipeMatches':swipeMatchProfiles,
        'refMatches':refMatchProfiles
        }
    
    return jsonify(connectionProfiles)

@app.route('/messaging', methods=["GET", "POST"])
def messaging():
    self_userID = session['userID']
    email = "a.26@dartmouth.edu"
    if request.method == "POST":
        provided_message = request.form.get("message")
        messagingLib.sendMessage(session["email"], email, provided_message)

    mTupleList = messagingLib.retrieveMessages(self_userID, email)
    return render_template("messaging.html", email=email, mTupleList=mTupleList)

if __name__ == '__main__':
    app.run()