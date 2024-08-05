# 'endorsementTest.py' – Testing endorsement features
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from classes.applicant import Applicant
import libraries.endorsementLib as endorsementLib
import libraries.algLib as algLib
import libraries.cencorshipLib as cencorshipLib
import libraries.resumeLib as resumeLib
import libraries.getterLib as getterLib
import sqlite3

########################################################
### RESET DATABASE #####################################
########################################################

dbPath = '../../main.db'

conn = sqlite3.connect(dbPath)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS applicant_pool;')
cursor.execute('DROP TABLE IF EXISTS interactions_table;')
cursor.execute('DROP TABLE IF EXISTS endorsements_table;')
conn.commit()
conn.close()


########################################################
### CREATING APPLICANT POOL ############################
########################################################

applicantDictionary = {}

## Straight Men

dShaw = Applicant(100, "D.E. Shaw", "d.e.shaw.26@dartmouth.edu", 2026, 'm', 'f')
applicantDictionary[100] = dShaw
jSteinbeck = Applicant(101, "John Steinbeck", "j.steinbeck.26@dartmouth.edu", 2026, 'm', 'f')
applicantDictionary[101] = jSteinbeck


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


## Bisexual Women

Zenobia = Applicant(500, "Zenobia Nightingale", "zenobia.nightingale@dartmouth.edu", 2025, 'f', 'b')
applicantDictionary[500] = Zenobia
Isolde = Applicant(501, "Isolde Moonshadow", "isolde.moonshadow@dartmouth.edu", 2023, 'f', 'b')
applicantDictionary[501] = Isolde

## Gay Women

Seraphina = Applicant(600, "Seraphina Wildheart", "seraphina.wildheart@dartmouth.edu", 2024, 'f', 'f')
applicantDictionary[600] = Seraphina
Lysandra = Applicant(601, "Lysandra Sunflower", "lysandra.sunflower@dartmouth.edu", 2025, 'f', 'f')
applicantDictionary[601] = Lysandra

algLib.createApplicantTable(dbPath)
for key in applicantDictionary:
    algLib.addApplicantToDB(dbPath, applicantDictionary[key])


## Creating endorsements talbe

endorsementLib.createEndorsementsTable(dbPath)

algLib.createEdgeTable(dbPath)
## Xerxes blacklists Zenobia Nightingale, so she cannot give him a bad endorsement
algLib.addInteractionToDB(dbPath, 200, 500, 9)
## Zenobia Nightingale tries to endorse John Steinbeck, but she's blacklisted him 
algLib.addInteractionToDB(dbPath, 500, 101, 9)

endorsementLib.attemptEndorsement(dbPath, 100, "zenobia.nightingale@dartmouth.edu", "Really good at spreadsheet modeling!")
endorsementLib.attemptEndorsement(dbPath, 100, "seraphina.wildheart@dartmouth.edu", "Great name!")
endorsementLib.attemptEndorsement(dbPath, 500, "D.E.shaw.26@dartmouth.edu", "great analytical thinker!")
endorsementLib.attemptEndorsement(dbPath, 500, "xerxes.vds.26@dartmouth.edu", "xerxes is awful, was terrible at thermopylae")
endorsementLib.attemptEndorsement(dbPath, 500, "j.steinbeck.26@dartmouth.edu", "terrible writer, an insult to books everywhere")

print("Endorsements added to db.")

algLib.blacklist(dbPath, 100, 500)
endorsementLib.attemptEndorsement(dbPath, 100, "zenobia.nightingale@dartmouth.edu", "Really good at spreadsheet modeling!")

## testing profanity checker

endorsementLib.attemptEndorsement(dbPath, 100, "seraphina.wildheart@dartmouth.edu", "bitch shit fuck")
endorsementLib.attemptEndorsement(dbPath, 100, "seraphina.wildheart@dartmouth.edu", "banging")
endorsementLib.attemptEndorsement(dbPath, 100, "seraphina.wildheart@dartmouth.edu", "head")
endorsementLib.attemptEndorsement(dbPath, 100, "seraphina.wildheart@dartmouth.edu", "hella sexy")

cencorshipLib.remove_from_applicantPool(dbPath, 100)

endorsementLib.attemptEndorsement(dbPath, 501, "lysandra.sunflower@dartmouth.edu", "cool")
endorsementLib.attemptEndorsement(dbPath, 501, "lysandra.sunflower@dartmouth.edu", "nice")
endorsementLib.attemptEndorsement(dbPath, 501, "lysandra.sunflower@dartmouth.edu", "reall great")
endorsementLib.attemptEndorsement(dbPath, 501, "lysandra.sunflower@dartmouth.edu", "very intelligent")

resumeLib.createResumeTable(dbPath)
print(getterLib.getLeaderboard())
