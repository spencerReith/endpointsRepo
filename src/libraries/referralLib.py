## REFERRAL LIB
## defines important things for referals
import psycopg2
import os
import sys
from sqlalchemy import text

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from classes.applicant import Applicant
import libraries.algLib as algLib
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx
import scipy as sp

import src.libraries.endorsementLib as endorsementLib



########################################################
### FUNCTIONS RELATING TO REFERRALS ####################
########################################################

## Run createReferralsTable
def createReferralsTable():
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS referrals_table (
        self_ID INTEGER,
        a_userID INTEGER,
        b_userID INTEGER,
        UNIQUE(a_userID, b_userID)
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()


# def getApplicantFromDB(userID):
#     from app import DATABASE_URL
    
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     query = '''
#     SELECT * FROM applicant_pool WHERE "userID" = %s;
#     '''
#     row = cursor.execute(query, (userID,)).fetchone()
#     a = Applicant(row[1], row[3], row[4], row[5], row[6])
#     conn.commit()
#     conn.close()
#     ## return tindarIndex
#     return a
def getApplicantFromDB(userID):
    from app import engin
    print('userID in getAppFromDB', userID)

    with engin.connect() as connection:
        query = text('SELECT * FROM applicant_pool WHERE "userID" = :userID')
        row = connection.execute(query, {'userID': userID}).fetchone()
    
    if row:
        print(row)
        print('row[1]', row[1])
        print('row[6]', row[6])
        a = Applicant(row[1], row[3], row[5], row[6])
        print(a)
        return a
    print('for userID about to return non', userID)
    return None


def sexBasedCompatabilityCheck(a_userID, b_userID):
    print("entered sex based compatability check")
    print("a_userID = ", a_userID)
    # print("b_userID = ", b_userID)
    applicantA = getApplicantFromDB(a_userID)
    print('amid,', b_userID)
    applicantB = getApplicantFromDB(b_userID)
    print('post get App')
    print("appA: ", applicantA)
    print("appB: ", applicantB)
    a_sex = applicantA.getSex()
    a_pref = applicantA.getPrefSex()
    b_sex = applicantB.getSex()
    b_pref = applicantB.getPrefSex()

    print("preferences: ", a_sex, a_pref, b_sex, b_pref)

    if (a_pref == b_sex) or (a_pref == 'b'):
        if (a_sex == b_pref) or (b_pref == 'b'):
            return True
    return False

def getEdgeWeight(a, b):
    from app import engin
    
    with engin.connect() as connection:
        query = text('''
        SELECT * FROM interactions_table WHERE "a_userID" = :a AND "b_userID" = :b
        ''')
        result = connection.execute(query, {'a': a, 'b': b}).fetchone()

    if result is None:
        return 'None'
    else:
        edge_weight = result[2]
        return edge_weight

def addReferralToDB(self_ID, a, b):
    from app import engin
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            INSERT INTO referrals_table ("self_ID", "a_userID", "b_userID")
            VALUES (:self_ID, :a, :b);
            ''')
            connection.execute(query, {
                'self_ID': self_ID,
                'a': a,
                'b': b
            })
            transaction.commit()
        except:
            transaction.rollback()
            raise

def getUserID(email):
    from app import engin

    with engin.connect() as connection:
        query = text('SELECT "userID" FROM applicant_pool WHERE "email" = :email')
        result = connection.execute(query, {'email': email}).fetchone()

    return result[0] if result else None

def attemptReferral(self_ID, a_email, b_email):
    print("\nPrinting self_ID:", self_ID)
    print("\nPrinting a_email", a_email)
    print("\nPrinting a_email.lower()", a_email.lower())
    print("\nPrinting b_email:", b_email)
    a = endorsementLib.getUserIDFromEmail(a_email)
    b = endorsementLib.getUserIDFromEmail(b_email)
    print("a_userID: ", a)
    print("b_userID: ", b)
    if sexBasedCompatabilityCheck(a, b) == False:
        print("COMPATABILITY FAILURE")
        return False
    else:
        print("pre-edge weight retrieval")
        ab_edgeWeight = getEdgeWeight(a, b)
        ba_edgeWeight = getEdgeWeight(b, a)
        print("post edgeweight", ab_edgeWeight, ba_edgeWeight)
        if ab_edgeWeight == ba_edgeWeight == 1:
            print("TYPE-1 FAILURE")
            return False
        if ab_edgeWeight == 9 or ba_edgeWeight == 9:
            print("TYPE-9 FAILURE")
            return False
        if ab_edgeWeight == 14 or ba_edgeWeight == 14:
            print("TYPE-14 FAILURE")
            return False
            # return("TYPE-14 FAILURE")
        if ab_edgeWeight == 0 or ba_edgeWeight == 0:
            print("TYPE-0 FAILURE")
            return False
            # return("TYPE-0 FAILURE")
        if ab_edgeWeight == 1 and ba_edgeWeight == 'None':
            print("1-nons uc")
            algLib.addInteractionToDB(b, a, 14)
            addReferralToDB(self_ID, a, b)
            decreaseReferralsRemaining(self_ID)
            return True
            # return("1-None Success")
        if ab_edgeWeight == 'None' and ba_edgeWeight == 1:
            print('ere')
            algLib.addInteractionToDB(a, b, 14)
            addReferralToDB(self_ID, a,b)
            decreaseReferralsRemaining(self_ID)
            return True
            # return("None-1 Success")
        if ab_edgeWeight == ba_edgeWeight == 'None':
            print('there')
            algLib.addInteractionToDB(a, b, 14)
            algLib.addInteractionToDB(b, a, 14)
            addReferralToDB(self_ID, a,b)
            decreaseReferralsRemaining(self_ID)
            return True
            # return("None-None Success")

    
def decreaseReferralsRemaining(userID):
    from app import engin
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            UPDATE resume_table 
            SET "referrals_remaining" = "referrals_remaining" - 1 
            WHERE "userID" = :userID
            ''')
            connection.execute(query, {'userID': userID})
            transaction.commit()
        except:
            transaction.rollback()
            raise

def getReferralInfo(referredUser):
    from app import engin
    
    refsList = []
    with engin.connect() as connection:
        query = text('''
        SELECT * FROM referrals_table 
        WHERE "a_userID" = :referredUser OR "b_userID" = :referredUser
        ''')
        rows = connection.execute(query, {'referredUser': referredUser}).fetchall()
    
    for row in rows:
        from_userID = row[0]
        a_userID = row[1]
        b_userID = row[2]
        refsList.append((from_userID, a_userID, b_userID))

    return(refsList)

