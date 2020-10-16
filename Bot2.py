import gspread
import datetime
import time
import cv2
import numpy as np
import face_recognition
import os
import csv

cap = cv2.VideoCapture(0)

gc = gspread.service_account(filename='service.json')
sh = gc.open_by_key('1WKj5jeVEsa0TA-sv7j_sGlcbZRNUgJJfgpk92SRPpKA')
worksheet = sh.worksheet("add_time")
worksheet2 = sh.worksheet("Class")
worksheet3 = sh.worksheet("check")

path = 'ImagesAttendance'
images = []
classNames = []

#list student
myList = os.listdir(path)
##print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
##print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print('Encoding Complete')

def find_people():
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            #print(name)
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            #print(name)
            #1print(type(name))
            cv2.imshow('Webcam',img)
            return name
    cv2.imshow('Webcam',img)
    return '0'

#get time function
def get_time_client():
    get_datetime = datetime.datetime.now()
    date = get_datetime.date()
    time = get_datetime.timetuple()
    year = time.tm_year
    month = time.tm_mon
    day = time.tm_mday
    hour = time.tm_hour
    minute = time.tm_min
    #print(type(minute))
    return year,month,day,hour,minute


#google sheet
def get_sheet_add_time():
    index_list = []
    
    try:
        row_false = worksheet.findall("False")
    except:
        return 0,0,0,0,0,0,0,0,0,0,0,0
    

    if(len(row_false) == 0):
        return 0,0,0,0,0,0,0,0,0,0,0,0
    try:
        
        for i in range(len(row_false)):
            value = row_false[i].row
            index_list.append(value)
        
        index_botton = min(index_list)
        index_of_region = row_false[0]
        row_reg = index_of_region.row
        col_reg = index_of_region.col
        
        print("check type")
        print(type(row_reg))
        data = worksheet.row_values(index_botton)
        ID = data[0]
        date = data[1]
        time_start = data[2]
        time_stop = data[3]
        IDs = data[4]
        status = data[5]
    
        #date from sheet
        year_sh = date[0:4]
        month_sh = date[5:7]
        day_sh = date[8:10]
    
        #time start
        hour_start = time_start[0:2]
        min_start = time_start[3:5]
        #time stop
        hour_stop = time_stop[0:2]
        min_stop = time_stop[3:5]
        #print(year)
        return ID,int(year_sh),int(month_sh),int(day_sh),int(hour_start),int(min_start),int(hour_stop),int(min_stop),IDs,status,row_reg,col_reg
    except:
        return 0,0,0,0,0,0,0,0,0,0,0,0
    
def update_cell(row_reg,col_reg):
    try:
        worksheet.update_cell(row_reg,col_reg, 'True')
    except:
        update_cell(row_reg,col_reg)
        
def find_student_in_class(IDs):
    student_list = []
    try:
        data_in_class = worksheet2.findall(str(IDs))    
        for index in range(len(data_in_class)):
            student_id = worksheet2.row_values(data_in_class[index].row)
            student_list.append(str(student_id[1]))
        return student_list
    except:
        find_student_in_class(IDs)
    


while True:
    #call get time
    year,month,day,hour,minute = get_time_client()    
    #data add time from sheet
    ID,year_sh,month_sh,day_sh,hour_start,min_start,hour_stop,min_stop,IDs,status,row_reg,col_reg = get_sheet_add_time()
    

    print(year,month,day,hour,minute)  
    
    print(ID,year_sh,month_sh,day_sh,hour_start,min_start,hour_stop,min_stop,IDs,status)
    
    if(year == year_sh and month == month_sh and day == day_sh):
        print("date")
        if(hour >= hour_start and minute >= min_start):
            #get id student from sheet <Class>
            print("..........................start ..........")
            student_list = find_student_in_class(IDs)
            id_checked = []
            id_checked_data = []
            id_send = []
            time_send = 0
            status_send = False
            #print("Hour")
            while True:
                if(hour >= hour_stop and minute >= min_stop):
                    print("..................stop......................")
                    update_cell(row_reg,col_reg)
                    
                    
                    try:
                        cv2.destroyWindow("Webcam")
                    except:
                        pass
                    
                    res = worksheet3.get_all_records()
                    index = len(res)+2
                    date_now = str(year)+"/"+str(month)+"/"+str(day)
                    for i in range(len(student_list)):
                        if student_list[i] not in id_checked:
                            print(student_list[i])
                            body = ["0",date_now,"-",IDs,student_list[i],"False"]
                            worksheet3.insert_row(body,index=index)
                            index = index + 1
                        else:
                            pass
                    break
                
                #time.sleep(1)
                year,month,day,hour,minute = get_time_client()
                print("Hello",hour,minute)
                id_student = find_people()
                if id_student != '0':
                    print(id_student)
                    print(id_student in student_list)
                    print(id_student not in student_list)
                    print(type(id_student))
                    print(student_list)
                    
                    
                if id_student in student_list and id_student not in id_checked:                    
                    status_send = True
                    date_now = str(year)+"/"+str(month)+"/"+str(day)
                    time_now = str(hour)+"/"+str(minute)
                    print(date_now,time_now,id_student)
                    body = ["0",date_now,time_now,IDs,id_student,"True"]
                    id_checked.append(id_student)
                    id_checked_data.append(body)
                    time_send = minute+2
                    if time_send > 59:
                        time_send = 1
                
                if minute == time_send and status_send == True:
                    status_send = False
                    print("Send data")
                    res = worksheet3.get_all_records()
                    index = len(res)+2                    
                    
                    for i in range(len(id_checked_data)):
                        data_student = id_checked_data[0]
                        worksheet3.insert_row(data_student,index=index)
                        del id_checked_data[0]
                        index = index + 1
                #res = worksheet.get_all_records()
                #index = len(res)+2
                #worksheet.insert_row(body,index=index)
                    
        else:
            print("None signal")
    else:
        print("None signal")
        
    
    #print(year,month,day,hour,minute)
    #print(ID,date,time_start,time_stop,IDs,status)
    time.sleep(1)
#google sheet
#gc = gspread.service_account(filename='service.json')
#sh = gc.open_by_key('1WKj5jeVEsa0TA-sv7j_sGlcbZRNUgJJfgpk92SRPpKA')
#worksheet = sh.worksheet("add_time")

#re = worksheet.findall("False")


#get time setting from sheet
#for i in range(len(re)):
    #print(i)
#    #print(re[i].col)
#    print(re[i].row)
#



# body = [5888,str(date),str(time)]
# res = worksheet.get_all_records()
# index = len(res)+2

# worksheet.insert_row(body,index=index)
