# ultrasonic.py
# The file called to detect the water level in the water tank
# Created by: Team MF02 
#           1. SANDRA LO YII SHIN
#           2. MAJEED ABDUL MAJEED
#           3. TAY MING HUI
#           4. TEOH XHU WEI
#           5. VINCENT LAW YUN KAE
# Last modified: 21 MAY 2023



import time
from pymata4 import pymata4


triggerPin = 13
echoPin = 12
callbackDistanceList = []
distance = -1
finalDistanceList = []



# A callback function to detect the changes in water level during the detection time
# Inputs:
#     data - [pin_type=12, trigger pin number, distance, timestamp]
# Return:
#     None
def the_callback(data):

    try:
        callbackDistanceList.append(data[2])
    except KeyboardInterrupt:
        return



# Function to detect the gap between the ultrasonic sensor and the water level
# Inputs:
#     arduinoBoard - current Arduino board
#     detectionTime - time for detecting the water level
# Return:
#     gapHeight - gap between the ultrasonic sensor and water level
def ultrasonic_detect(arduinoBoard, detectionTime):

    global callbackDistanceList
    global finalDistanceList
    finalDistanceList = []

    # set up the pin and callback function
    arduinoBoard.set_pin_mode_sonar(triggerPin, echoPin, the_callback, timeout = 10000000)
    time.sleep(0.1)

    timePass = 0

    while timePass < detectionTime:
        startTime = time.time()
        constantDistanceRead = arduinoBoard.sonar_read(triggerPin)[0]
        # a instantGapDistance is detected every 0.3 seconds
        time.sleep(0.3)
        # check if they is any changes during the sleeptime
        # if yes using the average value detected from callback function as instant gap between ultrasonic sensor and water level as instantGapDistance
        # if not using the value detected by sonar_read
        if callbackDistanceList == []:
            instantGapDistance = constantDistanceRead
        else:
            instantGapDistance = sum(callbackDistanceList)/len(callbackDistanceList)
        # append instantGapDistance to a finalDistanceList
        finalDistanceList.append(instantGapDistance)
        callbackDistanceList = []
        endTime = time.time()
        timePass += (endTime-startTime)
    
    # all the reading in finalDistanceList is subtracted by 1 to compensate the distance between the lowest point of ultrasonic sensor to the spot where sonar wave is released and detected
    finalDistanceList = [reading-1 for reading in finalDistanceList]

    # the final gapHeight during the detection time is calcultated by taking the average of finalDistanceList
    gapHeight = sum(finalDistanceList)/len(finalDistanceList)
    return gapHeight



# test code
if __name__ == "__main__":
    board = pymata4.Pymata4()
    distanceList = []
    while True:
        try:
            print("Start detecting.....")
            time.sleep(1)
            distance = ultrasonic_detect(board,1)
            print("****************")
            print(f'Distance detected = {distance}')
            print("****************")
            # distanceList.append(distance)
            # print(distanceList)
            # time.sleep(1.5)
        except KeyboardInterrupt:
            board.shutdown()
            break