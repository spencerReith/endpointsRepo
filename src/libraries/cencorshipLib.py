import psycopg2
import os
import sys
from sqlalchemy import text

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
    

def remove_from_applicantPool(userID):
    from app import engin
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('SELECT "email" FROM applicant_pool WHERE "userID" = :userID')
            email = connection.execute(query, {'userID': userID}).fetchone()

            query = text('DELETE FROM applicant_pool WHERE "userID" = :userID')
            connection.execute(query, {'userID': userID})

            transaction.commit()
        except:
            transaction.rollback()
            raise

    # Add their name to the banned_emails
    with open(bannedNamesPath, 'a') as file:
        file.write('\n' + email[0] + ',')

    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            DELETE FROM interactions_table
            WHERE "a_userID" = :userID OR "b_userID" = :userID
            ''')
            connection.execute(query, {'userID': userID})

            transaction.commit()
        except:
            transaction.rollback()
            raise


def remove_endorsements(a_userID, b_userID):
    from app import engin
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            DELETE FROM endorsements_table
            WHERE ("a_userID" = :a_userID AND "b_userID" = :b_userID)
            OR ("a_userID" = :b_userID AND "b_userID" = :a_userID)
            ''')
            connection.execute(query, {'a_userID': a_userID, 'b_userID': b_userID})

            transaction.commit()
        except:
            transaction.rollback()
            raise


def is_banned(email):
    df = pd.read_csv(bannedNamesPath)
    if email in df['email'].values:
        return True
    return False





additionalBadWords = [
    'head',
    'sexy',
    'sex',
    'banging',
    'sloppy',
    '}',
    '{',
    '-',
    '=',
    '\'',
    '\\',
    '/',
    '"',
    '@',
    '$',
    '&',
    '%',
    '*',
    'SELECT',
    'DELETE'
]