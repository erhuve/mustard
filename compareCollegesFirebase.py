import pyrebase
import pandas as pd
import os
from scraper import read_data
import numpy as np

config = {
        "apiKey": "AIzaSyAiBxG429FT-kZj9tjpAjHlcIo6CDXed7s",
        "authDomain": "mustard-cba34.firebaseapp.com",
        "databaseURL": "https://mustard-cba34.firebaseio.com",
        "projectId": "mustard-cba34",
        "storageBucket": "mustard-cba34.appspot.com",
        "messagingSenderId": "445402188887",
        "appId": "1:445402188887:web:55ea85d4e7ab506a036712",
        "measurementId": "G-S34T7N2NN7"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()


#db.child("colleges").child("Georgia Tech").push({"name": "Georgia Institute of Technology-Main Campus"})

def getDataForCollege(college, DRIVER_PATH = 'chromedriver'):
    # For every college dictionary obtained from scaping the data will be inputted into firebase under the colleges node with the child being the name of the college
    collectDict = {}
    if not db.child("colleges").child(college).shallow().get().val():
        print("College does not exist in the firebase database")
        collegeDict = read_data(college, DRIVER_PATH)
        #print(collegeDictionary)
        db.child("colleges").child(college).push(collegeDict)       

    else:
        print("College exists in the database")
        collegeValue = db.child("colleges").child(college).get()
        #print(collegeValue)
        collegeDict = {}
        i = 0
        for x in collegeValue.each():
           collegeDict = dict(x.val())
           if i == 0:
               break
        #print(collegeDict)

    return collegeDict



#print(getDataForCollege("Massachusetts Institute of Technology"))

def diversityScore(college):
    return (5.0 - np.std(np.array(getDataForCollege(college)["diversity"])) / 6.28)

def costScore(college, preference):
    return min(6 - float(float(getDataForCollege(college)["avg_cost"]) / preference), 5)

def publicScore(college, preferences):
    if getDataForCollege(college)["public"] in preferences:
        return 1
    return 0

def sizeScore(college, preferences):
    size = getDataForCollege(college)["size"]
    #print(f"Size is {size}")
    if size in preferences:
        #print(getDataForCollege(college)["size"])
        return 1
    return 0

def calculate(colleges, field, salary, urbanicity):
    print(field)
    college_scores = []
    for college in colleges:
        field_score = 0

        if type(college['fields']) is list:
            for rank, study in enumerate(college['fields']):
                if study == field:
                    field_score = max(10 - rank, 0)
        else:      
            fields = college['fields'].replace('[','')
            fields = fields.replace(']','')
            fields = fields.split('",',)

            for rank, study in enumerate(fields):

                study = study.replace('"','')
                study = study.strip()

                if study == field:

                    field_score = max(10 - rank, 0)

        salary_score = min(float(college['salary']) / salary * 5, 5)

        urban_score = 0
        urbanicity = set(urbanicity)
        if college['location_type'] in urbanicity:
            urban_score += 1
        
        college_scores.append([field_score, salary_score, urban_score])
    return college_scores
#print(diversityScore("Stanford University"))
#print(costScore("Stanford University", 12000))
#print(publicScore("Stanford University", ["Public", "Private"]))
#print(sizeScore("Stanford University", ["Small", "Medium"]))




