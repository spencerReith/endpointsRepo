## REFERRAL LIB
## defines important things for referals
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


db = 'main.db'


########################################################
### FUNCTIONS RELATING TO REFERRALS ####################
########################################################

## Run createReferralsTable
def createReferralsTable(myDB):
    conn = sqlite3.connect(myDB)
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
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM applicant_pool WHERE userID = ?;
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
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM interactions_table WHERE a_userID = ? AND b_userID = ?;
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
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    INSERT INTO referrals_table (self_ID, a_userID, b_userID)
    VALUES (?, ?, ?);
    '''
    cursor.execute(query, (self_ID, a, b))
    conn.commit()
    conn.close()

def getUserID(email):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT userID FROM applicant_pool WHERE email = ?;
    '''
    result = cursor.execute(query, (email,)).fetchone()
    conn.close()

    return result[0]

def attemptReferral(self_ID, a_email, b_email):
    a = getUserID(a_email)
    b = getUserID(b_email)
    if sexBasedCompatabilityCheck(db, a, b) == False:
        # return("COMPATABILITY FAILURE")
        return False
    else:
        ab_edgeWeight = getEdgeWeight(db, a, b)
        ba_edgeWeight = getEdgeWeight(db, b, a)
        if ab_edgeWeight == ba_edgeWeight == 1:
            return False
            # return("TYPE-1 FAILURE")
        if ab_edgeWeight == 9 or ba_edgeWeight == 9:
            return False
            # return("TYPE-9 FAILURE")
        if ab_edgeWeight == 14 or ba_edgeWeight == 14:
            return False
            # return("TYPE-14 FAILURE")
        if ab_edgeWeight == 0 or ba_edgeWeight == 0:
            return False
            # return("TYPE-0 FAILURE")
        if ab_edgeWeight == 1 and ba_edgeWeight == 'None':
            algLib.addInteractionToDB(b, a, 14)
            addReferralToDB(db, self_ID, a, b)
            decreaseReferralsRemaining(db, self_ID)
            return True
            # return("1-None Success")
        if ab_edgeWeight == 'None' and ba_edgeWeight == 1:
            algLib.addInteractionToDB(a, b, 14)
            addReferralToDB(db, self_ID, a,b)
            decreaseReferralsRemaining(db, self_ID)
            return True
            # return("None-1 Success")
        if ab_edgeWeight == ba_edgeWeight == 'None':
            algLib.addInteractionToDB(a, b, 14)
            algLib.addInteractionToDB(b, a, 14)
            addReferralToDB(db, self_ID, a,b)
            decreaseReferralsRemaining(db, self_ID)
            return True
            # return("None-None Success")

    
def decreaseReferralsRemaining(myDB, userID):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    UPDATE resume_table SET referrals_remaining = referrals_remaining - 1 WHERE userID = ?
    '''
    cursor.execute(query, (userID,))
    conn.commit()
    conn.close()

def getReferralInfo(myDB, referredUser):
    # list of tuples in order (from_user other_user)
    refsList = []
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM referrals_table WHERE a_userID = ? OR b_userID = ?
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

