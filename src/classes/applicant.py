"""
applicant.py – 'applicant' module for Tindar web application

The applicant module holds data about an individual applicant, which is used 
to connect them to other applicants.

Spencer Reith, Summer 2024

"""
import libraries.resumeLib as resumeLib

class Applicant:
    def __init__(self, userID, email, sex, prefSex):
        print('atempting init')
        self.userID = userID
        print('fail00')
        self.name = resumeLib.parseName(email)
        print('fail01')
        self.email = email
        print('fail02')
        self.classYear = resumeLib.parseClassYear(email)
        print('fail03')
        self.sex = sex
        self.prefSex = prefSex
        print('fail, on exit')
    
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