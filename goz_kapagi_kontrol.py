import cv2
from math import dist
import mediapipe as mp
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from datetime import datetime
import serial
arduino = serial.Serial("COM5", 9600)
cap = cv2.VideoCapture(0)
sol = [33, 160, 158, 133, 153, 144]
sag = [362, 385, 387, 263, 373, 380]
ear = 0.28
yuz = mp.solutions.face_mesh
yuzler = yuz.FaceMesh(max_num_faces = 1)
basla = None
durum = "Göz Algılanmadı"
renk = (0,0,255)
while True:
    ret, goruntu = cap.read()
    if not ret:
        break
    goruntu = cv2.flip(goruntu, 1)
    goruntu = cv2.resize(goruntu, (900, 700))
    yukseklik, genislik, _ = goruntu.shape
    rgb = cv2.cvtColor(goruntu, cv2.COLOR_BGR2RGB)
    algilama = yuzler.process(rgb)

    if algilama.multi_face_landmarks:
        yuz = algilama.multi_face_landmarks[0]
        solkordinat, sagkordinat = [], []
        for i in sol:
            x, y = int(yuz.landmark[i].x*genislik), int(yuz.landmark[i].y*yukseklik)
            solkordinat.append((x, y))
            cv2.circle(goruntu, (x,y), 2, (0,0,255), -1)
        pts = np.array(solkordinat, np.int32).reshape(-1,1,2)
        cv2.polylines(goruntu, [pts], True, (0,0,255),1)

        for i in sag:
            x, y = int(yuz.landmark[i].x*genislik), int(yuz.landmark[i].y*yukseklik)
            sagkordinat.append((x,y))
            cv2.circle(goruntu, (x,y), 2, (0,0,255), -1)
        pts = np.array(sagkordinat, np.int32).reshape(-1,1,2)
        cv2.polylines(goruntu, [pts], True, (0,0,255),1)

        soldikey1, soldikey2 = dist(solkordinat[1], solkordinat[5]), dist(solkordinat[2], solkordinat[4])
        sagdikey1, sagdikey2 = dist(sagkordinat[1], sagkordinat[5]), dist(sagkordinat[2], sagkordinat[4])
        solyatay, sagyatay = dist(solkordinat[0], solkordinat[3]), dist(sagkordinat[0], sagkordinat[3])

        sol_ear = (soldikey1+soldikey2)/(solyatay*2)
        sag_ear = (sagdikey1+sagdikey2)/(sagyatay*2)
        ort_ear = (sag_ear+sol_ear)/2

        if ort_ear < ear:
            if basla is None:
                basla = datetime.now()
            else:
                bitir = (datetime.now() - basla).total_seconds()
                if bitir > 1:
                    durum = "Göz Kapalı!"
                    renk = (255,0,0)
                    arduino.write(b"1")
                    basla = None
        else:
            durum = "Göz Açık"
            renk = (0,255,0)
            arduino.write(b"0")
            basla = None
    else:
        durum = "Göz Algılanmadı"
        renk = (0,0,255)
        arduino.write(b"0")
        ort_ear = 0

    font = ImageFont.truetype("opencv/goz kontrolu/fonts/CALIBRI.TTF", 32)
    pilgoruntu = Image.fromarray(cv2.cvtColor(goruntu, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pilgoruntu)
    draw.text((30, 40), durum + f" | Ear: {ort_ear:.2f}", font=font, fill=renk)
    goruntu = cv2.cvtColor(np.array(pilgoruntu), cv2.COLOR_RGB2BGR)
    
    cv2.imshow("Goz Takibi", goruntu)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
