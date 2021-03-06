import cv2
import numpy as np
import math
import os
import numpy as np
import util as ut
import svm_train as st 
import re
from picamera.array import PiRGBArray
from picamera import PiCamera
import io, time

print("Opening ASL Model!")
try:
    direct = cwd + "/ASLClassifier.dat"
    print(direct)
    model=st.load(direct)
    print("SVM Loaded successfully..")
except:
    model=st.trainSVM(17)
    
camera=PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)
font = cv2.FONT_HERSHEY_SIMPLEX
text= " "

temp=0
previouslabel=None 
previousText=" "
label = None 
    
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True): # Capture pi camera frames
    stream = frame.array # store frame input as array
    rawCapture.truncate(0) # take optional size
    img=stream # store stream as temp img
    cv2.rectangle(img, (300,300), (100,100), (0,255,0),0) # create rectangle one screen
    img1 = img[100:300, 100:300] # image stream ratio
    img_ycrcb = cv2.cvtColor(img1, cv2.COLOR_BGR2YCR_CB) # color format settings
    blur = cv2.GaussianBlur(img_ycrcb,(11,11),0) # Gaussian blur added to screen helps deal with frams quality and performance
    skin_ycrcb_min = np.array((0, 138, 67)) # color spaces min
    skin_ycrcb_max = np.array((255, 173, 133)) # color spaces max
    mask = cv2.inRange(blur, skin_ycrcb_min, skin_ycrcb_max)  # detecting the hand in the bounding box using skin detection
    contours,hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # track motion points
    cnt=ut.getMaxContour(contours,4000)	#store total motion points
    if cnt is not None: # is there something there?
        gesture,label=ut.getGestureImg(cnt,img1,mask,model)   # passing the trained model for prediction and fetching the result
        if(label!=None): # is the model finding something in the box that matches a label?
            if(temp==0): # if temp is 0
                previouslabel=label # last label now label
            elif previouslabel==label: # still same gesture?
                previouslabel=label # track again
                temp+=1 # increse temp gesture count
            else: # otherwise
                temp=0 # temp gesture back to 0
            if(temp==40): # has it been on screen for 40 temp counts?
                if(label=='P'): # create sentence space if user does P
                    label=" " # lable space
                    text= text + label # add results to text
                if(label=='Q'): # Wipe with Q(QUIT)
                    words = re.split(" +",text) # split result
                    words.pop() # push text off
                    text = " ".join(words) # fresh text
                        
            print(text) # print out your last gestures before quiting
            print(label)
        cv2.putText(img,label,(50,150), font,8,(0,125,155),2)  # displaying the predicted letter on the main screen
        cv2.putText(img,text,(50,450), font,3,(0,0,255),2)
            
    cv2.imshow('Frame',img) # show on screen
    #cv2.imshow('Mask',mask)
    key = cv2.waitKey(1) & 0xFF # wait for q to quit
    if key == ord("q"): # is Q?
            #cap.release()        
        cv2.destroyAllWindows() # close OpenCV session
        camera.close()
        break # stop while

    

