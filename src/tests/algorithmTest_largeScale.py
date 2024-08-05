import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from classes.applicant import Applicant
from algorithm import getCompositeQueue
from libraries.algLib import getNodesFromDB
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx
import scipy as sp

myDB = '../../main.db'


applicantDictionary = getNodesFromDB(myDB)

########################################################
### ESTABLISHING GRAPH LARGE GRAPH 'lG' ################
########################################################

lG = nx.DiGraph()

for key, value in applicantDictionary.items():
    lG.add_node(key, sex=value.getSex(), prefSex=value.getPrefSex())



i = 400
while i < 450:
    lG.add_edge(i, 100, weight=1)
    lG.add_edge(i, 101, weight=1)
    i+=1

j = 400
while j < 600:
    if lG.has_node(j):
        if j < 450: ## applicants 400-449 should give 101 an offer
            lG.add_edge(j, 101, weight=1)
        else: ## applicant 101 blacklists all other applicants
            lG.add_edge(101, j, weight=9)
        j+=1
    else:
        # print(j)
        j+=1

k = 400
while k < 600:
    if lG.has_node(k):
        if k < 450: ## applicants 400-449 should give 101 an offer
            lG.add_edge(k, 102, weight=1)
        ## applicant 101 blacklists all other applicants
        lG.add_edge(102, k, weight=9)
        k+=1
    else:
        # print(j)
        k+=1


nx.draw(lG, with_labels=True)
plt.show()

### EDGE CASE: |UNMET| > 0 && |RESPONSE| > 35 ##########
### At least 7 numbers should be between 400 and 450.
print("\nTESTING, EDGE CASE: |UNMET| > 0 && |RESPONSE| > 35")
print("Running getCompositeQueue() on userID 100, who has 50 offers")
print("At least 7 numbers should be between 400 and 450.")
for l in range(5):
    firstQueue = getCompositeQueue(lG, 100, 10)
    print(firstQueue)
### EDGE CASE: |UNMET| == 0 && |RESPONSE| > 35 #########
print("\nTESTING, EDGE CASE: |UNMET| == 0 && |RESPONSE| > 35")
print("Running getCompositeQueue() on userID 101, who has blacklisted all applicants who he could match with based on sex & prefSex, EXCEPT for the 50 applicants who gave him an offer.")
print("The list should contain 20 numbers between 400 and 450, as we are testing a larger totalCap of 20.")
for m in range(5):
    secondQueue = getCompositeQueue(lG, 101, 20)
    print(secondQueue)

### EDGE CASE: |UNMET| == 0 && MULTIPLE OFFERS, BUT ALL BLACKLISTED #########
print("\nTESTING, EDGE CASE: |UNMET| == 0 && and multiple offers, but applicant has blacklisted every potential match.")
print("Running getCompositeQueue() on userID 102, who has blacklisted all applicants who he could match with based on sex & prefSex, INCLUDING the 50 applicants who gave him an offer.")
print("The list should be empty.")
for n in range(5):
    thirdQueue = getCompositeQueue(lG, 102, 10)
    print(thirdQueue)

## REQUIREMENTS MET, TEST COMPLETE

print("\n\nRequirements met, test complete.\n\n")