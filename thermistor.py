# thermistor.py
# The file called to detect the temperature in the water tank
# Created by: Team MF02 
#           1. SANDRA LO YII SHIN
#           2. MAJEED ABDUL MAJEED
#           3. TAY MING HUI
#           4. TEOH XHU WEI
#           5. VINCENT LAW YUN KAE
# Last modified: 21 MAY 2023

# functions that run the thermistor to detect the temperature
from pymata4 import pymata4
import time
import math

# A callback function to detect the changes in temperature during the detection time
# Inputs:
#     data - [pin_type=12, trigger pin number, distance, timestamp]
# Return:
#     None
def the_callback_ther(data): 
    global thermistorPollData
    thermistorPollData.append(data[2])

# Function to detect the temperature in the water tank
# Inputs:
#     arduinoBoard - current Arduino board
#     detectionTime - time for detecting the temperature
# Return:
#     finalTemp - temperature in the water tank
def thermistor_detect(board,detectionTime): 
    global thermistorPollData  
    thermistorPin = 0 # Analog Pin
    thermistorPollData = []
    tempList = []
    voltageSupply = 5
    fixResistance = 10000
    # set up the pin and callback function
    board.set_pin_mode_analog_input(thermistorPin,the_callback_ther)
    time.sleep(0.1)
    timePass = 0
    while timePass < detectionTime:
        # record start time for measuring the polling time
        startTime = time.time()
        # voltage passing through the thermistor is detected evert 0.2 seconds
        time.sleep(0.2) 
        # check if they is any temperature changes during the sleeptime
        # if yes using the average value detected from callback function as current voltage passing through the thermistor
        # if no using the value detected by analog_read
        if thermistorPollData == []:
            currentVoltage = board.analog_read(thermistorPin)[0]
        else:
            currentVoltage = sum(thermistorPollData)/len(thermistorPollData)
        # using formula to convert raw data get to temperature
        vOut = currentVoltage*voltageSupply/1023
        rThermistor = fixResistance*vOut/(voltageSupply-vOut)
        temp = round(-21.21*math.log(rThermistor/1000) + 72.203,2)
        # append temperature get to a temperature list named 'tempList'
        tempList.append(temp)
        thermistorPollData = []
        endTime = time.time()
        timePass += (endTime-startTime)
    # all the temperature in the tempList is added up by 2 for calibration
    tempList = [i+2 for i in tempList]
    # the final temperature is calculated by taking average of the tempList
    finalTemp = sum(tempList)/len(tempList)
    return finalTemp

if __name__ == "__main__":
    board = pymata4.Pymata4()
    while True:
        try:
            print("Start detecting.....")
            time.sleep(1)
            temp = thermistor_detect(board,1)
            print("****************")
            print(f'Temperature detected = {temp}')
            print("****************")
            # distanceList.append(distance)
            # print(distanceList)
            # time.sleep(1.5)
        except KeyboardInterrupt:
            board.shutdown()
            break