import psycopg2
import sqlite3
import src.libraries.authenticationLib as authenticationLib
from sqlalchemy import text

# from app import db
# db = 'main.db'


def createMessagesTable():
    from app import DATABASE_URL
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS messages_table (
        a_userID INTEGER,
        b_userID INTEGER,
        messageString STRING,
        UNIQUE(a_userID, b_userID),
        CHECK (a_userID < b_userID)
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def parseMessage(messageString):
    if messageString == None:
        return None
    splitArray = messageString.strip('}').split('}')
    # print(len(splitArray))
    mTupleList = []
    for i in range(0, len(splitArray), 2):
        messageTuple = (splitArray[i], splitArray[i+1])
        mTupleList.append(messageTuple)
    return mTupleList

def retrieveRawMessageString(user1_ID, user2_ID):
    from app import engin
    
    ## ensure lower userID will be marked as 'a_userID' in DB
    if user1_ID < user2_ID:
        userA_ID = user1_ID
        userB_ID = user2_ID
    else:
        userA_ID = user2_ID
        userB_ID = user1_ID

    with engin.connect() as connection:
        query = text('''
        SELECT "messageString" 
        FROM messages_table 
        WHERE "a_userID" = :userA_ID AND "b_userID" = :userB_ID
        ''')
        result = connection.execute(query, {'userA_ID': userA_ID, 'userB_ID': userB_ID}).fetchone()

    return result[0] if result else None

def retrieveMessages(self_userID, other_userID):
    rawMessageString = retrieveRawMessageString(self_userID, other_userID)
    if rawMessageString == None:
        return None
    else:
        mTupleList = parseMessage(rawMessageString)
        return mTupleList

# def concatonateMessage(user1_ID, user2_ID, concatString):
#     from app import engin
    
#     ## ensure lower userID will be marked as 'a_userID' in DB
#     if user1_ID < user2_ID:
#         userA_ID = user1_ID
#         userB_ID = user2_ID
#     else:
#         userA_ID = user2_ID
#         userB_ID = user1_ID

#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     ## either concatonate onto message string, or add a new row to the table for the new conversation
#     query = '''
#     UPDATE messages_table
#     SET "messageString" = "messageString" || %s
#     WHERE "a_userID" = %s AND "b_userID" = %s
#     '''
#     cursor.execute(query, (concatString, userA_ID, userB_ID))
#     if cursor.rowcount == 0:
#         insert_query = '''
#         INSERT INTO messages_table ("a_userID", "b_userID", "messageString") 
#         VALUES (%s, %s, %s);
#         '''
#         cursor.execute(insert_query, (userA_ID, userB_ID, concatString))
#     conn.commit()
#     conn.close()

def concatonateMessage(user1_ID, user2_ID, concatString):
    from app import engin

    if user1_ID < user2_ID:
        userA_ID = user1_ID
        userB_ID = user2_ID
    else:
        userA_ID = user2_ID
        userB_ID = user1_ID

    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            UPDATE messages_table
            SET "messageString" = "messageString" || :concatString
            WHERE "a_userID" = :userA_ID AND "b_userID" = :userB_ID
            ''')
            result = connection.execute(query, {
                'concatString': concatString,
                'userA_ID': userA_ID,
                'userB_ID': userB_ID
            })
            
            if result.rowcount == 0:
                insert_query = text('''
                INSERT INTO messages_table ("a_userID", "b_userID", "messageString") 
                VALUES (:userA_ID, :userB_ID, :concatString)
                ''')
                connection.execute(insert_query, {
                    'userA_ID': userA_ID,
                    'userB_ID': userB_ID,
                    'concatString': concatString
                })
            
            transaction.commit()
        except:
            transaction.rollback()
            raise


def sendMessage(fromUserID, toUserID, message):
    ## Remove problematic characters from message ##
    message_list = list(message)
    for i in range(len(message_list)):
        if message_list[i] == '}' or message_list[i] == '`' or message_list[i] == '/' or message_list[i] == '<' or message_list[i] == '>' or message_list[i] == '$' or message_list[i] == '*' or message_list[i] == ';' or message_list[i] == '=' or message_list[i] == '-':
            message_list[i] = '_'
    message = ''.join(message_list)
            
    # fromUserID = authenticationLib.pullUserID(fromEmail)
    # toUserID = authenticationLib.pullUserID(toEmail)
    ## create properly formatted message string
    concatString = str(fromUserID) + "}" + message + "}"
    concatonateMessage(fromUserID, toUserID, concatString)
    return concatString