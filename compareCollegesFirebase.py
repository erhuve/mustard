import pyrebase
import pandas as pd
import os
from scraper import read_data
import numpy as np
import json


config = {
        "apiKey": os.environ.get("APIKEY"),
        "authDomain": os.environ.get("AUTHDOMAIN"),
        "databaseURL": os.environ.get("DATABASEURL"),
        "projectId": os.environ.get("PROJECTID"),
        "storageBucket": os.environ.get("STORAGEBUCKET"),
        "messagingSenderId": os.environ.get("MESSAGINGSENDERID"),
        "appId": os.environ.get("APPID"),
        "measurementId": os.environ.get("MEASUREMENTID"),
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

def getAllCollegeDicts():
    collegeDicts = []
    allDicts = db.child("colleges").get()
    #print(f"Length of dictionaries is {len(allDicts)}")
    for college in allDicts.each():
        #print(F"College Key: {college.key()}, College Value: {college.val()}, type of college value: {type(college.val())}")
        keys = college.val().keys()
        for key in keys:
            collegeDicts.append(college.val()[key])
            break
    #print(f"Length of first entry is {len(collegeDicts[0])}")
    return collegeDicts
#getAllCollegeDicts()
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

def calculate(listcollegesDict, field, salary, cost, diversity, size, urbanicity, public):
    collegeScores = []
    for collegeDict in listcollegesDict:
        if collegeDict['salary'] == 0 or collegeDict['avg_cost'] == '[]' or type(collegeDict['avg_cost']) is list:
            collegeScores.append(['We don\'t have enough information to score this college for you' for i in range(7)])
            continue
        diversityScore = (5.0 - np.std(np.array(collegeDict["diversity"]) / 6.28))
        costScore = min(6 - float(collegeDict["avg_cost"]) / float(cost), 5)
        publicScore = 0
        if collegeDict["public"] in public:
            publicScore = 1
        collegeSize = collegeDict["size"]
        sizeScore = 0
        if collegeSize in size:
            sizeScore = 1
        salary_score = min(float(collegeDict['salary']) / float(salary) * 5, 5)
        urban_score = 0
        if collegeDict['location_type'] in urbanicity:
            urban_score += 1
        field_score = 0
        for rank, study in enumerate(collegeDict['fields']):
            if study == field:
                field_score = max(10 - rank, 0)
        collegeScores.append([field_score, salary_score, costScore, diversityScore, sizeScore, urban_score, publicScore])
    return collegeScores
	    
def getAllScoresForColleges(college1, college2, field, salary, cost, diversity, size, urbanicity, public):
    college1Dict = getDataForCollege(college1)
    college2Dict = getDataForCollege(college2)
    scores = calculate([college1Dict, college2Dict], field, salary, cost, diversity, size, urbanicity, public)
    return scores

def coldRecommend(college_list, no_recs, field, salary, cost, diversity, size, urbanicity, public):
    filtered = []
    for college in college_list:
        # This will ensure size, urbanicity, public/private match,
        # and that there is existing cost and salary data
        if type(college['avg_cost']) is not list and type(college['salary']) is not list and college['salary'] > 0 and college['size'] in size and college['location_type'] in urbanicity and college['public'] in public:
            filtered.append(college)
    # Map list for calculating
    indices = {}
    for i, college in enumerate(filtered):
        indices[i] = college['name']
    scores = calculate(filtered, field, salary, cost, diversity, size, urbanicity, public)
    for i in range(len(scores)):
        scores[i] = np.sum(scores[i])
    no_recs = min(no_recs, len(scores) - 1)
    recs = np.argpartition(scores, -no_recs)[no_recs:]
    recs_final = []
    for index in recs:
        recs_final.append(indices[index])
        
    return recs_final

def getUniqueMajors():
    if not os.path.exists("unique_majors.json"):
        allDicts = getAllCollegeDicts()
        fieldsOfStudy = []
        for collegeDict in allDicts:
            if "fields" in collegeDict.keys():
                for fields in collegeDict["fields"]:
                    fieldsOfStudy.append(fields)
        setOfFields = list(set(fieldsOfStudy))
        jsonDict = {"Unique Fields": list(setOfFields)}
        with open("unique_majors.json", 'w') as f:
            json.dump(jsonDict, f)
            f.close()
    else:
        print("Loading data from file")
        setOfFields = []
        with open("unique_majors.json") as f:
            data = json.load(f)
            setOfFields = data["Unique Fields"]
    return setOfFields
#print(len(getUniqueMajors()))
#print(diversityScore("Massachusetts Institute of Technology"))
#print(costScore("Massachusetts Institute of Technology", 12000))
#print(publicScore("Massachusetts Institute of Technology", ["Public", "Private"]))
#print(sizeScore("Massachusetts Institute of Technology", ["Small", "Medium"]))
# print(getAllScoresForColleges("Stanford University", "Massachusetts Institute of Technology", "Computer Science - Bachelor's Degree", 100000, 20000, True, ["Small"], ["Suburban"], ["Public"]))
