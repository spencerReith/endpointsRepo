# Library for resume related functions
import psycopg2
import os
import sys
import re
from sqlalchemy import text

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)



import sqlite3
from classes.resume import Resume
from datetime import date


def createResumeTable():
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

def addResumeToDB(res):
    from app import engin
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            INSERT INTO resume_table ("userID", "major", "minor", "height", "skills", "interests", "referrals_remaining", "endorsements_remaining", "swipes_remaining", "latest_swipes_update", "photoID")
            VALUES (:userID, :major, :minor, :height, :skills, :interests, :referrals_remaining, :endorsements_remaining, :swipes_remaining, :latest_swipes_update, :photoID);
            ''')
            connection.execute(query, {
                'userID': res.getUserID(),
                'major': res.getMajor(),
                'minor': res.getMinor(),
                'height': res.getHeight(),
                'skills': res.getSkillsString(),
                'interests': res.getInterestsString(),
                'referrals_remaining': res.getReferrals_Remaining(),
                'endorsements_remaining': res.getEndorsements_Remaining(),
                'swipes_remaining': res.getSwipes_Remaining(),
                'latest_swipes_update': res.getLatest_Swipes_Update(),
                'photoID': res.getPhotoID()
            })
            transaction.commit()
        except:
            transaction.rollback()
            raise

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
    print("in here")
    startOfEmail = email.strip("@dartmouth.edu")
    year = startOfEmail[-2:]
    return year

def fetchLatestSwipesUpdate(userID):
    from app import engin
    
    with engin.connect() as connection:
        query = text('''
        SELECT "latest_swipes_update"
        FROM resume_table
        WHERE "userID" = :userID
        ''')
        result = connection.execute(query, {'userID': userID}).fetchone()

    if result:
        latestUpdate = result[0]
        return latestUpdate
    return None

def resetSwipes(userID, currentDate):
    from app import engin
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            UPDATE resume_table 
            SET "swipes_remaining" = 40, "latest_swipes_update" = :currentDate 
            WHERE "userID" = :userID
            ''')
            connection.execute(query, {'currentDate': currentDate, 'userID': userID})
            transaction.commit()
        except:
            transaction.rollback()
            raise


def decrementSwipes(userID):
    from app import engin
        
    curSwipes = fetchSwipesRemaining(userID)
    newSwipes = curSwipes - 1
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            UPDATE resume_table 
            SET "swipes_remaining" = :newSwipes 
            WHERE "userID" = :userID
            ''')
            connection.execute(query, {'newSwipes': newSwipes, 'userID': userID})
            transaction.commit()
        except:
            transaction.rollback()
            raise

def fetchSwipesRemaining(userID):
    from app import engin
    
    with engin.connect() as connection:
        query = text('''
        SELECT "swipes_remaining"
        FROM resume_table
        WHERE "userID" = :userID
        ''')
        result = connection.execute(query, {'userID': userID}).fetchone()

    if result:
        swipesRemaining = result[0]
        print('success')
        return swipesRemaining
    return None

def fetchEndorsementsRemaining(userID):
    from app import engin
    
    with engin.connect() as connection:
        query = text('''
        SELECT "endorsements_remaining"
        FROM resume_table
        WHERE "userID" = :userID
        ''')
        result = connection.execute(query, {'userID': userID}).fetchone()

    if result:
        return result[0]
    return None


def fetchReferralsRemaining(userID):
    from app import engin
    
    with engin.connect() as connection:
        query = text('''
        SELECT "referrals_remaining"
        FROM resume_table
        WHERE "userID" = :userID
        ''')
        result = connection.execute(query, {'userID': userID}).fetchone()

    if result:
        return result[0]
    return None


                             
def checkForSwipesUpdate(userID):
    currentDate = date.today()
    latestUpdate = fetchLatestSwipesUpdate(userID)
    if currentDate > latestUpdate:
        resetSwipes(userID, currentDate)
