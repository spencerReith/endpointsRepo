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
    def __init__(self, userID, major, minor, height, skills, interests, photoID):
        self.userID = userID
        self.major = major
        self.minor = minor
        self.skills = skills
        self.interests = interests
        self.height = height
        self.photoID = photoID

        self.referrals_remaining = 3
        self.endorsements_remaining = 5
        self.swipes_remaining = 40
        self.last_login = date.today()

    
    def getUserID(self):
        return self.userID
    
    def getMajor(self):
        return self.major

    def getMinor(self):
        return self.minor
    
    def getHeight(self):
        return self.height
    
    def getPhotoID(self):
        return self.photoID

    def getSkillsString(self):
        skillsString = ""
        for skill in self.skills:
            skillsString = skillsString + skill + ', '
        skillsString = str(skillsString[:-2])
        return skillsString
    
    def getInterestsString(self):
        interestsString = ""
        for interest in self.interests:
            interestsString = interestsString + interest + ', '
        interestsString = str(interestsString[:-2])
        return interestsString
    
    def getReferrals_Remaining(self):
        return self.referrals_remaining
    
    def getEndorsements_Remaining(self):
        return self.endorsements_remaining
    
    def getSwipes_Remaining(self):
        return self.swipes_remaining
    
    def getLatest_Swipes_Update(self):
        return self.last_login