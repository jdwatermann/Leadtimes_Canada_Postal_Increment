# Builders = JWatermann & WJohnson
# LastUpdated = 20171117

# LEAD_TIMES_CANADA zipcode Expansion

# Program needs CSV file containing Whse#, ZipFrom, ZipTo, Leadtime and ShipVia  (Updated portion1 with name of CSV file)

##########################################################################################################################################################################################################################################

# import the CSV file that contains the Lead_Times_Canada Table on DATAWSQL
# DictReader takes what is in the first row, and uses that as the fieldnames for storing in Dictionary.

import csv

fieldnames = {}
rows = []

with open('CAN_Zip6_Leadtime_TEST.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames
    
    for row in reader:
        rows.append(row)
    print('Total number of data rows:',((reader.line_num)-1))
print('Field names are: ' + ', '.join(field for field in fieldnames))

print('\nThe First 25 rows are:\n')
for row in rows[:25]:
    print(row,'\n')

##########################################################################################################################################################################################################################################

# Take the postal codes and apply a TYPE to each digit.  (Char or Int)
# Increment each character by the TYPE assigned.  If increment changes digit >=10 or 'A' then revert to fixed starting point (0 / A)

import string

ALPHA_LIST = list(string.ascii_uppercase)

class PostalCharDigit:
    
    def __init__(self,char):
        self.unit = char
        if char in ALPHA_LIST:
            self.type = "char"
        else:
            self.type = "int"

    def increment(self):
        old = self.unit
        if self.type == "int":
            temp_digit = int(self.unit)+1
            if temp_digit >= 10:
                self.unit = "0"
            else:
                self.unit=str(temp_digit)
            return temp_digit >= 10
        else:
            try:
                temp_digit = ALPHA_LIST[ALPHA_LIST.index(self.unit)+1]
            except IndexError:
                temp_digit = 'A'
            self.unit = temp_digit
            return temp_digit == 'A'

    def __str__(self):
        return self.unit

##########################################################################################################################################################################################################################################

class PostalCode:
    
    def __init__(self,postal):
        
        self.text = postal
        self.list = [PostalCharDigit(x) for x in list(postal)]
# Checking the length and types of each digit in the postal code, if not correct provide an error.
        if len(postal)!= 6:
            raise ValueError
        if self.list[0].type != 'char':
            raise ValueError
        if self.list[1].type != 'int':
            raise ValueError
        if self.list[2].type != 'char':
            raise ValueError
        if self.list[3].type != 'int':
            raise ValueError
        if self.list[4].type != 'char':
            raise ValueError
        if self.list[5].type != 'int':
            raise ValueError
# Checking the if the first character is equal to D,F,I,O,Q,U,W,Z;  if so provide an error.
# Postal codes in Canada cannot start with those Letters.
        if postal.startswith('D'):
            raise ValueError
        if postal.startswith('F'):
            raise ValueError
        if postal.startswith('I'):
            raise ValueError
        if postal.startswith('O'):
            raise ValueError
        if postal.startswith('Q'):
            raise ValueError
        if postal.startswith('U'):
            raise ValueError
        if postal.startswith('W'):
            raise ValueError
        if postal.startswith('Z'):
            raise ValueError       
        
    def value(self):
        return ''.join([str(each) for each in self.list])

    def increment(self):
        moveNextUnit = self.list[5].increment()
        remaining_digits = list(range(0,5))
        remaining_digits.reverse()
        for unit in remaining_digits:
            if moveNextUnit:
                moveNextUnit = self.list[unit].increment()
    
    def __str__(self):
        return self.text
    
    def __repr__(self):   #format change for better viewing
        return self.value()

##########################################################################################################################################################################################################################################

# Loop thru the postal codes given until reach 'end' postal code.
# Write the results to a CSV file.

def postalLoop(start, end, leadtime, warehouse, shipvia, csvfile):
    try:     #If the zipcode is not a length of 6 OR in the proper L#L#L# format, do not use that line.
        fromZipCode = PostalCode(start)
        toZipCode = PostalCode(end)
        
        while (toZipCode.value() >= fromZipCode.value()):
            csvfile.writerow([fromZipCode.value(), str(leadtime), str(warehouse), str(shipvia)])
            fromZipCode.increment()
    
    except ValueError:   #print out the bad lines found.
        print('Either ZipFrom:', start, ' or ', 'ZipTo:', end, 'has bad data found')

##########################################################################################################################################################################################################################################

# Execute loop from the input CSV File.

import csv
with open('CAN_Zip6_Leadtime_Expanded.csv', 'w', newline='') as output:  
# 'w' means we are writing to this file, will create the book.  If already created, will override with new data.
    wtr = csv.writer(output)
    wtr.writerow(['Zipcode','Leadtime','Warehouse','ShipVia']) #create Header
    for field in rows:
        postalLoop((field.get('ZipFrom')),(field.get('ZipTo')),(field.get('Leadtime')),(field.get('Whse#')),(field.get('ShipVia')),wtr)


##########################################################################################################################################################################################################################################

# Check the EXPANDED output file created, to verify if zips are in valid length and format.
# If NOT, then write to a new BAD_DATA CSV.
# If valid, then write to FINAL_DATA CSV.

import re
import csv

field_names = {}
data = []

with open('CAN_Zip6_Leadtime_Expanded.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    filed_names = reader.fieldnames
    
    for row in reader:
        data.append(row)


with open('CAN_FINAL_DATA.csv', 'w', newline='') as finaloutput:  
# 'w' means we are writing to this file, will create the book.  If already created, will override with new data.
    finaldata = csv.writer(finaloutput)
    finaldata.writerow(['Zipcode','Leadtime','Warehouse','ShipVia']) #create Header
    
    with open('CAN_BAD_DATA.csv', 'w', newline='') as badoutput:  
        baddata = csv.writer(badoutput)
        baddata.writerow(['Zipcode','Leadtime','Warehouse','ShipVia']) #create Header
    
        for field in data:

            zipcodeinput = field.get('Zipcode')
            zipcode = zipcodeinput.strip().upper()
            
            # Canadian postal codes cannot contain the letters: D,F,I,O,Q,U in any Alpha position.  Also 1st Alpha position cannot contain W or Z.   
            while(True):
                if len(zipcode) == 6:   #MOVE THIS CHECK TO POSTALCODE SEGEMENT?
                    stuff1 = re.match('([ABCEGHJKLMNPRSTVXY][0-9][ABCEGHJKLMNPRSTVWXYZ][0-9][ABCEGHJKLMNPRSTVWXYZ][0-9])', zipcode)
                    if stuff1 is None:   #if 'null' will continue to indented line.  If populated, moves to ELSE statement.
                        baddata.writerow([(field.get('Zipcode')), (field.get('Leadtime')),(field.get('Warehouse')),(field.get('ShipVia'))])
                        break
                    else:
                        finaldata.writerow([(field.get('Zipcode')), (field.get('Leadtime')),(field.get('Warehouse')),(field.get('ShipVia'))])
                        break
                else:
                    baddata.writerow([(field.get('Zipcode')), (field.get('Leadtime')),(field.get('Warehouse')),(field.get('ShipVia'))])
                    break
                break

##########################################################################################################################################################################################################################################

# This area is used to count the FINAL file.
# This will indicate the program has finished running

import csv

fieldnames = {}
rows = []

with open('CAN_FINAL_DATA.csv', 'r') as finalfile:
    reader = csv.DictReader(finalfile)
    fieldnames = reader.fieldnames
    
    for row in reader:
        rows.append(row)
    print('Total number of data rows:', ((reader.line_num)-1),'\n')
print('Field names are: ' + ', '.join(field for field in fieldnames))