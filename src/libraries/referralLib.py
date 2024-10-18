## REFERRAL LIB
## defines important things for referals
import psycopg2
import os
import sys

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

# from app import db
# db = 'main.db'


########################################################
### FUNCTIONS RELATING TO REFERRALS ####################
########################################################

## Run createReferralsTable
def createReferralsTable(myDB):
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


def getApplicantFromDB(myDB, userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM applicant_pool WHERE userID = %s;
    '''
    row = cursor.execute(query, (userID,)).fetchone()
    a = Applicant(row[1], row[3], row[4], row[5], row[6])
    conn.commit()
    conn.close()
    ## return tindarIndex
    return a

def sexBasedCompatabilityCheck(myDB, a_userID, b_userID):
    # print("a_userID = ", a_userID)
    # print("b_userID = ", b_userID)
    applicantA = getApplicantFromDB(myDB, a_userID)
    applicantB = getApplicantFromDB(myDB, b_userID)
    # print("appA: ", applicantA)
    # print("appB: ", applicantB)
    a_sex = applicantA.getSex()
    a_pref = applicantA.getPrefSex()
    b_sex = applicantB.getSex()
    b_pref = applicantB.getPrefSex()

    # print("preferences: ", a_sex, a_pref, b_sex, b_pref)

    if (a_pref == b_sex) or (a_pref == 'b'):
        if (a_sex == b_pref) or (b_pref == 'b'):
            return True
    return False

def getEdgeWeight(myDB, a, b):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM interactions_table WHERE a_userID = %s AND b_userID = %s;
    '''
    result = cursor.execute(query, (a, b)).fetchone()
    ## If edge does not exist, return 'DNE'
    if result == None:
        conn.close()
        return 'None'
    else:
        edge_weight = result[2]
        conn.close()
    ## return edge_weight
    return edge_weight

def addReferralToDB(myDB, self_ID, a, b):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    INSERT INTO referrals_table (self_ID, a_userID, b_userID)
    VALUES (%s, %s, %s);
    '''
    cursor.execute(query, (self_ID, a, b))
    conn.commit()
    conn.close()

def getUserID(email):
    from app import DATABASE_URL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT userID FROM applicant_pool WHERE email = %s;
    '''
    result = cursor.execute(query, (email,)).fetchone()
    conn.close()

    return result[0]

def attemptReferral(self_ID, a_email, b_email):
    print("\nPrinting self_ID:", self_ID)
    print("\nPrinting a_email", a_email)
    print("\nPrinting a_email.lower()", a_email.lower())
    print("\nPrinting b_email:", b_email)
    a = endorsementLib.getUserIDFromEmail(a_email)
    b = endorsementLib.getUserIDFromEmail(b_email)
    print("a_userID: ", a)
    print("b_userID: ", b)
    if sexBasedCompatabilityCheck(db, a, b) == False:
        print("COMPATABILITY FAILURE")
        return False
    else:
        ab_edgeWeight = getEdgeWeight(db, a, b)
        ba_edgeWeight = getEdgeWeight(db, b, a)
        if ab_edgeWeight == ba_edgeWeight == 1:
            return False
            print("TYPE-1 FAILURE")
        if ab_edgeWeight == 9 or ba_edgeWeight == 9:
            return False
            print("TYPE-9 FAILURE")
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
            addReferralToDB(db, self_ID, a, b)
            decreaseReferralsRemaining(db, self_ID)
            return True
            # return("1-None Success")
        if ab_edgeWeight == 'None' and ba_edgeWeight == 1:
            print('ere')
            algLib.addInteractionToDB(a, b, 14)
            addReferralToDB(db, self_ID, a,b)
            decreaseReferralsRemaining(db, self_ID)
            return True
            # return("None-1 Success")
        if ab_edgeWeight == ba_edgeWeight == 'None':
            print('there')
            algLib.addInteractionToDB(a, b, 14)
            algLib.addInteractionToDB(b, a, 14)
            addReferralToDB(db, self_ID, a,b)
            decreaseReferralsRemaining(db, self_ID)
            return True
            # return("None-None Success")

    
def decreaseReferralsRemaining(myDB, userID):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    UPDATE resume_table SET referrals_remaining = referrals_remaining - 1 WHERE userID = %s
    '''
    cursor.execute(query, (userID,))
    conn.commit()
    conn.close()

def getReferralInfo(myDB, referredUser):
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    refsList = []
    cursor = conn.cursor()
    query = '''
    SELECT * FROM referrals_table WHERE a_userID = %s OR b_userID = %s
    '''
    cursor.execute(query, (referredUser, referredUser))
    rows = cursor.fetchall()
    for row in rows:
        from_userID = row[0]
        a_userID = row[1]
        b_userID = row[2]
        refsList.append((from_userID, a_userID, b_userID))
    conn.close()
    return(refsList)

