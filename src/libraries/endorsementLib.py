# 'endorsementLib.py' - Library for endorsement related functions

## CREATE ENDORSEMENT TABLE
## a_userID SENDS the endorsement
## b_userID RECIEVES the endorsement
import psycopg2
import os
import sys
from sqlalchemy import text

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import sqlite3
from libraries import cencorshipLib
from libraries import getterLib


def createEndorsementsTable():
    from app import engin
    
    with engin.connect() as connection:
        query = text('''
        CREATE TABLE IF NOT EXISTS endorsements_table (
            a_userID INTEGER,
            b_userID INTEGER,
            message TEXT
        );
        ''')
        connection.execute(query)

def getUserIDFromEmail(given_email):
    from app import engin
    
    with engin.connect() as connection:
        query = text('SELECT "userID" FROM applicant_pool WHERE LOWER("email") = :email')
        result = connection.execute(query, {'email': given_email}).fetchone()

    if result is None:
        return False
    else:
        return result[0]

def getNameFromUserID(userID):
    from app import engin
    
    with engin.connect() as connection:
        query = text('SELECT "name" FROM applicant_pool WHERE "userID" = :userID')
        result = connection.execute(query, {'userID': userID}).fetchone()

    if result is None:
        return False
    else:
        return result[0]

def onBlacklist(list_manager, blacklistee):
    from app import engin

    weight = 9  # code for blacklist
    
    with engin.connect() as connection:
        query = text('''
        SELECT * FROM interactions_table
        WHERE "a_userID" = :list_manager AND "b_userID" = :blacklistee AND "weight" = :weight
        ''')
        result = connection.execute(query, {
            'list_manager': list_manager,
            'blacklistee': blacklistee,
            'weight': weight
        }).fetchone()
    
    return result is not None

def addEndorsementToDB(a_userID, b_userID, message):
    from app import engin
    
    print('attempting add')
    print("a_userID, b_userID", a_userID, b_userID)
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            INSERT INTO endorsements_table ("a_userID", "b_userID", "message")
            VALUES (:a_userID, :b_userID, :message);
            ''')
            connection.execute(query, {
                'a_userID': a_userID,
                'b_userID': b_userID,
                'message': message
            })
            transaction.commit()  # Commit the transaction
        except:
            transaction.rollback()  # Rollback in case of error
            raise
    print('succ conc')

def attemptEndorsement(a_userID, b_email, message):
    print('a, b, msg: (in aE)', a_userID, b_email, message)
    if cencorshipLib.contains_prof(message):
        print("MESSAGE CENSORED: ", message)
        return False
    b_userID = getUserIDFromEmail(b_email.lower())
    if b_userID == False:
        return False
    if onBlacklist(a_userID, b_userID):
        print('obl')
        return False
    if onBlacklist(b_userID, a_userID):
        print('obl3')
        return False
    print('cic')
    addEndorsementToDB(a_userID, b_userID, message)
    decreaseEndorsementsRemaining(a_userID)
    print("end")
    return True

def decreaseEndorsementsRemaining(userID):
    from app import engin
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            UPDATE resume_table 
            SET "endorsements_remaining" = "endorsements_remaining" - 1 
            WHERE "userID" = :userID
            ''')
            connection.execute(query, {'userID': userID})
            transaction.commit()
        except:
            transaction.rollback()
            raise


def fetchEndorsements(userID):
    from app import engin
    
    with engin.connect() as connection:
        query = text('''
        SELECT "a_userID", "message" 
        FROM endorsements_table 
        WHERE "b_userID" = :userID
        ''')
        result = connection.execute(query, {'userID': userID}).fetchall()
    
    if not result:
        return []
    
    newRes = [(getNameFromUserID(row[0]), row[1]) for row in result]
    return newRes

# def fetchEndorsements(userID):
#     from app import DATABASE_URL
    
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     query = '''
#     SELECT "a_userID", "message" FROM endorsements_table WHERE "b_userID" = %s;
#     '''
#     cursor.execute(query, (userID,))
#     result = cursor.fetchall()
#     if result == None:
#         conn.close()
#         return 'None'
#     else:
#         conn.close()
#         ## returns a list of tuples representing who the endorsement is from, and what their message says
#         newRes = []
#         for tuple in result:
#             newRes.append((getNameFromUserID(tuple[0]), tuple[1]))
#         return newRes
