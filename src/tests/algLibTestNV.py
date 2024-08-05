## 'algLibTestNV.py' – very similar to 'algLibTest', but no visualizaiton of graphs to avoid time delay
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from libraries import algLib
import libraries.analyticsLib as analyticsLib
import libraries.referralLib as referralLib
import libraries.endorsementLib as endorsementLib
import libraries.getterLib as getterLib
import libraries.setterLib as setterLib
import libraries.resumeLib as resumeLib
import libraries.cencorshipLib as cencorshipLib
import sqlite3
import random
import algorithm
from tests.applicantDictAssembler import getApplicantDict


myDB = '../../main.db'
cap = 5

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
    GPA = random.randint(330,400) / 100
    ricePurityScore = random.randint(40,80)
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
    algLib.addInteractionToDB(random_userIDs[0], random_userIDs[1], interaction)

## adding swiping connections for userID=500
algLib.addInteractionToDB(500, 700, 1)
algLib.addInteractionToDB(700, 500, 1)
algLib.addInteractionToDB(500, 701, 1)
algLib.addInteractionToDB(701, 500, 1)
algLib.addInteractionToDB(500, 702, 1)
algLib.addInteractionToDB(702, 500, 1)
algLib.addInteractionToDB(500, 703, 1)
algLib.addInteractionToDB(703, 500, 1)

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
        selfQueue = algorithm.getCompositeQueue(selfID_Graph, selfID, cap)
        print("Queue: ", selfQueue)
        for b_userID in selfQueue:
            swipe_choice = random.randint(0, 1)
            algLib.addInteraction(myDB, selfID_Graph, selfID, b_userID, swipe_choice)



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



print(referralLib.attemptReferral(105, 101, 500))
print(referralLib.attemptReferral(105, 152, 500))
print(referralLib.attemptReferral(105, 153, 500))
print(referralLib.attemptReferral(105, 160, 500))
print(referralLib.attemptReferral(105, 165, 500))
print(referralLib.attemptReferral(105, 170, 500))

print("\nprinting connections dict:")
print(getterLib.getConnections(500))
print("")

# analyticsLib.getHistogram(myDB, 100)

# setterLib.assignUserID("Bob Saint Elmo Jones")

print(resumeLib.parseName("bob.jones.joneson.iii.iv.McDavice.3rd.26@dartmouth.edu"))
print(cencorshipLib.is_banned("d.e.shaw.26@dartmouth.edu"))
print(cencorshipLib.is_banned("bob.jones.iii.26@dartmouth.edu"))
print(cencorshipLib.is_banned("fake.email.26@dartmouth.edu"))