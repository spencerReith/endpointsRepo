# Library for resume related functions
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)



import sqlite3
from classes.resume import Resume
from datetime import date

def createResumeTable(myDB):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS resume_table (
        userID INTEGER PRIMARY KEY,
        major TEXT,
        minor TEXT,
        skills TEXT,
        interests TEXT,
        referrals_remaining INT,
        endorsements_remaining INT,
        swipes_remaining INT,
        latest_swipes_update DATE
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def addResumeToDB(myDB, res):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    INSERT INTO resume_table (userID, major, minor, skills, interests, referrals_remaining, endorsements_remaining, swipes_remaining, latest_swipes_update)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (res.getUserID(), res.getMajor(), res.getMinor(), res.getSkillsString(), res.getInterestsString(), res.getReferrals_Remaining(), res.getEndorsements_Remaining(), res.getSwipes_Remaining(), res.getLatest_Swipes_Update()))
    conn.commit()
    conn.close()

def parseName(email):
    nameArray = email.replace('.26@dartmouth.edu', '').split('.')
    fullName = ""
    for n in nameArray:
        firstLetter = n[0].upper()
        name = firstLetter + n[1:]
        fullName = fullName + name + ' '
    fullName = fullName[:-1]
    return fullName

def parseClassYear(email):
    startOfEmail = email.strip("@dartmouth.edu")
    year = startOfEmail[:-2]
    return year

def fetchLatestSwipesUpdate(myDB, userID):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT latest_swipes_update
    FROM resume_table
    WHERE userID = ?
    '''
    cursor.execute(query, (userID,))
    results = cursor.fetchall()
    for row in results:
        latest = row
    latestUpdate = latest[0]
    conn.close()
    return latestUpdate

def resetSwipes(myDB, userID, currentDate):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    UPDATE resume_table SET swipes_remaining = 40, latest_swipes_update = ? WHERE userID = ?
    '''
    cursor.execute(query, (currentDate, userID))
    conn.commit()
    conn.close()


def fetchSwipesRemaining(myDB, userID):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT swipes_remaining
    FROM resume_table
    WHERE userID = ?
    '''
    cursor.execute(query, (userID,))
    results = cursor.fetchall()
    for row in results:
        remSwipes = row
    swipesRemaining = remSwipes[0]
    conn.close()
    return swipesRemaining

                             
def checkForSwipesUpdate(myDB, userID):
    currentDate = date.today()
    latestUpdate = fetchLatestSwipesUpdate(myDB, userID)
    if currentDate > latestUpdate:
        resetSwipes(myDB, userID, currentDate)
