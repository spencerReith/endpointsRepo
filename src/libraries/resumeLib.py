# Library for resume related functions
import psycopg2
import os
import sys
import re

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)



import sqlite3
from classes.resume import Resume
from datetime import date

# from app import db
# db = 'main.db'

def createResumeTable(myDB):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS resume_table (
        userID INTEGER PRIMARY KEY,
        major TEXT,
        minor TEXT,
        height TEXT,
        skills TEXT,
        interests TEXT,
        referrals_remaining INT,
        endorsements_remaining INT,
        swipes_remaining INT,
        latest_swipes_update DATE,
        photoID TEXT
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def addResumeToDB(myDB, res):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    INSERT INTO resume_table (userID, major, minor, height, skills, interests, referrals_remaining, endorsements_remaining, swipes_remaining, latest_swipes_update, photoID)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''
    cursor.execute(query, (res.getUserID(), res.getMajor(), res.getMinor(), res.getHeight(), res.getSkillsString(), res.getInterestsString(), res.getReferrals_Remaining(), res.getEndorsements_Remaining(), res.getSwipes_Remaining(), res.getLatest_Swipes_Update(), res.getPhotoID()))
    conn.commit()
    conn.close()

def parseName(email):
    modified_email = re.sub(r'\.(25|26|27|28)@dartmouth\.edu$', '', email)
    nameArray = modified_email.split('.')
    fullName = ""
    for n in nameArray:
        if len(n) == 1:
            fullName = fullName + n.upper() + '. '
            continue
        firstLetter = n[0].upper()
        name = firstLetter + n[1:]
        fullName = fullName + name + ' '
    fullName = fullName[:-1]
    return fullName

def parseClassYear(email):
    startOfEmail = email.strip("@dartmouth.edu")
    year = startOfEmail[-2:]
    return year

def fetchLatestSwipesUpdate(userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT latest_swipes_update
    FROM resume_table
    WHERE userID = %s
    '''
    cursor.execute(query, (userID,))
    results = cursor.fetchall()
    for row in results:
        latest = row
    latestUpdate = latest[0]
    conn.close()
    return latestUpdate

def resetSwipes(userID, currentDate):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    UPDATE resume_table SET swipes_remaining = 40, latest_swipes_update = %s WHERE userID = %s
    '''
    cursor.execute(query, (currentDate, userID))
    conn.commit()
    conn.close()

def decrementSwipes(userID):
    from app import DATABASE_URL
        
    curSwipes = fetchSwipesRemaining(userID)
    newSwipes = curSwipes - 1
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    UPDATE resume_table SET swipes_remaining = %s WHERE userID = %s
    '''
    cursor.execute(query, (newSwipes, userID))
    conn.commit()
    conn.close()


def fetchSwipesRemaining(userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT swipes_remaining
    FROM resume_table
    WHERE userID = %s
    '''
    cursor.execute(query, (userID,))
    results = cursor.fetchall()
    for row in results:
        remSwipes = row
    swipesRemaining = remSwipes[0]
    conn.close()
    return swipesRemaining

def fetchEndorsementsRemaining(userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT endorsements_remaining
    FROM resume_table
    WHERE userID = %s
    '''
    cursor.execute(query, (userID,))
    results = cursor.fetchall()
    for row in results:
        remEnds = row
    endorsementsRemaining = remEnds[0]
    conn.close()
    return endorsementsRemaining

def fetchReferralsRemaining(userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT referrals_remaining
    FROM resume_table
    WHERE userID = %s
    '''
    cursor.execute(query, (userID,))
    results = cursor.fetchall()
    for row in results:
        remRefs = row
    referralsRemaining = remRefs[0]
    conn.close()
    return referralsRemaining


                             
def checkForSwipesUpdate(myDB, userID):
    currentDate = date.today()
    latestUpdate = fetchLatestSwipesUpdate(myDB, userID)
    if currentDate > latestUpdate:
        resetSwipes(myDB, userID, currentDate)
