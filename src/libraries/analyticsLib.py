## library for analytics
import os
import sys
import mpld3

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
    print(userID)
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
    print(header)
    print(statistics) ## for now, I'll add functions later
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
    myDB = db
    numberOfBins = 20
    df = getTindarIndexDF(myDB)
    
    # Plot histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    df['tindarIndex'].plot(kind='hist', bins=numberOfBins, color='lightpink', edgecolor='maroon', grid=False, ax=ax)
    ax.set_title('Tindar Index Histogram')
    ax.set_xlabel('Tindar Index')
    ax.set_ylabel('Frequency')
    
    # Plot user & percentile
    userScore = df.loc[df['userID'] == userID, 'tindarIndex'].values[0]
    userScore = round(userScore, 2)
    userPercentile = percentileofscore(df['tindarIndex'], userScore)
    userPercentile = round(userPercentile, 2)
    
    ax.axvline(x=userScore, color='black', linestyle='solid', linewidth=10, label=f'TindarIndex = {userScore}')
    ax.axvline(x=userScore + .008, color='pink', linestyle='solid', linewidth=2, label=f'TindarIndex Percentile = {userPercentile}')
    
    ax.legend()
    
    # Save as HTML
    # html_str = mpld3.fig_to_html(fig)
    # with open("templates/otherProfile.html", "w") as f:
    #     f.write(html_str)



                    # def getHistogram(userID):
                    #     myDB = db
                    #     numberOfBins = 20
                    #     df = getTindarIndexDF(myDB)
                    #     ## plot histogram
                    #     df['tindarIndex'].plot(kind='hist', bins=numberOfBins, color='lightpink', edgecolor='maroon', figsize=(10, 6), grid=False, title='Tindar Index Histogram') 
                    #     plt.xlabel('Tindar Index')
                    #     plt.ylabel('Frequency')
                    #     ## plot user & percentile
                    #     userScore = df.loc[df['userID'] == userID, 'tindarIndex'].values[0]
                    #     userScore = round(userScore, 2)
                    #     userPercentile = percentileofscore(df['tindarIndex'], userScore)
                    #     userPercentile = round(userPercentile, 2)
                    #     plt.axvline(x=userScore, color='black', linestyle='solid', linewidth=10, label=f'TindarIndex = {userScore}')
                    #     plt.axvline(x=userScore+.008, color='pink', linestyle='solid', linewidth=2, label=f'TindarIndex Percentile = {userPercentile}')

                    #     # plt.legend()
                    #     # plt.show()