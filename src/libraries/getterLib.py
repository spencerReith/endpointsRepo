"""
'getterLib.py' – contains the functions needed to display data on the front-end
Spencer Reith – 24X
"""
import psycopg2
import os
import sys
from sqlalchemy import text

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import algorithm
import sqlite3
import pandas as pd
from libraries import algLib
from libraries import referralLib
from libraries import endorsementLib
import pandas as pd


def getDeck(userID, cap):
    print('Inside getDeck')
    print("userid: {userID}, {cap}}", userID, cap)
    selfID_Graph = algLib.buildSelfID_GraphFromDB(userID)

    userID_Queue = algorithm.getCompositeQueue(selfID_Graph, userID, cap)
    deck = {}
    print('pre iteration')
    print('userID_queue', userID_Queue)
    for userID in userID_Queue:
        deck[userID] = getProfile(userID)

    print('returning deck')
    return deck

def getProfile(userID):
    print("prior0")
    res_df = getResumeDF(userID)
    applicant_df = getApplicantDF(userID)
    stats_df = getStatisticsDF(userID)

    print('\nApplicant Dict Head\n')
    print(applicant_df.head())
    print("prior")
    print(applicant_df)
    name = applicant_df['name'][0]
    email = applicant_df['email'][0]
    classYear = "20" + str(applicant_df['classYear'][0])
    major = res_df['major'].to_list()
    minor = res_df['minor'].to_list()
    height = res_df['height'].to_list()
    photoID = res_df['photoID'].to_list()
    skills = res_df['skills'].to_list()
    interests = res_df['interests'].to_list()
    tindarIndex = stats_df['tindarIndex'].to_list()
    endorsements = endorsementLib.fetchEndorsements(userID)
    print("post")

    profile = {
        'userID' : userID,
        'name': name,
        'email': email,
        'classYear' : classYear,
        'major' : major,
        'minor' : minor,
        'height' : height,
        'photoID' : photoID,
        'skills' : skills,
        'interests' : interests,
        'tindarIndex' : tindarIndex,
        'endorsements' : endorsements,
        }

    return profile


def getResumeDF(userID):
    from app import engin

    query = text('''
    SELECT * FROM resume_table WHERE "userID" = :userID
    ''')
    df = pd.read_sql_query(query, engin, params={"userID": userID})
    print('got resume df')
    return df

def getApplicantDF(userID):
    from app import engin
    print('attempting appdf get')
    # conn = psycopg2.connect(DATABASE_URL)
    query = text('''
    SELECT * FROM applicant_pool WHERE "userID" = :userID
    ''')
    df = pd.read_sql_query(query, engin, params={"userID" : userID})
    # conn.close()
    print('suces appdf get')
    return df

def getStatisticsDF(userID):
    from app import engin
    
    query = text('''
    SELECT * FROM statistics WHERE "userID" = :userID
    ''')
    df = pd.read_sql_query(query, engin, params={"userID" : userID})
    return df


def getEndRefs(userID):
    from app import engin

    with engin.connect() as connection:
        query = text('''
        SELECT "endorsements_remaining", "referrals_remaining"
        FROM resume_table
        WHERE "userID" = :userID
        ''')
        results = connection.execute(query, {'userID': userID}).fetchall()

    for row in results:
        remEndorsements, remReferrals = row

    endRefs = {
        'remainingEndorsements' : remEndorsements,
        'remainingReferrals' : remReferrals
    }

    return endRefs

def getLeaderboard():
    from app import engin
    
    query = text('''
    SELECT "b_userID" FROM endorsements_table
    ''')
    df = pd.read_sql_query(query, engin)

    ## find and return the 5 most highly endorsed applicants
    sorted_df = df['b_userID'].value_counts()
    top5_df = sorted_df.head(5)
    leaderboardDict = top5_df.to_dict()
    return leaderboardDict

def getConnections(userID):
    from app import engin
    print("we here")
    swipingMatches = []
    query = text('''
    SELECT * FROM interactions_table WHERE "a_userID" = :userID OR "b_userID" = :userID
    ''')
    df = pd.read_sql_query(query, engin, params={"userID" : userID})

    ## filter by swiping connections, and refferals
    swiping_df = df[(df['weight'] == 1)]
    referrals_df = df[(df['weight'] == 14)]
    blacklist_df = df[(df['weight'] == 9)]

    ## convert swiping connections and referrals to dictionaries
    raw_swiping_interactions = swiping_df.to_dict(orient='list')
    raw_referrals_dict = referrals_df.to_dict(orient='list')
    raw_blacklist_dict = blacklist_df.to_dict(orient='list')
    blacklist_a_Users = raw_blacklist_dict['a_userID']
    blacklist_b_Users = raw_blacklist_dict['b_userID']

    seenDict = {}

    ## iterate through swiping interactions
    for i in range(len(raw_swiping_interactions['a_userID'])):
        a_userID = raw_swiping_interactions['a_userID'][i]
        b_userID = raw_swiping_interactions['b_userID'][i]
        ## when the userID in question is not one's self
        if a_userID != userID:
            ## if they've already been seen, must be a two-way connection
            if a_userID in seenDict:
                swipingMatches.append(a_userID)
            else: ## put them in, it's at least a one way connection
                seenDict[a_userID] = 1
        ## same logic applies to b_userID
        if b_userID != userID:
            if b_userID in seenDict:
                swipingMatches.append(b_userID)
            else:
                seenDict[b_userID] = 1
    
    
    referrals = referralLib.getReferralInfo(userID)
    refsList = []
    for ref in referrals:
        print("ref: ", ref)
        if ref[1] == userID:
            if ref[2] in blacklist_a_Users or ref[2] in blacklist_b_Users:
                continue
            refsList.append({'from_user' : ref[0], 'ref_connect' : ref[2]})
        if ref[2] == userID:
            if ref[1] in blacklist_a_Users or ref[1] in blacklist_b_Users:
                continue
            refsList.append({'from_user' : ref[0], 'ref_connect' : ref[1]})

    connections = {
        'userID' : userID,
        'swipingMatches' : swipingMatches,
        'referrals' : refsList
    }
    # print('per hostas logos, connections: ', connections)
    
    return connections


def overCharLimit(type, message):
    mLength = 0
    for word in message:
        for c in word:
            mLength += 1
    if type == 'skills':
        if mLength > 30:
            return True
    if type == 'interests':
        if mLength > 27:
            return True
    return False