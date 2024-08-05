import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from classes.applicant import Applicant
from algorithm import getCompositeQueue
import matplotlib.pyplot as plt
import networkx as nx
import scipy as sp

########################################################
### CREATING APPLICANT POOL ############################
########################################################

applicantDictionary = {}

## Straight Men

dShaw = Applicant(100, "D.E. Shaw", "d.e.shaw.26@dartmouth.edu", 2026, 'm', 'f')
applicantDictionary[100] = dShaw
jSteinbeck = Applicant(101, "John Steinbeck", "j.steinbeck.26@dartmouth.edu", 2026, 'm', 'f')
applicantDictionary[101] = jSteinbeck
pHanlon = Applicant(102, "Philip Hanlon", "p.hanlon.77@dartmouth.edu", 1977, 'm', 'f')
applicantDictionary[102] = pHanlon

## Bisexual Men

Xerxes = Applicant(200, "Xerxes van der Spiegel", "xerxes.vds.26@dartmouth.edu", 2026, 'm', 'b')
applicantDictionary[200] = Xerxes
Thelonious = Applicant(201, "Thelonious Blackwood", "thelonious.blackwood@dartmouth.edu", 2023, 'm', 'b')
applicantDictionary[201] = Thelonious

## Gay Men

Zephyr = Applicant(301, "Zephyr Nightingale", "zephyr.nightingale@dartmouth.edu", 2024, 'm', 'm')
applicantDictionary[301] = Zephyr
Aurelius = Applicant(302, "Aurelius Thunderclap", "aurelius.thunderclap@dartmouth.edu", 2025, 'm', 'm')
applicantDictionary[302] = Aurelius

## Straight Women

jHudson = Applicant(400, "Jennifer Hudson", "j.hudson.26@dartmouth.edu", 2026, 'f', 'm')
applicantDictionary[400] = jHudson
nManaj = Applicant(401, "Nikki Manaj", "n.manaj.26@dartmouth.edu", 2026, "f", "m")
applicantDictionary[401] = nManaj
mWashington = Applicant(402, "Martha Washington", "m.washington.53", 1753, 'f', 'm')
applicantDictionary[402] = mWashington

## Bisexual Women

Zenobia = Applicant(500, "Zenobia Nightingale", "zenobia.nightingale@dartmouth.edu", 2025, 'f', 'b')
applicantDictionary[500] = Zenobia
Isolde = Applicant(501, "Isolde Moonshadow", "isolde.moonshadow@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[501] = Isolde
Lysandera_Blackwood = Applicant(502, "Lysandera Blackwood", "lysandera.blackwood@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[502] = Lysandera_Blackwood
Thalassa_Seafoam = Applicant(503, "Thalassa Seafoam", "thalassa.seafoam@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[503] = Thalassa_Seafoam
Oriona_Nightshade = Applicant(504, "Oriona Nightshade", "oriona.nightshade@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[504] = Oriona_Nightshade
Sorena_Stormbringer = Applicant(505, "Sorena Stormbringer", "sorena.stormbringer@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[505] = Sorena_Stormbringer
Elara_Winterbourne = Applicant(506, "Elara Winterbourne", "elara.winterbourne@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[506] = Elara_Winterbourne
Cassia_Thornbrook = Applicant(507, "Cassia Thornbrook", "cassia.thornbrook@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[507] = Cassia_Thornbrook


## Gay Women

Seraphina = Applicant(600, "Seraphina Wildheart", "seraphina.wildheart@dartmouth.edu", 2024, 'f', 'f')
applicantDictionary[600] = Seraphina
Lysandra = Applicant(601, "Lysandra Sunflower", "lysandra.sunflower@dartmouth.edu", 2025, 'f', 'f')
applicantDictionary[601] = Lysandra

########################################################
### ESTABLISHING GRAPH SMALL GRAPH 'sG' ################
########################################################

sG = nx.DiGraph()

for key, value in applicantDictionary.items():
    sG.add_node(key, sex=value.getSex(), prefSex=value.getPrefSex())

########################################################
### ADDING INTERACTIONS BETWEEN NODES ##################
########################################################

sG.add_edge(100, 500, weight=9)
sG.add_edge(100, 501, weight=9)
sG.add_edge(100, 502, weight=0)
sG.add_edge(100, 503, weight=1)
sG.add_edge(400, 100, weight=1)
sG.add_edge(401, 100, weight=1)

sG.add_edge(302, 301, weight=9)
sG.add_edge(200, 301, weight=1)
sG.add_edge(201, 301, weight=1)

sG.add_edge(302, 200, weight=9)
sG.add_edge(302, 201, weight=0)

########################################################
### TEST WORKABILITY FOR {m,f} connection ##############
########################################################

print('\nTESTING: {m,f} from userID 100. Composite queue should be size 5. One member from the reciprocation list. No blacklisted or previously interacted nodes should be in the queue.\n')
for i in range(5):
    compositeQueue = getCompositeQueue(sG, 100, 5)
    print(compositeQueue)


nx.draw(sG, with_labels=True)
plt.show()

########################################################
### EDGE CASE: |UNMET| == 0 ############################
########################################################

print('\nTESTING: {m,m} from userID 301. |unmet| will equal 0. remaining elements in response will be printed, and |response| will equal 2.\n')
for i in range(5):
    compositeQueue = getCompositeQueue(sG, 301, 5)
    print(compositeQueue)


nx.draw(sG, with_labels=True)
plt.show()

########################################################
### EDGE CASE: |RESPONSE| == 0 #########################
########################################################

print('\nTESTING: {f,f} from userID 601. |unmet| > 0, but |response| == 0.\n')
for i in range(5):
    compositeQueue = getCompositeQueue(sG, 601, 5)
    print(compositeQueue)


nx.draw(sG, with_labels=True)
plt.show()

########################################################
### EDGE CASE: |UNMET| == 0 && |RESPONSE| = 0 ##########
########################################################

print('\nTESTING: {m,m} from userID 302. |unmet| == 0 && |response| == 0.\n')
for i in range(5):
    compositeQueue = getCompositeQueue(sG, 302, 5)
    print(compositeQueue)


nx.draw(sG, with_labels=True)
plt.show()

print("Requirements met, test complete.")