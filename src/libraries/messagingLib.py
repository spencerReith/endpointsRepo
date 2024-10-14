import sqlite3
import src.libraries.authenticationLib as authenticationLib


db = 'main.db'


def createMessagesTable():
    conn = sqlite3.connect(db)
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
    ## ensure lower userID will be marked as 'a_userID' in DB
    if user1_ID < user2_ID:
        userA_ID = user1_ID
        userB_ID = user2_ID
    else:
        userA_ID = user2_ID
        userB_ID = user1_ID

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT messageString FROM messages_table WHERE a_userID = ? AND b_userID = ?
    '''
    result = cursor.execute(query, (userA_ID, userB_ID)).fetchone()
    conn.commit()
    conn.close()
    if result:
        rawMessageString = result[0]
    else:
        rawMessageString = None
    return rawMessageString

def retrieveMessages(self_userID, other_userID):
    rawMessageString = retrieveRawMessageString(self_userID, other_userID)
    if rawMessageString == None:
        return None
    else:
        mTupleList = parseMessage(rawMessageString)
        return mTupleList

def concatonateMessage(user1_ID, user2_ID, concatString):
    ## ensure lower userID will be marked as 'a_userID' in DB
    if user1_ID < user2_ID:
        userA_ID = user1_ID
        userB_ID = user2_ID
    else:
        userA_ID = user2_ID
        userB_ID = user1_ID

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    ## either concatonate onto message string, or add a new row to the table for the new conversation
    query = '''
    UPDATE messages_table
    SET messageString = messageString || ?
    WHERE a_userID = ? AND b_userID = ?
    '''
    cursor.execute(query, (concatString, userA_ID, userB_ID))
    if cursor.rowcount == 0:
        insert_query = '''
        INSERT INTO messages_table (a_userID, b_userID, messageString) 
        VALUES (?, ?, ?);
        '''
        cursor.execute(insert_query, (userA_ID, userB_ID, concatString))
    conn.commit()
    conn.close()


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