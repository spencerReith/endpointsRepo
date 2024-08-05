"""
applicant.py – 'applicant' module for Tindar web application

The applicant module holds data about an individual applicant, which is used 
to connect them to other applicants.

Spencer Reith, Summer 2024

"""
import libraries.resumeLib as resumeLib

class Applicant:
    def __init__(self, userID, email, classYear, sex, prefSex):
        self.userID = userID
        self.name = resumeLib.parseName(email)
        self.email = email
        self.classYear = classYear
        self.sex = sex
        self.prefSex = prefSex
    
    def getUserId(self):
        return self.userID
    
    def getName(self):
        return self.name
    
    def getEmail(self):
        return self.email
    
    def getClassYear(self):
        return self.classYear
    
    def getSex(self):
        return self.sex
    
    def getPrefSex(self):
        return self.prefSex