## library for analytics
import os
import sys
import mpld3
import numpy as np

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)



import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore

db = 'main.db'

def getStatisticsFromDB(myDB):
    # Connect to the SQLite database
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    # Fetch data from the table
    cursor.execute('SELECT * FROM statistics;')
    rows = cursor.fetchall()
    # Create a dictionary to store the fetched data
    statistics = {}
    # store in dictionary as {userID:(stat1, stat2, stat3)}
    for row in rows:
        key = int(row[0])
        statistics[key] = [row[1], row[2], row[3]]
    # Close the connection
    conn.close()
    return statistics # return nodes


########################################################
### FUNCTIONS FOR GRAPH ANALYSIS #######################
########################################################

## Run createApplicantTable
def createStatisticsTable(myDB):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS statistics (
        userID INTEGER PRIMARY KEY,
        offerReceptionRate FLOAT,
        offerBestowalRate FLOAT,
        tindarIndex FLOAT
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

##  Run calcOfferReceptionRate
def calcOfferReceptionRate(G, selfID):
    in_edges_list = list(G.in_edges(selfID, data=True))
    offers = 0
    swipes = 0
    for edge in in_edges_list:
        if edge[2]['weight'] == 1:
            offers+=1
            swipes+=1
        if edge[2]['weight'] == 0:
            swipes+=1
        else:
            continue
    ## if applicant has not recieved any swipes, leave rate as None
    if swipes == 0:
        rate = None
    else:
        rate = offers/swipes
    return rate


## Run calcOfferBestowalRate
def calcOfferBestowalRate(G, selfID):
    out_edges_list = list(G.out_edges(selfID, data=True))
    offers = 0
    swipes = 0
    for edge in out_edges_list:
        if edge[2]['weight'] == 1:
            offers+=1
            swipes+=1
        if edge[2]['weight'] == 0:
            swipes+=1
        else:
            continue
    ## if applicant has not swiped on anyone yet, leave rate as None
    if swipes == 0:
        rate = None
    else:
        rate = offers/swipes
    return rate

# Run calcTindarIndex
def calcTindarIndex(GPA, ricePurityScore):
    scaledGPA = 0
    if GPA < 3:
        scaledGPA = .1
    else:
        scaledGPA = GPA - 2.9
    tindarIndex = (scaledGPA * ricePurityScore) / 1.1

    return tindarIndex

def addTindarIndexToDB(userID, tindarIndex):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    INSERT INTO statistics (userID, tindarIndex)
    VALUES (?, ?);
    '''
    cursor.execute(query, (userID, tindarIndex))
    conn.commit()
    conn.close()

## no long needed
def fetchTindarIndex(userID):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = '''
    SELECT tindarIndex FROM statistics WHERE userID = ?;
    '''
    tindarIndex = cursor.execute(query, (userID,)).fetchone()[0]
    conn.commit()
    conn.close()
    ## return tindarIndex
    return tindarIndex


    

## Run calcApplicantStatistics
def calcApplicantStatistics(myDB, G, selfID):
    offerReceptionRate = calcOfferReceptionRate(G, selfID)
    offerBestowalRate = calcOfferBestowalRate(G, selfID)
    ## insert data into table
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    UPDATE statistics SET offerReceptionRate = ?, offerBestowalRate = ? WHERE userID = ?
    '''
    cursor.execute(query, (offerReceptionRate, offerBestowalRate, selfID))
    conn.commit()
    conn.close()


def calcStatistics(myDB, G):
    ID_list = list(G.nodes())
    for ID in ID_list:
        calcApplicantStatistics(myDB, G, ID)


##  run calcOfferReceptionRate (percentage at which an applicant recieve offers)
##  run calcOfferBestowalRate (percentage at which an applicant bestows offers)
##  write statistics into the database

## Run writeApplicantStatistics(filepath)
def writeApplicantStatistics():
    header = "\n\nStatistics Breakdown.\nTindar.\n\nThis file breaks-down several key metrics of the applicant pool.\n"
    # with open(filepath, 'w') as file:
    #     file.write(header)
    statistics = getStatisticsFromDB()
    # print(header)
    # print(statistics) ## for now, I'll add functions later
    ## now we'd want to analyze these stats
    ## lots of ways to do it... some ideas
    ## sort database by highest to lowest offerReceptionRate
    ## sort database by highest to lowest offerBestowalRate
    ## histogram of tindarIndex es
    ## tindarIndex versus offerReceptionRate
    ## tindarIndex versus offerBestowalRate
    ## offerReceptionRate versus offerBestowalRate

def getTindarIndexDF(myDB):
    conn = sqlite3.connect(myDB)
    cursor = conn.cursor()
    query = '''
    SELECT userID, tindarIndex FROM statistics
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def getHistogram(userID):
    myDB = db  # Assuming db is already defined
    numberOfBins = 20
    df = getTindarIndexDF(myDB)
    
    # Get user score
    userScore = df.loc[df['userID'] == userID, 'tindarIndex'].values[0]
    userScore = round(userScore, 2)
    
    # Create histogram
    counts, bins, patches = plt.hist(df['tindarIndex'], bins=numberOfBins, color='lightpink', edgecolor='maroon')
    
    # Highlight the bin that contains the userScore
    bin_index = np.digitize(userScore, bins) - 1
    bin_index = min(bin_index, len(patches) - 1)  # Ensure bin_index is within range
    patches[bin_index].set_facecolor('pink')
    
    # Plot histogram with highlighted bar
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(bins[:-1], counts, width=np.diff(bins), edgecolor='maroon', color=['black' if i == bin_index else 'lightpink' for i in range(len(patches))])
    ax.set_title('Tindar Index Histogram')
    ax.set_xlabel('Tindar Index')
    ax.set_ylabel('Frequency')
    
    userPercentile = percentileofscore(df['tindarIndex'], userScore)
    userPercentile = round(userPercentile, 2)

    ax.text(0.7 * max(bins), 0.99 * max(counts), f'TindarIndex = {userScore}', fontsize=14, color='black')
    ax.text(0.7 * max(bins), 0.94 * max(counts), f'TindarIndex Percentile = {userPercentile}', fontsize=14, color='black')
    
    # Convert to HTML string
    html_str = mpld3.fig_to_html(fig)
    
    return html_str
