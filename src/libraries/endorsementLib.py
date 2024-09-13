# 'endorsementLib.py' - Library for endorsement related functions

## CREATE ENDORSEMENT TABLE
## a_userID SENDS the endorsement
## b_userID RECIEVES the endorsement
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import sqlite3
from libraries import cencorshipLib
from libraries import getterLib


db = 'main.db'


def createEndorsementsTable(myDB):
    conn = sqlite3.connect(myDB)
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

def getUserIDFromEmail(email):
    myDB = db
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT userID FROM applicant_pool WHERE email = ?;
    '''
    result = cursor.execute(query, (email,)).fetchone()
    conn.commit()
    if result == None:
        conn.close()
        return False
    else:
        userID = result[0]
        conn.close()
    return userID

def onBlacklist(myDB, list_manager, blacklistee):
    weight = 9 ## code for blacklist
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM interactions_table WHERE a_userID=? AND b_userID=? AND weight=?;
    '''
    result = cursor.execute(query, (list_manager, blacklistee, weight)).fetchone()
    if result == None:
        conn.close()
        return False
    else:
        conn.close()
        return True

def addEndorsementToDB(myDB, a_userID, b_userID, message):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    INSERT INTO endorsements_table (a_userID, b_userID, message)
    VALUES (?, ?, ?);
    '''
    cursor.execute(query, (a_userID, b_userID, message))
    conn.commit()
    conn.close()

def attemptEndorsement(a_userID, b_email, message):
    if cencorshipLib.contains_prof(message):
        print("MESSAGE CENSORED: ", message)
        return False
    b_userID = getUserIDFromEmail(b_email.lower())
    if onBlacklist(db, a_userID, b_userID):
        return False
    if onBlacklist(db, b_userID, a_userID):
        return False
    addEndorsementToDB(db, a_userID, b_userID, message)
    decreaseEndorsementsRemaining(db, a_userID)
    return True

def decreaseEndorsementsRemaining(myDB, userID):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    UPDATE resume_table SET endorsements_remaining = endorsements_remaining - 1 WHERE userID = ?
    '''
    cursor.execute(query, (userID,))
    conn.commit()
    conn.close()

def fetchEndorsements(userID):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT a_userID, message FROM endorsements_table WHERE b_userID = ?;
    '''
    result = cursor.execute(query, (userID,)).fetchall()
    if result == None:
        conn.close()
        return 'None'
    else:
        conn.close()
        ## returns a list of tuples representing who the endorsement is from, and what their message says
        return result
