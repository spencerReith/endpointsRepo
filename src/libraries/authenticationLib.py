import psycopg2
import sqlite3
import hashlib
from sqlalchemy import text

# #################
# CONFIG_DATABASE_URL = 'postgresql+psycopg2://uenjmmbebllolo:pe3ec20e2633908367b0d8e83665f0f392cb1d17ae8d18d781a6462a3abbe37ce@c9mq4861d16jlm.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/df2upfom9smjvg'
# engine = create_engine(CONFIG_DATABASE_URL)
# #################

def createAuthorizationTable():
    from app import DATABASE_URL

    conn = psycopg2.connect(DATABASE_URL)
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
    from app import engin

    hashed_key = hash_with_sha256(password)
    
    with engin.connect() as connection:
        transaction = connection.begin()
        try:
            query = text('''
            INSERT INTO authorization_table ("hashedKey", "email", "userID")
            VALUES (:hashedKey, :email, :userID)
            ''')
            connection.execute(query, {
                'hashedKey': hashed_key,
                'email': email,
                'userID': userID
            })
            transaction.commit()
        except:
            transaction.rollback()
            raise


def pullHash(email):
    from app import engin
    # Create a new connection using the engine
    with engin.connect() as connection:
        # Use a parameterized query to avoid SQL injection
        query = text('SELECT "hashedKey" FROM authorization_table WHERE "email" = :email')
        result = connection.execute(query, {'email': email})
        hash = result.fetchone()
        
        # Return the hash if a result was found, otherwise return None
        if hash:
            return hash[0]
        return None


def emailInDB(email):
    from app import engin

    with engin.connect() as connection:
        query = text('SELECT 1 FROM authorization_table WHERE "email" = :email')
        result = connection.execute(query, {'email': email}).fetchall()
        
    return bool(result)


def pullUserID(email):
    from app import engin
    
    with engin.connect() as connection:
        query = text('SELECT "userID" FROM authorization_table WHERE "email" = :email')
        result = connection.execute(query, {'email': email})
        userID = result.fetchone()
        
        if userID:
            return userID[0]
        return None

def hash_with_sha256(password):
    return hashlib.sha256(password.encode()).hexdigest()

def passwordIsAccurate(email, provided_password):
    provided_hash = hash_with_sha256(provided_password)
    if provided_hash == pullHash(email):
        return True
    else:
        return False
