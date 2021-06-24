from dateutil.relativedelta import relativedelta
import random
import argparse
import names
from datetime import datetime, timedelta

MAX_AGE = 122 #Represents the Max age to live top
MID_AGE = 70 #Repsents the minumn mid age to shoot for living for
MIN_WORKING_AGE = 14 #Represents the mininum working age in the state of maryland
MAX_DISTANCE = 31 #Represents a patient's maximum distance from doctors office before an anomaly
MAX_ANOMALY_DISTANCE = 2800 #Represents the max distance from facility if row is an anomaly
CO_PAYMENT = 50 #Represents typical co_payment amount
MAX_ANOMALY_CO_PAYMENT = 1000 #Represents the maximum co_payment amount if the row is an anomaly
MIN_ANOMALY_CO_PAYMENT = -50 #Represents the minum co_payment amount if the row is an anomaly
DISCOUNT = .15 #Represents the discount percent to subtract from a co_pay amount if the customer is new
MAX_PROBABILITY = 100 #Represents the general max probability
PROBABILITY_OF_MAX_AGE = 33 #Represents the probability of living 1 to the MAX_AGE
PROBABILITY_OF_MIN_AGE = MAX_PROBABILITY - PROBABILITY_OF_MAX_AGE #The remaing probabiltiy represents the prob of living 1 to MID_AGE
MAX_PREGNANCY_AGE = 52 #Represents the maximum age of being pregnant as a female
MIN_PREGNANCY_AGE = 12 #Represents the mininum age of being pregnant as a female
PROBABILITY_PREGNANT= 6 #Represents the probability of being pregnant out of a hundred
MAX_WORKING_AGE = 65 #Represents the typical maximum working age
PROBABILITY_OLD_WORKING = 20 #Represents The probability of working when older than the MAX_WORKING_AGE
PROBABILITY_WORKING = 80 #Represents the probability of working when within age range of Min and Max Working Age
PROBABILITY_NEW_PATIENT = 10 #The probability of the patient being new

parser = argparse.ArgumentParser()

#returns a random number inclusively from min to max
def getRandomInt(min,max):
  return random.randint(min, max)
  
#returns a random name based on sex
def get_name(sex):
     return names.get_first_name(gender=sex.lower())

#returns a random age
def get_age():
    p = getRandomInt(1, MAX_PROBABILITY)
    #if p represents that someone's age can be within range
    #from 1 to the max age then allow it else make it to the mid age
    if (p <= PROBABILITY_OF_MAX_AGE):
        return getRandomInt(0, MAX_AGE)
    else:
        return getRandomInt(0, MID_AGE)

#returns sex
def get_sex():
    p = getRandomInt(1,2)
    if (p == 1):
        return "Male"
    else:
        return "Female"

#returns pregnancy status
def get_pregnancy(sex, age):
    if (sex == "Male"):
        return False
    else:
        #if the given age is within range to be pregnant
        if (age >= MIN_PREGNANCY_AGE and age <= MAX_PREGNANCY_AGE):
            #assign the probability of being pregnant to dictate the status
            p = getRandomInt(1, MAX_PROBABILITY)
            return (p <= PROBABILITY_PREGNANT)
        else:
            return False

#returns work status
def get_work_status(age):
    #if person's age is within the typical range of working
    if (age >= MIN_WORKING_AGE and age < MAX_WORKING_AGE):
        #return the probability of them working
        p = getRandomInt(PROBABILITY_WORKING, MAX_PROBABILITY)
        return (p <= PROBABILITY_WORKING)
    #if the person's age is above the typical working age
    elif (age >= MAX_WORKING_AGE):
        #return the probability of that person working
        p = getRandomInt(PROBABILITY_OLD_WORKING, MAX_PROBABILITY)
        return (p <= PROBABILITY_OLD_WORKING)
    else:
        return False

#returns the distance
def get_distance():
    #returns a random distance from the given range with 1 decimal place over
    return round(random.uniform(1,MAX_DISTANCE), 1)

#returns the first visit date
def get_first_visit(age):
    #picks a random number from the person's age and multiplies by days in a year
    day_difference = age * 365
    current_time = datetime.now()

    if (age > 1):
        #pick a random number of days from to the difference calculation
        random_day_difference = getRandomInt(1, day_difference)
        #subtract those given days to the current time
        return_date = current_time - timedelta(days = random_day_difference )
        return return_date
    else:
        #in the case where a person is less than one years old we can pick a random day from 365 days
        random_day_difference = getRandomInt(1,365)
        #subtract those days from the current time
        return_date = current_time - timedelta(days = random_day_difference )
        return return_date

#returns the last_visit date
def get_last_visit(first_visit, consider_new_patient):
    #p represents the probability that the patient is new
    p = getRandomInt(PROBABILITY_NEW_PATIENT ,MAX_PROBABILITY)
    #if the probability and paramter deems it true then return the first_visit date
    if (p <= PROBABILITY_NEW_PATIENT and consider_new_patient == True):
        return first_visit
    else:
        current_year = datetime.now().year
        #calculate the year difference from the current year to the first_visit and find the possible future days
        day_difference = (current_year - first_visit.year) * 365
        #if the generated day is the same year as the first visit make day_difference 365 days
        if (day_difference == 0):
            day_difference = 365
        #randomly pick a day from the year difference rage
        random_day_difference = getRandomInt(1, day_difference)
        #add the given time to the first_visit 
        return_date = first_visit + timedelta(days = random_day_difference )
        return return_date

#returns the copay amount
def get_co_pay(first_visit, last_visit):
    #if the first and last visit are equal the discount is applie
    if (first_visit == last_visit):
        return CO_PAYMENT - (CO_PAYMENT * DISCOUNT)
    else:
        return CO_PAYMENT