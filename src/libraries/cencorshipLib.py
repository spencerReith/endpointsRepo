import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from better_profanity import profanity
import sqlite3
import pandas as pd

bannedNamesPath = 'testingOutput/bannedNames.csv'


def contains_prof(message):
    profanity.add_censor_words(additionalBadWords)
    ## if message is a string
    if isinstance(message, str):
        if profanity.contains_profanity(message):
            print("profain statement: ", message)
            return True
        return False
    ## if message is a list of strings
    elif isinstance(message, list):
        for word in message:
            if profanity.contains_profanity(word):
                print("profain statement: ", message)
                return True
        return False
    else:
        return True
    
def remove_from_applicantPool(myDB, userID):
    ## fetch their email to ban them for future
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT email FROM applicant_pool WHERE userID = ?
    '''
    cursor.execute(query, (userID,))
    email = cursor.fetchone()
    ## remove them from the applicant pool
    query = '''
    DELETE FROM applicant_pool WHERE userID = ?
    '''
    cursor.execute(query, (userID,))
    conn.commit()
    conn.close()

    ## remove them from their resume from the resume deck
    ## add their name to the banned_emails
    with open(bannedNamesPath, 'a') as file:
        file.write('\n' + email[0] + ',')


    ## delete all connections in database
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    DELETE FROM interactions_table WHERE a_userID = ? OR b_userID = ?
    '''
    cursor.execute(query, (userID, userID))
    conn.commit()
    conn.close()

def remove_endorsements(myDB, a_userID, b_userID):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    DELETE FROM endorsements_table WHERE a_userID = ? AND b_userID = ?
    '''
    cursor.execute(query, (a_userID, b_userID))
    query = '''
    DELETE FROM endorsements_table WHERE a_userID = ? AND b_userID = ?
    '''
    cursor.execute(query, (b_userID, a_userID))
    conn.commit()
    conn.close()

def is_banned(email):
    df = pd.read_csv(bannedNamesPath)
    if email in df['email'].values:
        return True
    return False





additionalBadWords = [
    'head',
    'sexy',
    'banging',
    'sloppy',
]