# Grabs pdfs in a folder and base64 encodes them to add to an hl7 file defined by the csv file source

import base64
import pandas
import csv
import numpy
from dateutil import parser
from datetime import datetime

# Input/output path definitions
source_path = "PDF_PATH"
destination_path = "DESTINATION_FILE"
data_path = "CSV_PATH"

# Dataframe specific var definitions
colnames = next(csv.reader(open(data_path)))
# Assignment of the dataframe with its delimiters and column name definitions
df = pandas.read_csv(data_path, names=colnames, delimiter=",")
# Handles nan values
df = df.replace(numpy.nan, '', regex=True)

# Reverses traversal of df for troubleshooting
#df = df[::-1]

# Parent counter init
first = False

# Main loop that iterates over the dataframe rows
for index, row in df.iterrows():
    # Skips first row which is the headers
    if first == False:
        first = True
        continue

    try:
        # Assignment of values from dataframe       
        DocumentID = row['DocumentID']
        DocumentName = row['DocumentName']
        Organization = row['Organization']
        PatientMedicalRecordNumber = row['MRN']
        FirstName = row['FirstName']
        MiddleName = row['MiddleName']
        LastName = row['LastName']
        Gender = row['Gender']
        DateOfBirth = row['DOB']
        Address1 = row['Street']
        City = row['City']
        State = row['State']
        ZipCode = row['Zip']
        HomePhone = row['Phone']
        CreatedAt = row['CreatedAt']
        PDF = row['PDF']
        SSN = row['SSN']
        
        # Converts floats to a friendly value for time conversion
        def floatHourToTime(fh):
            h, r = divmod(fh, 1)
            m, r = divmod(r*60, 1)
            return (
                int(h),
                int(m),
                int(r*60),
            )

        # Converts a float to date
        def convertExcelDate(inputDate):
            try:
                # Toss out the decimal section because we don't care about the itme
                excel_date = int(inputDate.split(".")[0])
                dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(excel_date) - 2)
                hour, minute, second = floatHourToTime(excel_date % 1)
                dt = dt.replace(hour=hour, minute=minute, second=second)
            except Exception as e:
                # If it fails then just make it blank
                dt = ""
            return dt
    
        # Date/time conversions. This assumes the source dates are excel decimals
        CreatedAt = parser.parse(str(convertExcelDate(CreatedAt))).strftime('%Y%m%d%H%M%S')
        DateOfBirth = parser.parse(str(convertExcelDate(DateOfBirth))).strftime('%Y%m%d%H%M%S')
        
        try:
            # Open a PDF and convert to base64 with utf decoded to remove b' surrounding str
            with open(source_path+"\\"+PDF, "rb") as pdf_file:
                PDF_Encoded = base64.b64encode(pdf_file.read()).decode("utf-8")
        # If the pdf fails, we're interested in why so we dump the details out
        except Exception as e:
            print(source_path+"\\"+PDF)
            print(DocumentID +" Missing PDF")   
            
        # Init hl7 structure explicitely as str otherwise it's bytes. Add all the fields into their appropriate places
        base = str("MSH|^~\&||"+Organization+"|PCD||"+CreatedAt+"||MDM^T02||P|2.5\n"
        +"PID|||"+PatientMedicalRecordNumber+"||"+LastName+"^"+FirstName+"^"+MiddleName+"||"+DateOfBirth+"|"+Gender+"|||"+Address1+"^^"+City+"^"+State+"^"+ZipCode+"^^^||"+HomePhone+"||||||"+SSN+"|||||||||||||||||||||||||||||||||\n"
        +"TXA|1|^"+DocumentName+"|FT|"+CreatedAt+"|||||^MHC^Advanced Care Directives|||"+DocumentID+"||||Final|\n"
        +"OBX|1|ED|RPT^|1|SOURCESYSTEM^Image^PDF^Base64^"+PDF_Encoded+"||||||F\n")

        # Write to hl7 file
        hl7_file = open(destination_path+DocumentID+".hl7","w+")
        hl7_file.write(base)
        hl7_file.close()
        
        # Can be enabled/disabled to show live progress
        print("Finished " + DocumentID)
        
    # If there's a bad error we stop progress so that we can inspect
    except Exception as e:
        print(e)
        print(DocumentID)
        break
