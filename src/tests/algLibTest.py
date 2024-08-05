## 'algLibTest.py' – testing functions in the algLib (algorithm library)
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from libraries import algLib
import libraries.analyticsLib as analyticsLib
import libraries.referralLib as referralLib
import libraries.endorsementLib as endorsementLib
import sqlite3
import random
import algorithm
from tests.applicantDictAssembler import getApplicantDict


myDB = '../../main.db'

conn = sqlite3.connect(myDB)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS applicant_pool;')
cursor.execute('DROP TABLE IF EXISTS interactions_table;')
cursor.execute('DROP TABLE IF EXISTS statistics;')
cursor.execute('DROP TABLE IF EXISTS referrals_table;')
cursor.execute('DROP TABLE IF EXISTS endorsements_table;')
conn.commit()
conn.close()




## loads the mock users from CVV files into an applicant dictionary
applicantDict = getApplicantDict()



algLib.createApplicantTable(myDB)
algLib.createEdgeTable(myDB)
analyticsLib.createStatisticsTable(myDB)
referralLib.createReferralsTable(myDB)
endorsementLib.createEndorsementsTable(myDB)


for applicantKey in applicantDict:
    algLib.addApplicantToDB(myDB, applicantDict[applicantKey])
    GPA = random.randint(290,400) / 100
    ricePurityScore = random.randint(1,100)
    tindarIndex = analyticsLib.calcTindarIndex(GPA, ricePurityScore)
    analyticsLib.addTindarIndexToDB(myDB, applicantKey, tindarIndex)

for i in range(800):
    interaction = 0
    random_userIDs = random.sample(list(applicantDict.keys()), 2)
    random_number = random.randint(0,10)
    if 0 <= random_number <= 2:
        interaction = 0
    elif 3 <= random_number <= 8:
        interaction = 1
    else:
        interaction = 9
    ### AS ANNOYING AS IT IS, THE TEST WOULD BE A LOT MORE REALISTIC IF I MADE THE INTERACTIONS MORE REALISTIC... I KNOW ITS STILL GOOD, BUT, IF IM GONNA SHOW IT TO JOBS MAYBE ITS WORTH IT TO MAKE THE INTERACITONS MORE REALISTIC, BUT ALSO IT WOULD BE A PAIN IN THE ASS... I DONT KNOW
    algLib.addInteractionToDB(random_userIDs[0], random_userIDs[1], interaction)

wholeGraph = algLib.buildWholeGraphFromDB(myDB)

string_selfID_sample = random.sample(list(applicantDict.keys()), 5)
## convert userID's to integers
int_selfID_sample = []
for element in string_selfID_sample:
    int_selfID_sample.append(int(element))

print("random_selfID_sample: ", int_selfID_sample)
for selfID in int_selfID_sample:
    selfID_Graph = algLib.buildSelfID_GraphFromDB(myDB, selfID)
    print("\nselfID: ", selfID)
    selfQueue = []
    for q in range(5):
        selfQueue = algorithm.getCompositeQueue(selfID_Graph, selfID, 8)
        print("Queue: ", selfQueue)
        for b_userID in selfQueue:
            swipe_choice = random.randint(0, 1)
            algLib.addInteraction(myDB, selfID_Graph, selfID, b_userID, swipe_choice)
    algLib.visualizeGraph(selfID_Graph)

algLib.visualizeGraph(wholeGraph)

analyticsLib.calcStatistics(myDB, wholeGraph)

print("\nTindarIndex: ", analyticsLib.fetchTindarIndex(myDB, 100))
print("")


## TYPE-9 Failure
algLib.addInteractionToDB(100, 500, 9)
algLib.addInteractionToDB(500, 100, 1)

## TYPE-9 Failure
algLib.addInteractionToDB(501, 100, 9)

## TYPE-0 Failure
algLib.addInteractionToDB(502, 100, 0)

## TYPE-0 Failure
algLib.addInteractionToDB(100, 503, 0)

## TYPE-1 Failure
algLib.addInteractionToDB(100, 504, 1)
algLib.addInteractionToDB(504, 100, 1)

# 1-None Success
algLib.addInteractionToDB(100, 504, 1)

# None-1 Success
algLib.addInteractionToDB(505, 100, 1)

# None-None Success
## no interaction added between 100 & 400

print(referralLib.attemptReferral(105, 100, 200))
print(referralLib.attemptReferral(105, 100, 300))
print(referralLib.attemptReferral(105, 100, 600))
print(referralLib.attemptReferral(105, 400, 300))
print(referralLib.attemptReferral(105, 100, 300))
print(referralLib.attemptReferral(105, 400, 300))

print(referralLib.attemptReferral(105, 100, 500))
print(referralLib.attemptReferral(105, 100, 501))
print(referralLib.attemptReferral(105, 100, 502))
print(referralLib.attemptReferral(105, 100, 503))
print(referralLib.attemptReferral(105, 100, 504))

print(referralLib.attemptReferral(105, 100, 505))
print(referralLib.attemptReferral(105, 100, 400))

algLib.renegInDatabase(505, 100)