# 'endorsementLib.py' - Library for endorsement related functions

## CREATE ENDORSEMENT TABLE
## a_userID SENDS the endorsement
## b_userID RECIEVES the endorsement
import psycopg2
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import sqlite3
from libraries import cencorshipLib
from libraries import getterLib

# from app import db
# db = 'main.db'


def createEndorsementsTable(myDB):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS endorsements_table (
        a_userID INTEGER,
        b_userID INTEGER,
        message TEXT
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def getUserIDFromEmail(given_email):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT userID FROM applicant_pool WHERE LOWER(email) = ?;
    '''
    result = cursor.execute(query, (given_email,)).fetchone()
    conn.commit()
    if result == None:
        conn.close()
        return False
    else:
        userID = result[0]
        conn.close()
    return userID

def getNameFromUserID(userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT name FROM applicant_pool WHERE userID = %s;
    '''
    result = cursor.execute(query, (userID,)).fetchone()
    conn.commit()
    if result == None:
        conn.close()
        return False
    else:
        name = result[0]
        conn.close()
    return name

def onBlacklist(myDB, list_manager, blacklistee):
    from app import DATABASE_URL

    weight = 9 ## code for blacklist
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM interactions_table WHERE a_userID=%s AND b_userID=%s AND weight=%s;
    '''
    result = cursor.execute(query, (list_manager, blacklistee, weight)).fetchone()
    if result == None:
        conn.close()
        return False
    else:
        conn.close()
        return True

def addEndorsementToDB(myDB, a_userID, b_userID, message):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    INSERT INTO endorsements_table (a_userID, b_userID, message)
    VALUES (%s, %s, %s);
    '''
    cursor.execute(query, (a_userID, b_userID, message))
    conn.commit()
    conn.close()
    print('succ conc')

def attemptEndorsement(a_userID, b_email, message):
    if cencorshipLib.contains_prof(message):
        print("MESSAGE CENSORED: ", message)
        return False
    b_userID = getUserIDFromEmail(b_email.lower())
    print(b_email.lower())
    print('b_userID = ', b_userID)
    if b_userID == False:
        return False
    if onBlacklist(db, a_userID, b_userID):
        print('obl')
        return False
    if onBlacklist(db, b_userID, a_userID):
        print('obl3')
        return False
    addEndorsementToDB(db, a_userID, b_userID, message)
    decreaseEndorsementsRemaining(db, a_userID)
    return True

def decreaseEndorsementsRemaining(myDB, userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    UPDATE resume_table SET endorsements_remaining = endorsements_remaining - 1 WHERE userID = %s
    '''
    cursor.execute(query, (userID,))
    conn.commit()
    conn.close()

def fetchEndorsements(userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT a_userID, message FROM endorsements_table WHERE b_userID = %s;
    '''
    result = cursor.execute(query, (userID,)).fetchall()
    if result == None:
        conn.close()
        return 'None'
    else:
        conn.close()
        ## returns a list of tuples representing who the endorsement is from, and what their message says
        newRes = []
        for tuple in result:
            newRes.append((getNameFromUserID(tuple[0]), tuple[1]))
        return newRes
