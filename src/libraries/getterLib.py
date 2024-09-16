"""
'getterLib.py' – contains the functions needed to display data on the front-end
Spencer Reith – 24X
"""

import os
import sys

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



db = 'main.db'

def getDeck(userID, cap):
    selfID_Graph = algLib.buildSelfID_GraphFromDB(db, userID)
    ## get queue of userID's to swipe through
    userID_Queue = algorithm.getCompositeQueue(selfID_Graph, userID, cap)
    deck = {}
    ## place userID & corresponding information in a double-layered dictionary
    for userID in userID_Queue:
        deck[userID] = getProfile(userID)

    return deck

def getProfile(userID):
    print("\n\nUserID:", userID)
    res_df = getResumeDF(userID)
    applicant_df = getApplicantDF(userID)
    stats_df = getStatisticsDF(userID)
    print("\n\ApplicantDF:\n", applicant_df)

    name = applicant_df['name'][0]
    email = applicant_df['email'][0]
    classYear = 2026
    major = res_df['major'].to_list()
    minor = res_df['minor'].to_list()
    skills = res_df['skills'].to_list()
    interests = res_df['interests'].to_list()
    tindarIndex = stats_df['tindarIndex'].to_list()
    endorsements = endorsementLib.fetchEndorsements(userID)

    profile = {
        'userID' : userID,
        'name': name,
        'email': email,
        'classYear' : classYear,
        'major' : major,
        'minor' : minor,
        'skills' : skills,
        'interests' : interests,
        'tindarIndex' : tindarIndex,
        'endorsements' : endorsements,
        }

    return profile


def getResumeDF(userID):
    print("\n\nuserID where there's an issue:", userID)
    conn = sqlite3.connect(db)
    query = "SELECT * FROM resume_table WHERE userID = ?"
    df = pd.read_sql_query(query, conn, params=(userID,))
    conn.close()
    return df

def getApplicantDF(userID):
    conn = sqlite3.connect(db)
    query = "SELECT * FROM applicant_pool WHERE userID = ?"
    df = pd.read_sql_query(query, conn, params=(userID,))
    conn.close()
    return df

def getStatisticsDF(userID):
    conn = sqlite3.connect(db)
    query = "SELECT * FROM statistics WHERE userID = ?"
    df = pd.read_sql_query(query, conn, params=(userID,))
    conn.close()
    return df


def getEndRefs(userID):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT endorsements_remaining, referrals_remaining
    FROM resume_table
    WHERE userID = ?
    '''
    cursor.execute(query, (userID,))
    results = cursor.fetchall()
    for row in results:
        remEndorsements, remReferrals = row
    conn.close()
    endRefs = {
        'remainingEndorsements' : remEndorsements,
        'remainingReferrals' : remReferrals
    }

    return endRefs

def getLeaderboard():
    ## create dataframe of b_userID's from endorsement_table
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT b_userID FROM endorsements_table
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    ## find and return the 5 most highly endorsed applicants
    sorted_df = df['b_userID'].value_counts()
    top5_df = sorted_df.head(5)
    leaderboardDict = top5_df.to_dict()
    return leaderboardDict

def getConnections(userID):
    swipingMatches = []
    # referrals = []
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT * FROM interactions_table WHERE a_userID = ? OR b_userID = ?
    '''
    df = pd.read_sql_query(query, conn, params=(userID, userID))
    conn.close()
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
    print("Raw_blacklist_dict: ", raw_blacklist_dict, blacklist_a_Users, blacklist_b_Users)
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
    
    
    referrals = referralLib.getReferralInfo(db, userID)
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

    print("referals", refsList)

    
                    # ## if a_userID is not one's self, it's the person he or she was referred to
                    # for i in range(len(raw_referrals_dict['a_userID'])):
                    #     a_userID = raw_referrals_dict['a_userID'][i]
                    #     if a_userID != userID:
                    #         referrals.append(a_userID)

    connections = {
        'userID' : userID,
        'swipingMatches' : swipingMatches,
        'referrals' : refsList
    }
    
    print("\nsending connections. Refs list:\n\n", refsList)
    return connections

##getEndorsements

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