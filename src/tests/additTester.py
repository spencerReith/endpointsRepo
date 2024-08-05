"""
Test file for additionaly getter, setter, and extraneous functions that have not been tested in other files
"""
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import sqlite3
import libraries.setterLib as setterLib
import libraries.getterLib as getterLib
import libraries.algLib as algLib
import libraries.analyticsLib as analyticsLib
import libraries.referralLib as referralLib
import libraries.endorsementLib as endorsementLib
import libraries.cencorshipLib as cencorshipLib
import libraries.resumeLib as resumeLib
from random import randint

## empty existing tables
myDB = '../../main.db'

conn = sqlite3.connect(myDB)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS applicant_pool;')
cursor.execute('DROP TABLE IF EXISTS interactions_table;')
cursor.execute('DROP TABLE IF EXISTS statistics;')
cursor.execute('DROP TABLE IF EXISTS referrals_table;')
cursor.execute('DROP TABLE IF EXISTS endorsements_table;')
cursor.execute('DROP TABLE IF EXISTS resume_table;')
conn.commit()
conn.close()

algLib.createApplicantTable(myDB)
algLib.createEdgeTable(myDB)
analyticsLib.createStatisticsTable(myDB)
referralLib.createReferralsTable(myDB)
endorsementLib.createEndorsementsTable(myDB)
resumeLib.createResumeTable(myDB)

####################################################
#### Load Database #################################
####################################################


for i in range(30):
    email = f"fakeperson{i}.{i}.26@dartmouth.edu"
    if randint(0, 1) == 0:
        sex = 'm'
        prefSex = 'f'
    else:
        sex = 'f'
        prefSex = 'm'
    major = f"Finance{i}"
    minor = f"Econ{i}"
    skills = ["skill1", "skill2", "skill3"]
    interests = ["interest1", "interest2", "interest3"]
    blurbList = ["N", "N", "N", "V", "V", "V", "A", "A", "A"]
    userID = setterLib.createUser(email, 2026, sex, prefSex)
    setterLib.createProfile(userID, major, minor, skills, interests, blurbList)
    tindarIndex = analyticsLib.calcTindarIndex(randint(2, 4), randint(0, 100))
    analyticsLib.addTindarIndexToDB(userID, tindarIndex)
    print(f"Creating user {i}")
    ############
    ### Assuming they are not the first or second user, make endorsement of previous 2 people
    ############
    if i >= 2:
        endorsementLib.attemptEndorsement(userID, f"fakeperson{i-1}.{i-1}.26@dartmouth.edu", f"{i} here endorsing {i-1}")
        endorsementLib.attemptEndorsement(userID, f"fakeperson{i-2}.{i-2}.26@dartmouth.edu", f"{i} here endorsing {i-2}")

    



## create user with proper parameters
email = "john.b.hancock.iii.26@dartmouth.edu"
sex = 'm'
prefSex = 'f'
major = "Economics"
minor = "Finance"
skills = ["fishing", "hunting", "coding"]
interests = ["this", "that", "the other"]
blurbList = ["N", "N", "N", "V", "V", "V", "A", "A", "A"]

## test if user is banned
if cencorshipLib.is_banned(email):
    print("user is banned.")
print("user is not banned")
bannedEmail = "mr.doback.26@dartmouth.edu"
if cencorshipLib.is_banned(bannedEmail):
    print("user is banned: ", bannedEmail)
## test for profanity in parameters
for thisVar in [major, minor, skills, interests, blurbList]:
    if cencorshipLib.contains_prof(thisVar):
        print("profanity error. Please try again")
print("no profanity")

## since user passed checks create new user and profile
newUserID = setterLib.createUser("john.b.hancock.iii.26@dartmouth.edu", 2026, 'm', 'f')
setterLib.createProfile(newUserID, major, minor, skills, interests, blurbList)
tindarIndex = analyticsLib.calcTindarIndex(randint(2, 4), randint(0, 100))
analyticsLib.addTindarIndexToDB(newUserID, tindarIndex)
print("\n\nJohn Hancock's Profile: \n", getterLib.getProfile(newUserID))

## get deck
deck = getterLib.getDeck(newUserID)
print("\n\ndeck: \n", deck)
for id in deck:
    profile = getterLib.getProfile(id)
    decision = randint(0, 1)
    algLib.addInteractionToDB(newUserID, id, decision)

## get leaderboard
leaderboard = getterLib.getLeaderboard()
for leaderID in leaderboard:
    print("\n\nleaderID: ", leaderID)
    profile = getterLib.getProfile(leaderID)
    print("\nleader's profile: \n", profile)

setterLib.makeReport(newUserID, "john.adams.26@dartmouth.edu", "really frustrating person should be kicked off the app")
setterLib.makeReport(newUserID, "john.adams.26@dartmouth.edu", "awful")
setterLib.makeReport(newUserID, "john.adams.26@dartmouth.edu", "violated community standards")
setterLib.makeReport(newUserID, "john.adams.26@dartmouth.edu", "should be investigated for community standards violations")



shortSkills = ["as", "as", "asd"]
shortInterests = ["ad", "asdad", "as"]
longSkills = ["sdfgasdfasdfasdfasdfsdfasdf", "skill2", "skdffsdfdsfsdill3"]
longInterests = ["skill1", "skidfasdfasdfsdfll2", "skilldsfsdfsfdfssdffsddfsfd3"]
print("\n\nIs this over the char limit?", getterLib.overCharLimit('skills', shortSkills))
print("Is this over the char limit?", getterLib.overCharLimit('skills', shortInterests))
print("Is this over the char limit?", getterLib.overCharLimit('skills', longInterests))
print("Is this over the char limit?", getterLib.overCharLimit('skills', longSkills))