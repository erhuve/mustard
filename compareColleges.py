# import argparse
import pandas as pd
import os
from selenium import webdriver
from scraper import read_data
import numpy as np
'''
# Testing

ap = argparse.ArgumentParser()

ap.add_argument("-c1", "--college", help = "First College to compare")
ap.add_argument("-c2", "--compare", help = "Second College to compare")
ap.add_argument("-d", "--driver", help = "Path to Selenium Driver")

args = vars(ap.parse_args())


DRIVER_PATH = args["driver"]

firstCollege = args["college"]
secondCollege = args["compare"]
'''
def compare(firstCollege, secondCollege = "Indiana Institute of Technology", DRIVER_PATH = 'chromedriver', returnDf = False):
    dataFirst = {}
    dataSecond = {}
    initdfLength = 0
    if not os.path.exists("college_db.csv"):
        print("Path doesn't exist")
        dataFirst = read_data(firstCollege, DRIVER_PATH)
        dataSecond = read_data(secondCollege, DRIVER_PATH)
        df = pd.DataFrame([dataFirst, dataSecond])
        #df = df.append(dataFirst, ignore_index = True)
        #df = df.append(dataSecond, ignore_index = True)
        df = df.T
        df.to_csv('college_db.csv')
        initdfLength = len(df)
        return df
    else:
        df = pd.read_csv("college_db.csv")
        # print(df)
        df = df.T
        headers = df.iloc[0]
        df  = pd.DataFrame(df.values[1:], columns = headers)
        initdfLength = len(df)
        if len(df[df['name'] == firstCollege]) == 0:
            print("Dataframe found but college not found")
            dataFirst = read_data(firstCollege, DRIVER_PATH)
            df = df.append(dataFirst, ignore_index = True)
        else:
            dataFirst = df[df["name"] == firstCollege].iloc[0].to_dict()
        if len(df[df['name'] == secondCollege]) == 0:
            dataSecond = read_data(secondCollege, DRIVER_PATH)
            df = df.append(dataSecond, ignore_index = True)
        else:
            dataSecond = df[df["name"] == secondCollege].iloc[0].to_dict()
    df = df.T
    #print(f"First college data is {dataFirst}")
    #print(f"Second college data is {dataSecond}")
    #compare_colleges(dataFirst, dataSecond)
    if len(df) > initdfLength:
        df.to_csv('college_db.csv')
    if returnDf:
        return df
    else:
        return [dataFirst, dataSecond]


#print(compare("Stanford University", "University of Southern California", returnDf = True))


def convertStringToListNums(string):
    if(type(string) is list):
        return string
    string = string[1: len(string) - 1].replace(" ", "")
    string_list = string.split(",")
    map_object = map(int, string_list)
    return list(map_object)


def diversityScore(college):
    return (5.0 - np.std(np.array(convertStringToListNums(compare(college)[0]["diversity"]))) / 6.28)


def costScore(college, preference):
    return min(6 - float(float(compare(college)[0]["avg_cost"]) / preference), 5)

def publicScore(college, preferences):
    if compare(college)[0]["public"] in preferences:
        return 1
    return 0

def sizeScore(college, preferences):
    if compare(college)[0]["size"] in preferences:
        return 1
    return 0

print(diversityScore("University of Washington-Seattle Campus"))
print(costScore("University of Washington-Seattle Campus", 12000))
print(publicScore("University of Washington-Seattle Campus", ["Public", "Private"]))
print(sizeScore("University of Washington-Seattle Campus", ["Small", "Medium", "Large"]))
