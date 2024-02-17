import cv2
import numpy as np
from time import sleep as zzz
from BoyScout.triangle import is_right_triangle

# initialize the camera 
# If you have multiple camera connected with  
# current device, assign a value in cam_port  
# variable according to that 
cam_port = 1
cam = cv2.VideoCapture(cam_port) 
  
def centroid(contour):
    
    M = cv2.moments(contour)
    if M['m00'] != 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
    
    return (cx,cy)

def yellow(rgbimage):
    
    blur = cv2.GaussianBlur(rgbimage, (5,5), 0)

    hsv_image = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Define the range of yellow color in HSV
    lower_yellow = np.array([20, 50, 100])
    upper_yellow = np.array([40, 255, 255])

    # Threshold the HSV image to get only yellow color
    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def printDis(redCen, yelCen, image):
    pairs = []
    for rx, ry in yelCen:
        lowest = 1000
        cur = (0,0)
        for yx, yy in redCen:
            cv2.line(image, (rx, ry), (yx, yy), (100, 12, 50), 2)
            dis = ((rx-yx)**2 + (ry-yy)**2)**0.5
            if dis < lowest:
                lowest = dis
                cur = (yx, yy)
            cv2.putText(image, f"{int(dis)}px", (int((rx + yx)/2 + 4), int((ry+yy)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 12, 50), 2)
        pairs.append(((rx, ry), cur))

        cv2.imshow("distances", image)

        #Only Smallest Pairs:
        for (r, y) in pairs:
            cv2.line(image, r, y, (100, 12, 50), 2)

        cv2.imshow("flags", image)

def red(rgbimage):
    blur = cv2.GaussianBlur(rgbimage, (7,7), 0)

    hsv_image = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # lower boundary RED color range values; Hue (0 - 10)
    lower1 = np.array([0, 70, 100])
    upper1 = np.array([10, 255, 255])
 
    # upper boundary RED color range values; Hue (160 - 180)
    lower2 = np.array([160,70,100])
    upper2 = np.array([179,255,255])

    # Threshold the HSV image to get only yellow color
    top_mask = cv2.inRange(hsv_image, lower1, upper1)
    bot_mask = cv2.inRange(hsv_image, lower2, upper2)

    red_mask = top_mask + bot_mask

    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def go():

    # reading the input using the camera 
    result, image = cam.read() 
    
    # If image will detected without any error,  
    # show result 
    if result: 
    
        # showing result, it take frame name and image  
        # output 
        cv2.imshow("og", image) 

        # Yellow Thresh
        yel_con = yellow(image)
        red_con = red(image)
        
        red_con_new = []
        for contour in red_con:

            print(len(contour))
            # Approximate the contour
            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) == 3 and cv2.contourArea(contour) > 80:
                red_con_new.append(approx)
        
        yel_con_new = []
        for contour in yel_con:

            # Approximate the contour
            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) == 3 and cv2.contourArea(contour) > 80:
                yel_con_new.append(approx)
        

        # Draw the simplified contour
        redim = cv2.drawContours(image, red_con_new, -1, (0, 255, 0), 2)
        redim = cv2.drawContours(redim, yel_con_new, -1, (255, 0, 0), 2)

        finim = redim.copy()

        # Check if triangle is more or less right-angled!

        #red_con_new = filter(lambda x: is_right_triangle(np.vstack(x).squeeze()), red_con_new)
        #yel_con_new = filter(lambda x: is_right_triangle(np.vstack(x).squeeze()), yel_con_new)


        #Get all centroids
        redCen = [centroid(x) for x in red_con_new]
        yelCen = [centroid(x) for x in yel_con_new]

        for px,py in redCen:
            cv2.circle(redim, (px,py), 3, (0, 255, 0), -1)

        for px,py in yelCen:
            cv2.circle(redim, (px,py), 3, (255, 0, 0), -1)
        
        cv2.imshow("conts", redim)

        #printDis(redCen, yelCen, redim)


        # If keyboard interrupt occurs, destroy image  
        # window 
    
    # If captured image is corrupted, moving to else part 
    else: 
        print("No image detected. Please! try again")

while True:
    go()

    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cv2.destoyAllWindows()