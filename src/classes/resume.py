"""
resume.py – 'resume' module for Tindar web application

The resume module contains information regarding an applicant's resumé.

Spencer Reith – Summer 2024
"""

import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


import random
from datetime import date

class Resume:
    wordInputCap = 10
    def __init__(self, userID, major, minor, skills, interests, blurbEntries):
        self.userID = userID
        self.major = major
        self.minor = minor
        self.skills = skills
        self.interests = interests
        self.blurb = self.createBlurb(blurbEntries)

        self.referrals_remaining = 3
        self.endorsements_remaining = 5
        self.swipes_remaining = 40
        self.last_login = date.today()
        
    def createBlurb(self, wordEntries):
        amntOfBlurbs = 3
        blurbsPath = 'textFiles/blurbs.txt'

        randomNumber = random.randint(0, amntOfBlurbs - 1)

        blurbsFile = open(blurbsPath)
        blurbText = ""
        i = 0
        for line in blurbsFile:
            if i == randomNumber:
                blurbText = line
                break
            i += 1
        nouns = wordEntries[0:3]
        verbs = wordEntries[3:6]
        adjectives =  wordEntries[6:10]

        for i in range(len(nouns)):
            blurbText = blurbText.replace("myNoun", nouns[i], 1)
        for i in range(len(verbs)):
            blurbText = blurbText.replace("myVerb", verbs[i], 1)
        for i in range(len(adjectives)):
            blurbText = blurbText.replace("myAdjective", adjectives[i], 1)
        
        return blurbText
    
    def getUserID(self):
        return self.userID
    
    def getMajor(self):
        return self.major

    def getMinor(self):
        return self.minor

    def getSkillsString(self):
        skillsString = ""
        for skill in self.skills:
            skillsString = skillsString + skill + ','
        skillsString = str(skillsString[:-1])
        return skillsString
    
    def getInterestsString(self):
        interestsString = ""
        for interest in self.interests:
            interestsString = interestsString + interest + ','
        interestsString = str(interestsString[:-1])
        return interestsString
    
    def getBlurb(self):
        return self.blurb
    
    def getReferrals_Remaining(self):
        return self.referrals_remaining
    
    def getEndorsements_Remaining(self):
        return self.endorsements_remaining
    
    def getSwipes_Remaining(self):
        return self.swipes_remaining
    
    def getLatest_Swipes_Update(self):
        return self.last_login