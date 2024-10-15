import psycopg2
import sqlite3
import hashlib

# from app import db
# db = 'main.db'


def createAuthorizationTable():
    from app import db

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
    from app import db

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
    from app import db

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT hashedKey FROM authorization_table WHERE email = %s;
    '''
    hash = cursor.execute(query, (email,)).fetchone()[0]
    conn.close()
    return hash

def emailInDB(email):
    from app import DATABASE_URL

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    query = '''
    SELECT 1 FROM authorization_table WHERE email = %s;
    '''
    cursor.execute(query, (email,))
    
    if cursor.fetchall():
        result = cursor.fetchall()
        conn.close()
        return True
    else:
        conn.close()
        return False

def pullUserID(email):
    from app import db

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
