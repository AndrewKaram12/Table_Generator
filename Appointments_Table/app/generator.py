import csv
import io
import random
import argparse
import math
from datetime import datetime
from Universal_Methods.app.universal import *


NUMBER_OF_ANOMALIES = 3 #The number of potential anomalies
ID_START = 10000 #Represents the start of the ID count
OLDER_EXAM_AGE_MIN = 55
NEW_BORN_EXAM_AGE_MAX = 3

#Appointments seperated on stages of age and sex, these are our overall rules
MALE_APPOINTMENTS_CHECKS = ["Prostate Exam", "Testiular Cancer Exam" ]
FEMALE_APPOINTMENTS_CHECKS = ["Mammogram", "Pelvic Exam", "Pap Smear", "Prenatal Test", "HPV Test"]
PREGNANCY_APPOINTMENTS_CHECKS = ["Ultra Sound Exam", "Feturs Measurements", "Prental Vitamin Screening", ]
NEW_BORN_APPOINTMENTS_CHECKS = ["Phenylketonuria", "Congenital Hypothyroidism Exam" , "Galactosemia Exam", "Sickle Cell Exam", "Maple Syrup Urine Examination", "Homocystinuria Exam", "Biotinidase Deficiency Check" , "Congenital adrenal hyperplasia Screening", "Medium chain acyl-CoA dehydrogenase deficiency (MCAD)", "Hearing Exam", "Eye Exam"]
ADULT_APPOINTMENTS_CHECKS = ["Blood Pressure Screening", "Cholesterol Screening", "HIV Test", "Skin Examination", "Vaccination", "Physical" , "Check Up"]
ELDER_APPOINTMENTS_CHECKS = ["Colorectal Cancer Screening", "Abdominal Aortic Aneurysm Screening", "Thryoid Hormone Test", "Dental Exam"]
MALE_APPOINTMENTS_NUM_MAX = math.ceil((len(MALE_APPOINTMENTS_CHECKS)/2)) #Represents the max number of male appointments to take
FEMALE_APPOINTMENTS_NUM_MAX = math.ceil((len(FEMALE_APPOINTMENTS_CHECKS)/2)) #Represents the max number of female appointments to take
PREGNANCY_APPOINTMENTS_NUM_MAX = math.ceil((len(PREGNANCY_APPOINTMENTS_CHECKS)/2)) #Represents the max number of pregnancy appointments to take
ELDER_APPOINTMENTS_NUM_MAX = math.ceil((len(ELDER_APPOINTMENTS_CHECKS)/2)) #Represents the max number of elder appointments to take
ADULT_APPOINTMENTS_NUM_MAX = math.ceil((len(ADULT_APPOINTMENTS_CHECKS)/2)) #Represents the max number of adults appointments to take
NEW_BORN_APPOINTMENTS_NUM_MAX = math.ceil((len(NEW_BORN_APPOINTMENTS_CHECKS)/2)) #Represents the max number of new_born appointments to take

parser = argparse.ArgumentParser()

def get_appointments(sex, age, pregnant):
    appointments = []
    #if you are consider an older person randomly take on Elder appointments, Adult Appointments and sex based appointments
    if (age > OLDER_EXAM_AGE_MIN):
        appointments.extend(random.sample(ELDER_APPOINTMENTS_CHECKS, getRandomInt(0, ELDER_APPOINTMENTS_NUM_MAX)))
        appointments.extend(random.sample(ADULT_APPOINTMENTS_CHECKS, getRandomInt(0, ADULT_APPOINTMENTS_NUM_MAX)))
        if(sex == "Male"):
            appointments.extend(random.sample(MALE_APPOINTMENTS_CHECKS, getRandomInt(0, MALE_APPOINTMENTS_NUM_MAX )))
        else: 
            appointments.extend(random.sample(FEMALE_APPOINTMENTS_CHECKS, getRandomInt(0, FEMALE_APPOINTMENTS_NUM_MAX)))
        return appointments

    #if you are older than three (Adult based appointments) randomly take on Adult Appointments and sex based appointments
    elif(age > 3):
        appointments.extend(random.sample(ADULT_APPOINTMENTS_CHECKS, getRandomInt(0, ADULT_APPOINTMENTS_NUM_MAX)))
        if(sex == "Male"):
            appointments.extend(random.sample(MALE_APPOINTMENTS_CHECKS, getRandomInt(0, MALE_APPOINTMENTS_NUM_MAX)))
        else: 
            appointments.extend(random.sample(FEMALE_APPOINTMENTS_CHECKS, getRandomInt(0, FEMALE_APPOINTMENTS_NUM_MAX)))
            if(age > 12 and pregnant):
                appointments.extend(random.sample(PREGNANCY_APPOINTMENTS_CHECKS, getRandomInt(1, PREGNANCY_APPOINTMENTS_NUM_MAX)))
        return appointments
    #if you are consider a new born, younger than three randomly take on new born based appointments
    else:
        appointments.extend(random.sample(NEW_BORN_APPOINTMENTS_CHECKS, getRandomInt(1, NEW_BORN_APPOINTMENTS_NUM_MAX)))
        return appointments

#represents a row object
class Table_row:
    #initializes row's fields
    def __init__(self, id, age, sex, name, pregnant):
        self.id = id
        self.age = age
        self.sex = sex
        self.name = name
        self.pregnant = pregnant
        self.appointments = get_appointments(self.sex, self.age, self.pregnant)
        self.anomaly = "None"
    
    #updates the given row for an anomaly (acts as a switch case)
    def row_anomaly(self, anomaly_num):
        num = anomaly_num
        #represents an innapropriate age-based appointment
        if (num == 1 and self.age <=3):
            self.appointments.extend(random.sample(ELDER_APPOINTMENTS_CHECKS, 1))
            self.anomaly = "Wrong Age Based Appointments"
        elif (num == 1):
             self.appointments.extend(random.sample(NEW_BORN_APPOINTMENTS_CHECKS, 1))
             self.anomaly = "Wrong Age Based Appointments"

        #represents an innapropriate sex-based appointment
        elif (num == 2 and self.sex == "Male"):
            self.appointments.extend(random.sample(FEMALE_APPOINTMENTS_CHECKS, 1))
            self.anomaly = "Wrong Sex-Based Appointments"
        
        elif(num == 2 and self.sex == "Female"):
            self.appointments.extend(random.sample(MALE_APPOINTMENTS_CHECKS, 1))
            self.anomaly = "Wrong Sex-Based Appointments"

        #represents an innapropriate pregnancy-based appointment or gives a pregnant women none.
        elif (num == 3 and self.pregnant == False):
            self.appointments.extend(random.sample(PREGNANCY_APPOINTMENTS_CHECKS, 1))
            self.anomaly = "Wrong Pregnant-Based Appointments"

        elif(num == 3 and self.pregnant == True):
            for element in self.appointments:
                if element in PREGNANCY_APPOINTMENTS_CHECKS:
                    self.appointments.remove(element)
            self.anomaly = "Wrong Pregnant-Based Appointments"
        else:
            print("Not A Valid Anomaly!")
        
    def get_row(self, show_bad_data):
        if show_bad_data:
            return [self.id, self.name, self.age, self.sex, self.pregnant, self.appointments, self.anomaly]
        else:
            return [self.id, self.name, self.age, self.sex, self.pregnant, self.appointments]


def appointments_data_maker(probability, visible, patients):
    filename = f"Appointments_{datetime.now().strftime('%Y%m%d')}.csv"
    target = open(filename, 'w', newline='')
    #generates field names
    fieldnames = ["id", "name", "age", "sex", "pregnant", "Reason for appointment", "bad_data"]
    #handles the flag case where the titled bad anomalies are not shown
    if not visible:
        fieldnames.remove("bad_data")
    writer = csv.writer(target)
    writer.writerow(fieldnames)
    #loop through patients from Patient_Table
    for patient in patients:
        new_row = Table_row(patient.id, patient.age, patient.sex, patient.name, patient.pregnant)
        #if the generated probaility is within range for the anomaly probability
        if (probability >= getRandomInt(1, MAX_PROBABILITY)):
            #generate a random anomaly from 1 to the number of anomalies
            anomaly = getRandomInt(1, NUMBER_OF_ANOMALIES)

            if (anomaly <= NUMBER_OF_ANOMALIES):
                #anomalize the row
                new_row.row_anomaly(anomaly)

            writer.writerow(new_row.get_row(visible))
        else: 
            #write the unanomlized row to the target
            writer.writerow(new_row.get_row(visible))

'''#creates a csv to a target, by taking the number of rows and the probability for an anomaly occuing
def data_maker(target, row_count, probability, visible):
    fieldnames = ["id", "name", "age", "sex", "pregnant", "Reason for appointment", "bad_data"]
    if not visible:
        fieldnames.remove("bad_data")
    id_list = list(range(ID_START,ID_START + row_count)) #generate a random ID from the given ID_START to row_count range
    random.shuffle(id_list) #shuffle the given ID list
    writer = csv.writer(target)
    writer.writerow(fieldnames)
    #creates given row count
    for i in range(1, row_count):
        temp_sex = get_sex()
        temp_age = get_age()
        new_row = Table_row(id_list[i-1], temp_age, temp_sex, get_name(temp_sex), get_pregnancy(temp_sex, temp_age)) #create a new row with the given ID

        #if the generated probaility is within range for the anomaly probability
        if (probability >= getRandomInt(1, MAX_PROBABILITY)):
            #generate a random anomaly from 1 to the number of anomalies
            anomaly = getRandomInt(1, NUMBER_OF_ANOMALIES)

            if (anomaly <= NUMBER_OF_ANOMALIES -1):
                #anomalize the row
                new_row.row_anomaly(anomaly)

            writer.writerow(new_row.get_row(visible))
        else: 
            #write the unanomlized row to the target
            writer.writerow(new_row.get_row(visible))'''