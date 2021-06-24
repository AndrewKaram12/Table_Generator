import csv
from hashlib import new
import io
import random
import argparse
from datetime import datetime
import boto3
from Universal_Methods.app.universal import *
from Appointments_Table.app.generator import appointments_data_maker

NUMBER_OF_ANOMALIES = 7 #The number of potential anomalies
ID_START = 10000 #Represents  the start of the ID count

parser = argparse.ArgumentParser()

#represents a row object
class Table_row:
    #initializes row's fields
    def __init__(self, id):
        self.id = id
        self.age = get_age()
        self.sex = get_sex()
        self.name = get_name(self.sex)
        self.pregnant = get_pregnancy(self.sex, self.age)
        self.working = get_work_status(self.age)
        self.distance = get_distance()
        self.first_visit = get_first_visit(self.age)
        self.last_visit = get_last_visit(self.first_visit, True)
        self.co_pay = get_co_pay(self.first_visit, self.last_visit)
        self.anomaly = "None"
    
    #updates the given row for an anomaly (acts as a switch case)
    def row_anomaly(self, num):
        #represents an age anomaly where the age is clearly out of range
        if (num == 1):
            self.age = getRandomInt(MAX_AGE + 1, 1000)
            self.anomaly = "age"

        #represents a prenancy anomaly, where a male is pregnant, then update affected fields
        elif (num == 2):
            self.sex = "Male"
            self.pregnant = True
            self.name = get_name(self.sex)
            self.anomaly = "pregnant"

        #represents an illegal working age, then updates affect fields
        elif (num == 3):
            self.age = getRandomInt(1, MIN_WORKING_AGE-1)
            self.pregnant = get_pregnancy(self.sex, self.age)
            self.working = True
            self.first_vist = get_first_visit(self.age)
            self.last_visit = get_last_visit(self.first_vist, True)
            self.co_pay = get_co_pay(self.first_vist, self.last_visit)
            self.anomaly = "working age"

        #represents a distance anomaly
        elif (num == 4):
            self.distance = round(random.uniform(MAX_DISTANCE+1,MAX_ANOMALY_DISTANCE), 1)
            self.anomaly = "distance"

        #represents an inccorect last visit dates, then updates affected fields
        elif (num == 5):
            first_vist_temp = get_first_visit(self.age)
            last_visit_temp = get_last_visit(first_vist_temp, False)
            self.first_vist = last_visit_temp
            self.last_visit = first_vist_temp
            self.co_pay = get_co_pay(self.first_vist,self.last_visit)
            self.anomaly = "visits"

        #represents an inncorect copay amount
        elif(num == 6):
            p = getRandomInt(1,2)
            #two ways to anomalize the co_pay, one where the copayment is the min and the other where it is the max
            if (p == 1):
                co_pay_temp = getRandomInt(MIN_ANOMALY_CO_PAYMENT, CO_PAYMENT-1)
            else:
                co_pay_temp = getRandomInt(CO_PAYMENT + 1, MAX_ANOMALY_CO_PAYMENT)
            self.co_pay = co_pay_temp
            self.anomaly = "co_pay wrong"

        #represents an incorrect copay amount by applying a discount innapropriately
        elif (num == 7 ):
            last_visit_temp = get_last_visit(self.first_visit, False)
            co_pay_temp = CO_PAYMENT - (CO_PAYMENT *DISCOUNT)
            self.co_pay = co_pay_temp
            self.anomaly = "discount"

        else:
            print("Not A Valid Anomaly!")

    #returns the the instance variables in an list
    def get_row(self, show_bad_data):
        if show_bad_data:
            return [self.id, self.name, self.age, self.sex, self.pregnant, self.working, self.distance, self.first_visit.strftime("%m-%d-%Y"), self.last_visit.strftime("%m-%d-%Y"), self.co_pay, self.anomaly]
        else:
            return [self.id, self.name, self.age, self.sex, self.pregnant, self.working, self.distance, self.first_visit.strftime("%m-%d-%Y"), self.last_visit.strftime("%m-%d-%Y"), self.co_pay]

#creates a csv to a target, by taking the number of rows and the probability for an anomaly occuing
def patient_data_maker(target, row_count, probability, visible, appointment_probability):
    fieldnames = ["id", "name", "age", "sex", "pregnant", "working", "location_miles_away", "first_visit", "last_visit", "co_pay_for_checkup", "bad_data"]
    if not visible:
        fieldnames.remove("bad_data")
    id_list = list(range(ID_START,ID_START + row_count)) #generate a random ID from the given ID_START to row_count range
    random.shuffle(id_list) #shuffle the given ID list
    writer = csv.writer(target)
    writer.writerow(fieldnames)
    patient_list = []
    #creates given row count
    for i in range(1, row_count):
        new_row = Table_row(id_list[i-1]) #create a new row with the given ID

        #if the generated probaility is within range for the anomaly probability
        if (probability >= getRandomInt(1, MAX_PROBABILITY)):
            #generate a random anomaly from 1 to the number of anomalies
            anomaly = getRandomInt(1, NUMBER_OF_ANOMALIES)
            new_row.row_anomaly(anomaly)
            writer.writerow(new_row.get_row(visible))
            patient_list.append(new_row)
        else: 
            #write the unanomlized row to the target
            writer.writerow(new_row.get_row(visible))
            patient_list.append(new_row)
    appointments_data_maker(appointment_probability,visible, patient_list)

if __name__ == '__main__':
    print("Starting process...")
    filename = f"orders_{datetime.now().strftime('%Y%m%d')}.csv"
    print(f"Writing {filename}")
    parser.add_argument("--target")
    parser.add_argument("--rows", type = int)
    parser.add_argument("--patient_probability", type = int)
    parser.add_argument("--appointment_probability", type = int)
    parser.add_argument("--visible")
    parser.add_argument("--path")
    parser.add_argument("--bucket")
    args = parser.parse_args()
    print(f"Target: {args.target}")

    try:
        if args.target == "local":
            print(f"Path: {args.path}")
            if args.path:
                filename = args.path + "/" + filename
            file = open(filename, 'w', newline='')
            visible_bool = args.visible == "True"
            patient_data_maker(file, args.rows, args.patient_probability, visible_bool, args.appointment_probability)

        elif args.target == "s3":
            print(f"Bucket: {args.bucket}")
            s3_key = args.path + "/" + filename
            print(f"Path: {args.path}")
            source = io.StringIO()
            client = boto3.resource('s3')
            patient_data_maker(source)
            client.Bucket(args.bucket).put_object(Key=s3_key, Body=source.getvalue())
        
        print("OK!")

    except Exception as e:
        print("ERROR!")
        print(e)

'''
POSTGRES DDL
CREATE TABLE demo.orders (
    name varchar NULL,
    age numeric NULL,
    sex varchar NULL, 
    pregnant boolean NULL,
    profession varchar NUll,
    location_miles_away double NULL,
    first_visit date NULL,
    last_visit date NUll,
    co_pay_for_checkup double NULL,
    bad_data boolean NULL
    returned boolean NULL
);
'''
            #add normaly
                #name is done with generator
                #age - random
                #sex is random
                #if sex is male not pregant if sex is female and age is less 44 there is a 5.83 out of 100 chance she is pregant (random generator to decide)
                #working if there are less then 14 they are students otherwise they work
                #location_miles_away less then 5 - 30 this is a local doctors office
                #first visit random number generator thats takes the age and picks a random number from 1 to age using this it subtracts from current date and a subtracts (1-12 months )and picks a random day based on map
                #last visit random number generator every 1 in 20 have a chance of being brand new (if they are brandnew same first and last visit) if they are new same first_visit if not
                    #- take the first_date add  (1-12 months based on probability) to it then randomly picks a day of the given months possible days will add mapping for this
                #bad date is false