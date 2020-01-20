import cv2
import numpy as np
import rospy
from std_msgs.msg import String

lowerBound=np.array([33,80,40])
upperBound=np.array([102,255,255])

red = (255,0,0)
distance = 1
xcenter = 1
center = 0
cam = cv2.VideoCapture(1)

kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))


def limelightPublisher():
    pub = rospy.Publisher('visiondata', String, queue_size=10)
    rospy.init_node('visionsender', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    #prev frame not image
    ret, image = cam.read()
    ret, img = cam.read()
    #added resize function
    frame = cv2.resize(image, (250, 250))
    
    #convert BGR to HSV
    imgHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    # create the Mask
    mask=cv2.inRange(imgHSV,lowerBound,upperBound)
    #morphology
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

    maskFinal=maskClose
    _, conts, _= cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for i in range(len(conts)):
        #cool center stuff (for big brains only)        
        c =  max(conts,key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 50:
            x,y,w,h=cv2.boundingRect(conts[i])
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255), 2)
            print(center)
            xcenter = (int(M["m10"] / M["m00"]))
            distance = int(xcenter - 125)
             
            stringVal = String(xcenter)
            rospy.loginfo(stringVal)
            pub.publish(stringVal)

        #else:
            #this is run if figure found is less than a defined number of pixels
            #table.putNumber('x', 125)
            
    # Uncomment the following ONLY if a display is connected (if you want to see the detection output)   
    #cv2.imshow("maskClose",maskClose)
    #cv2.imshow("maskOpen",maskOpen)
    #cv2.imshow("mask",mask)
    #cv2.imshow("cam",frame)
    cv2.waitKey(10)

if __name__ == '__main__':
    try:
        limelightPublisher()
    except rospy.ROSInterruptException:
        pass
