"""
applicantDriver.py –

The 'applicantDriver' file will be used to test the applicant module.

Spencer Reith, Summer 2024

"""
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from classes.applicant import Applicant


def main():

    applicantTest = open('../../testingOutput/applicantTest.txt', 'w')
    print("Creating an applicant object called applicantA, with arbitrary parameters.\n", file=applicantTest)
    applicantA = Applicant(12, "D.E. Shaw", "d.e.shaw.26@dartmouth.edu", 2026, 'm', 'f')
    
    print("Testing 'Getter' Methods.", file=applicantTest)
    print("userID:", applicantA.getUserId(), file=applicantTest)
    print("name:", applicantA.getName(), file=applicantTest)
    print("email:", applicantA.getEmail(), file=applicantTest)
    print("class year:", applicantA.getClassYear(), file=applicantTest)
    print("sex:", applicantA.getSex(), file=applicantTest)
    print("pref sex:", applicantA.getPrefSex(), file=applicantTest)

    
    applicantTest.close()
    return applicantA


applicantA = main()
