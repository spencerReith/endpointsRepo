## 'algLib.py' - contains several functions that relate to database querierying, graph visualization, editing, and analysis. These functions are relevant for our usage of the algorithm.
## Spencer Reith, Summer 2024
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from classes.applicant import Applicant
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx
import scipy as sp
from libraries import cencorshipLib


########################################################
### FUNCTIONS FOR DATABASE QUERERING & GRAPH CONSTRUCTION + VISUALIZATION
########################################################

db = '../../main.db'

def getNodesFromDB(myDB):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM applicant_pool;')
    rows = cursor.fetchall()
    # store in dictionary as {userID:applicant}
    nodes = {}
    for row in rows:
        key = int(row[0])
        nodes[key] = Applicant(int(row[1]), row[3], row[4], row[5], row[6])
    conn.close()
    return nodes

def getEdgesFromDB(myDB):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM interactions_table;')
    rows = cursor.fetchall()
    # store fetched data
    edges = []
    for row in rows:
        edge = row ## key by weight
        edges.append(edge) ## item is a list of [node a, node b]
    conn.close()
    return edges


def buildSelfID_GraphFromDB(myDB, selfID):
    ## initialize graph G
    G = nx.DiGraph()
    ##  select all nodes (getNodesFromDB)
    applicantDictionary = getNodesFromDB(myDB)
    for key, value in applicantDictionary.items():
        G.add_node(key, sex=value.getSex(), prefSex=value.getPrefSex())
    
    interactionsList = getEdgesFromDB(myDB)
    for interaction in interactionsList:
        ## if node a = self or node b = self, then that interaction is from or to the relevant
        if interaction[0] == selfID or interaction[1] == selfID:
            G.add_edge(interaction[0], interaction[1], weight=interaction[2])
    
    return G ##  return whole_G


def buildWholeGraphFromDB(myDB):
    ## build graph based on db, nodes represent applicants, edges represent interactions between them
    G = nx.DiGraph()
    applicantDictionary = getNodesFromDB(myDB)
    ## get nodes (applicants)
    for key, value in applicantDictionary.items():
        G.add_node(key, sex=value.getSex(), prefSex=value.getPrefSex())
    ## get edges (interactions)
    interactionsList = getEdgesFromDB(myDB)
    for interaction in interactionsList:
        G.add_edge(interaction[0], interaction[1], weight=interaction[2])

    return G


########################################################
### FUNCTIONS FOR GRAPH/DATABASE INSERTION #############
########################################################

def createApplicantTable(myDB):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS applicant_pool (
        key INTEGER PRIMARY KEY,
        userID INTEGER,
        name TEXT,
        email TEXT,
        classYear INTEGER,
        sex CHAR(1),
        prefSex CHAR(1)
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def createEdgeTable(myDB):
    ## assumes that the interaction is going FROM user A TO user B.
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS interactions_table (
        a_userID INTEGER,
        b_userID INTEGER,
        weight INTEGER,
        UNIQUE(a_userID, b_userID)
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def addApplicantToDB(myDB, a):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    INSERT INTO applicant_pool (key, userID, name, email, classYear, sex, prefSex)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (a.getUserId(), a.getUserId(), a.getName(), a.getEmail(), a.getClassYear(), a.getSex(), a.getPrefSex()))
    conn.commit()
    conn.close()

def addInteractionToDB(a_userID, b_userID, weight):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    INSERT OR REPLACE INTO interactions_table (a_userID, b_userID, weight)
    VALUES (?, ?, ?);
    '''
    cursor.execute(query, (a_userID, b_userID, weight))
    conn.commit()
    conn.close()

def addInteractionToGraph(G, a_userID, b_userID, edge_weight):
    G.add_edge(a_userID, b_userID, weight=edge_weight)


def addInteraction(myDB, G, a_userID, b_userID, edge_weight):
    addInteractionToDB(a_userID, b_userID, edge_weight)
    addInteractionToGraph(G, a_userID, b_userID, edge_weight)


########################################################
### FUNCTIONS FOR GRAPH VISUALIZATION ##################
########################################################

def visualizeGraph(G):
    nx.draw(G, with_labels=True)
    plt.show()

## If 'a' wants to reneg on 'b', then we replace a & b's old interaction with a blacklist
def renegInDatabase(a_userID, b_userID):
    blacklist(a_userID, b_userID)


def blacklist(from_userID, to_userID):
    addInteractionToDB(db, from_userID, to_userID, 9)
    ## in case of blacklist, remove all previous endorsements the users have made of eachother
    cencorshipLib.remove_endorsements(db, from_userID, to_userID)
