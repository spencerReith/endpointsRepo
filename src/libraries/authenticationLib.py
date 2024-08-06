import sqlite3
import hashlib


db = 'main.db'


def createAuthorizationTable():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS authorization_table (
        userID INTEGER PRIMARY KEY,
        email STRING,
        hashedKey STRING
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def insert_passcode(userID, email, password):
    hashed_key = hash_with_sha256(password)
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    INSERT INTO authorization_table (hashedKey, email, userID) VALUES (?, ?, ?)
    '''
    cursor.execute(query, (hashed_key, email, userID))
    conn.commit()
    conn.close()

def pullHash(email):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT hashedKey FROM authorization_table WHERE email = ?;
    '''
    hash = cursor.execute(query, (email,)).fetchone()[0]
    conn.close()
    return hash

def emailInDB(email):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT 1 FROM authorization_table WHERE email = ?;
    '''
    result = cursor.execute(query, (email,)).fetchall()
    conn.close()
    if result:
        return True
    else:
        return False

def pullUserID(email):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT userID FROM authorization_table WHERE email = ?;
    '''
    userID = cursor.execute(query, (email,)).fetchone()[0]
    conn.close()
    return userID

def hash_with_sha256(password):
    return hashlib.sha256(password.encode()).hexdigest()

def passwordIsAccurate(email, provided_password):
    provided_hash = hash_with_sha256(provided_password)
    if provided_hash == pullHash(email):
        return True
    else:
        return False
