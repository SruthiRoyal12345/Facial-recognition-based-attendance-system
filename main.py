import cv2
import numpy as np
import face_recognition
import os
import time
import mysql.connector as ms


mydb = ms.connect(host="localhost", user="mimir", passwd="Mrin@l123")

cursorObject = mydb.cursor()

cursorObject.execute("use attendance;")

am ={}

path = "./img_lear"
image = []
className = []
mylist = os.listdir(path)
for cls in mylist:
    curImg = cv2.imread(f'{path}/{cls}')
    image.append(curImg)
    className.append(os.path.splitext(cls)[0])
    am[os.path.splitext(cls)[0]] = 0
    mydb.commit()

cursorObject.close()



def findEncodings(images):
	encodeList = []
	for img in images:
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		enode = face_recognition.face_encodings(img)[0]
		encodeList.append(enode)

	return encodeList



def main():
    encodeListKnown = findEncodings(image)
    print('Encoding Complete')
    cap = cv2.VideoCapture(0)
    mydb1 = ms.connect(host="localhost", user="mimir", passwd="Mrin@l123")
    cursorObject1 = mydb1.cursor()
    cursorObject1.execute("use attendance;")
    tim = time.localtime()

    while True:
        # tim.tm_hour > 14 and tim.tm_hour < 24
        if True:
            sucess, img = cap.read()
            imgS = cv2.resize(img,(0,0),None,0.25,0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)


            for encodeFace,faceLoc in zip(encodesCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                print (faceDis)
                
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    na=className[matchIndex]
                    name = className[matchIndex].upper()
                    if am[na]==0: 
                        se="update `%s` set `%s`=\"1\" where name=\"%s\";"
                        cursorObject1.execute(se%(tim.tm_mon,tim.tm_mday,name))
                        mydb1.commit()
                        am[name]=1
                    y1,x2,y2,x1 = faceLoc
                    y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img, (x1,y1), (x2,y2),(0,255,0),2)
                    cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)


                cv2.imshow('Webcam', img)
                cv2.waitKey(1)

            else:
                cv2.putText(img,"attendance over",(0,0),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

        else :
            for i in am:
                am[i]=0



if __name__ == "__main__":
    main()
