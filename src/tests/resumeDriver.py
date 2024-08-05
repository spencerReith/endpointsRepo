"""
resumeDriver.py –

The 'resumeDriver' file will be used to test the resume module.

Spencer Reith, Summer 2024

"""
import os
import sys

dirname = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(dirname, os.pardir))
sys.path.append(parent_dir)


from classes.resume import Resume

def main():

    resumeTest = open('../../testingOutput/resumeTest.txt', 'w')
    print("Creating a resume object called resA, with arbitrary parameters.\n", file=resumeTest)
    wordsList = ["dog", "house", "person", "run", "jump", "fly", "red", "3", "tall"]
    resA = Resume(12, "Cognitive Science", "Dutch Topology", ["Good at craftsmanship", "strong", "friendly"], ["history", "social science", "cards"], wordsList)
    
    print("Testing 'Getter' Methods.", file=resumeTest)
    print("userID:", resA.getUserID(), file=resumeTest)
    print("major:", resA.getMajor(), file=resumeTest)
    print("minor:", resA.getMinor(), file=resumeTest)
    print("skills:", resA.getSkills(), file=resumeTest)
    print("interests:", resA.getInterests(), file=resumeTest)
    print("blurb:", resA.getBlurb(), file=resumeTest)

    
    resumeTest.close()
    return resA


resA = main()
