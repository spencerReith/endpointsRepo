import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import sqlite3
import csv
from src.libraries import algLib
from src.libraries import resumeLib
from src.libraries import getterLib
from src.classes.applicant import Applicant
from src.classes.resume import Resume

db = 'main.db'




def createUser(email, classYear, sex, prefSex):
    userID = assignUserID(resumeLib.parseName(email))
    newApplicant = Applicant(userID, email, classYear, sex, prefSex)
    algLib.addApplicantToDB(db, newApplicant)
    return userID

def createProfile(userID, major, minor, skills, interests, blurbEntries):
    newResume = Resume(userID, major, minor, skills, interests, blurbEntries)
    resumeLib.addResumeToDB(db, newResume)

def assignUserID(name):
    filePath = 'textFiles/userIDs.csv'
    with open(filePath, 'r', newline='') as file:
        reader = list(csv.reader(file))
        last_row = []
        if reader:
            last_row = reader[-1]
            mostRecentID = int(last_row[0])
            nextID = mostRecentID + 1
        else:
            return False
    with open(filePath, 'a') as file:
        file.write('\n' + str(nextID) + ',' + name)
    return nextID

def makeReport(userID, reportedEmail, message):
    filePath = '../../textFiles/reports.csv'
    with open(filePath, 'a', newline='') as file:
        writer = csv.writer(file)
        user_email = getterLib.getProfile(userID)['email']
        writer.writerow([user_email, reportedEmail, message])




# def checkBannedList
# def checkNameConsistency