import os
import matplotlib as plt
import io
import base64
import sys
import json
import roman
from datetime import date


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
import src.libraries.algLib as algLib
import src.libraries.resumeLib as resumeLib


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
        height = data.get('heightTotal')
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
        setterLib.createProfile(userID, major, minor, height, skills, interests)
        analyticsLib.addTindarIndexToDB(userID, tindarIndex)
        
        session['userID'] = userID
        session['email'] = email
        newDeck = getterLib.getDeck(userID, 40)
        session['deck'] = newDeck

        return jsonify({'message': 'Registration successful'})
    else:
        return jsonify({'error': 'Registration error'}), 400

@app.route('/api/login', methods=["POST"])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        if authenticationLib.passwordIsAccurate(email, password):
            userID = int(authenticationLib.pullUserID(email))
            session['userID'] = userID
            session['email'] = email
            print("1. heres the session:\n", session)
            #############
            ## Get deck only if one hasn't been pulled that day
            #############
            latest_update = resumeLib.fetchLatestSwipesUpdate(userID)
            date_today = date.today()

            if latest_update != date_today:
                resumeLib.resetSwipes(userID, date_today)
                newDeck = getterLib.getDeck(userID, 40)
                session['deck'] = newDeck
            elif resumeLib.fetchSwipesRemaining(userID) <= 0:
                session['deck'] = []
            else:
                remSwipes = resumeLib.fetchSwipesRemaining()
                newDeck = getterLib.getDeck(userID, remSwipes)
                session['deck'] = newDeck

            print("2. heres the session:\n", session)
            #############
            #############

            # Serialize the session data to a JSON string
            session_data = json.dumps(dict(session))
    
            # Calculate the size of the session data in bytes
            session_size = len(session_data.encode('utf-8'))
                
            print("\n3. session_size:", session_size)
            # Return a JSON response with the redirect URL
            # This should show all the session variables
            return jsonify({"redirect": "/recruiting"})
        else:
            return jsonify({"error": "Incorrect password"}), 401
    except Exception as e:
        print(e)
        return jsonify({"error": "Email not found"}), 404

## other user's profile
@app.route('/api/othprf', methods=["POST"])
def other_profile():
    data = request.get_json()
    userID = data.get('userID')

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
    print("\n\n\nHere is session:", session)
    print("inside of profile")
    userID = session['userID']            
    profileDict = getterLib.getProfile(userID)
    endRefs = getterLib.getEndRefs(userID)
    print("\n\nRetrieved Profile:\n")
    print(profileDict)
    histoCode = analyticsLib.getHistogram(userID)
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
                "histogramHTML": histoCode
            }
        })



## recruiting
@app.route('/api/recruiting', methods=['GET', 'POST'])
def recruiting():
    if request.method == 'POST':
        data = request.get_json()
        direction = data.get('choice')
        if direction == 'right':
            choice_code = 1
        else:
            choice_code = 0
        
        otherUserID = data.get('userID')
        oldDeck = session['deck']
        del oldDeck[otherUserID]
        session['deck'] = oldDeck

        userID = session['userID']
        algLib.addInteractionToDB(userID, otherUserID, choice_code)
        resumeLib.decrementSwipes(userID)

    if session['userID']:
        return jsonify(session['deck'])
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

    print(profilesDict)
    return jsonify(profilesDict)

## connections
@app.route('/api/connections', methods=["GET"])
def connections():    
    userID = session['userID']
    connectionsDict = getterLib.getConnections(userID)
    print(connectionsDict)
    print("\n\nConnections Dict: ", connectionsDict)

    swipeMatchProfiles = {}
    refs = {}
    for swipeUserID in connectionsDict['swipingMatches']:
        swipeMatchProfiles[swipeUserID] = getterLib.getProfile(swipeUserID)
    for ref in connectionsDict['referrals']:
        refMatchUserID = ref['ref_connect']
        refFromUserName = endorsementLib.getNameFromUserID(ref['from_user'])
        refs[refFromUserName] = getterLib.getProfile(refMatchUserID)
    ## return full profiles of connections
    print("html string from analytics lib: ", analyticsLib.getHistogram(userID))
    connectionProfiles = {
        'selfID':userID,
        'swipeMatches':swipeMatchProfiles,
        'refs': refs
        }
    
    print("\nconnections Profile: \n\n", connectionProfiles)
    return jsonify(connectionProfiles)

@app.route('/api/messaging', methods=['POST'])
def messaging():
    data = request.get_json()
    print("data: ", data)

    self_userID = data.get('selfUserID')
    b_userID = int(data.get('bUserID'))
    print("b_userID here:", b_userID)
    self_name = endorsementLib.getNameFromUserID(self_userID)
    b_name = endorsementLib.getNameFromUserID(b_userID)
    print("bName:", b_name)

    messages = messagingLib.retrieveMessages(self_userID, b_userID)
    newMessagesList = []
    ## get messages into new object containing roman numeral deliniating which message it is
    try:
        if len(messages) == 0:
            return jsonify([])
        for i in range(len(messages)):
            numeral = roman.toRoman(i+1)
            if messages[i][0] == str(self_userID):
                sender_name = self_name
            else:
                sender_name = b_name
            newTuple = (numeral, sender_name, messages[i][1])
            newMessagesList.append(newTuple)
        
        return jsonify(newMessagesList)
    except:
        return jsonify({'error' : 'Error collecting messages'})

@app.route('/api/sendMessage', methods=['POST'])
def sendMessage():
    self_userID = session['userID']
    data = request.get_json()
    b_userID = data.get('bUserID')
    msg = data.get('msg')
    print(msg)
    try:
        result = messagingLib.sendMessage(self_userID, b_userID, msg)
        print("result: ", result)
        if result:
            return jsonify({'result' : 'successful'})
        else:
            return jsonify({'error' : 'Message failed. Ensure your message has no profanity in it.'})
    except:
        return jsonify({'error' : 'Message failed. Ensure your message has no profanity in it.'})


@app.route('/api/endorse', methods=['POST'])
def endorse():
    print("entering the endorsement")
    data = request.get_json()
    print("\nheres the data: ", data)
    to_email = data.get("email")
    if to_email == session['email']:
        print('\nattempted self endorsement\n\n')
        return jsonify({'error': 'You cannot endorse yourself.'})
    msg = data.get("msg")
    a_email = session["email"]
    a_userID = endorsementLib.getUserIDFromEmail(a_email)
    ## if the user is out of swipes, don't let the endorsement go through
    endsRemaining = resumeLib.fetchEndorsementsRemaining(a_userID)
    print(endsRemaining)
    if endsRemaining <= 0:
            return jsonify({'error': 'No more endorsements remaining.'}), 400
    else:
        try:
            if endorsementLib.attemptEndorsement(a_userID, to_email, msg) == True:
                return jsonify({'result': 'sucess'}), 200
            else:
                return jsonify({'error': 'Error. these users have already matched, or you included profanity in your endorsement.'})
        except:
            return jsonify({'error': 'Are you sure you entered the email correctly?'})

@app.route('/api/refer', methods=['POST'])
def refer():
    data = request.get_json()
    self_ID = endorsementLib.getUserIDFromEmail(session["email"])
    email1 = data.get("email1")
    email2 = data.get("email2")

    if email1 == session['email'] or email2 == session['email']:
        print('\nattempted self referrel\n\n')
        return jsonify({'error': 'You cannot refer yourself.'})

    remRefs = resumeLib.fetchReferralsRemaining(self_ID)
    if remRefs <= 0:
        return jsonify({'error': 'Error: You are out of endorsements'})
    
    try:
        result = referralLib.attemptReferral(self_ID, email1, email2)
        if result == True:
            return jsonify({'result': 'Success! These users have been referred'})
        else:
            return jsonify({'error': 'these users have already been referred or are not compatible for a referral'})
    except:
        return jsonify({'error': 'Error: Ensure both emails are valid Dartmouth emails'})

@app.route('/api/blacklist', methods=['POST'])
def blacklist():
    print("inside of blacklist")
    data = request.get_json()
    self_ID = session["userID"]
    email = data.get("email")
    b_userID = endorsementLib.getUserIDFromEmail(email)

    if b_userID == False:
        return jsonify({'error' : 'User does not exist'})

    if email == session['email']:
        print('\nattempted self blacklist\n\n')
        return jsonify({'error': 'You cannot blacklist yourself.'})
    
    ## insert interaction with blacklist code
    try:
        algLib.addInteractionToDB(self_ID, b_userID, 9)
        return jsonify({'result' : 'successful blacklist'})
    except:
        return jsonify({'error': 'Error in blacklisting.'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))