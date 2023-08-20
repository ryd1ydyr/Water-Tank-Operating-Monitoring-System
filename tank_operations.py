# tank_operations.py
# The file that contains all files required to run the polling loop and its associated components
# Created by: Team MF02
#           1. SANDRA LO YII SHIN
#           2. MAJEED ABDUL MAJEED
#           3. TAY MING HUI
#           4. TEOH XHU WEI
#           5. VINCENT LAW YUN KAE
# Last modified: 21 MAY 2023

import time
import random
import system_menu
import ultrasonic as us
import seven_segment as ss
import motor
import alert_system as rov
import thermistor as tm


# A function that will repeat the sub operations that are included in the polling loop,
# calling other functions from this main function. It will routinely check for all input
# sources in each function contained in the loop and act accordingly to the sub functions
# residing in the loop. This will be the main process of the entire system operations.
# no input parameters and no return value
def polling_loop():
    print('\n\n====================================')
    print('POLLNG LOOP'.center(40))
    print('====================================\n')

    print('[CTRL+C to return to system menu]')
    time.sleep(1)
    print('\nPolling...')

    global tankVolumeState, tankHeight, tankBaseArea, pollingMinRate, pollingMaxRate, motorSpeedHigh, motorSpeedLow, rateOfVolumeChange
    global elapsedTimeList, tankWaterVolumeList, tankWaterLevelList, tankVolumeStateList
    global operationState
    global board
    global pollingStartTime

    # arduino board
    board = system_menu.board

    # system parameters
    tankHeight = system_menu.tankHeight
    tankBaseArea = system_menu.tankBaseArea
    pollingMinRate = system_menu.pollingMinRate
    pollingMaxRate = system_menu.pollingMaxRate
    motorSpeedHigh = system_menu.motorSpeedHigh
    motorSpeedLow = system_menu.motorSpeedLow

    # initialising variables
    tankVolumeState = ''
    tankWaterVolumeList = []
    elapsedTimeList = []
    tankWaterLevelList = []
    tankVolumeStateList = []
    pollingStartTime = time.time()
    # distance between the ultrasonic and water level (initialised as 0)
    gapHeight = 0

    try:
        while True:
            # start time recording, call subfunctions
            startTime = time.time()
            temp = tm.thermistor_detect(board,0.5)
            print(f"Current temperature in the water tank is {round(temp,2)} degree celcius")
            # for testing and demo purpose  
            if temp < 20:
                print("WARNING: Temperature is too low")
            elif temp > 30:
                print("WARNING: Temperature is too high")

            gapHeight = us.ultrasonic_detect(board, 1)
            tank_water_level_detection(gapHeight, tankHeight, tankBaseArea)
            # detect the current tankState and the time it last for for alert system checking
            if len(tankVolumeStateList) > 1 and tankVolumeStateList[-1] == tankVolumeStateList[-2]:
                volumeContinuousStateCount += 1
                markingTime = time.time()   # a marking time used for measuring the time taken to reach this point for calculation of time remained of particular tank state
                tankVolumeStateTime = sum(elapsedTimeList[-volumeContinuousStateCount:]) + (markingTime - startTime)
            else:
                # reset counts and time remained for particular state to 0
                tankVolumeStateTime = 0
                volumeContinuousStateCount = 0
            # activate alert system if tankState has been near full, near empty, empty and overfull for 5 s
            rov.tank_state_alert(board,tankVolumeState,tankVolumeStateTime)
            time.sleep(0.01)
            pump_activation(tankVolumeState)
            seven_segment_display()

            # end time recording, get elapsedTime
            endTime = time.time()
            elapsedTime = endTime - startTime

            print('----------------------------------------------')
            print(f'LOOP COMPLETE. Time taken: {elapsedTime:.4f}s')

            # append to list for data_observation needs
            elapsedTimeList.append(elapsedTime)
            tankWaterLevelList.append(tankWaterHeight)

            # elapsedTime out of reasonable range warning
            if elapsedTime > pollingMaxRate or elapsedTime < pollingMinRate:
                print('|| WARNING: Elapsed time out of reasonable range. ||')

            # print total polling time
            print(f'Total Polling time = {sum(elapsedTimeList):.2f}s')

            # check for tank faults
            operationStateVolChange = rate_of_volume_change(
                elapsedTimeList, tankWaterVolumeList)

            # check if tank remains operational
            operationState = operationStateVolChange

            # emergency termination in event of tank fault
            if operationState == False:
                # time.sleep(2)
                print(
                    'SUSPECTED FAULTS DETECTED'
                )
                if rateOfVolumeChange > 0:
                    print("Water is draining in too fast.")
                    motor.motor_anticlockwise_control(board,"FULL")
                else:
                    print("Water is draining out too fast.")
                    motor.motor_clockwise_control(board,"FULL")
                # time.sleep(1)

                # system_menu.end_program()
                # quit(0)

    except KeyboardInterrupt:
        cleanup()


# Conduct system cleanup in the event of KeyboardInterrupt detection.
# no input parameters and no return value
def cleanup():

    # if elapsed time is not appended by the time keyboard interrupted detected, time is calculated using
    # the difference between the time when keyboard interrupt detected and (sum of polling time + polling loop start time)

    # adds or removes elapsedTime value in the event of KeyboardInterrupt
    timeKeyBoardInterEnd = time.time()
    if len(elapsedTimeList) < len(tankWaterVolumeList) or len(
            elapsedTimeList) < len(rateOfVolumeChangeList) or len(
                elapsedTimeList) < len(tankWaterLevelList):
        elapsedTimeList.append(timeKeyBoardInterEnd - pollingStartTime -
                               sum(elapsedTimeList))
    elif len(tankWaterVolumeList) < len(elapsedTimeList) or len(
            rateOfVolumeChangeList) < len(elapsedTimeList) or len(
                tankWaterLevelList) < len(elapsedTimeList):
        elapsedTimeList.pop()

    # console alert
    print('\nKEYBOARD INTERRUPT DETECTED: Terminating polling loop...\n\n')
    time.sleep(0.5)
    motor.motor_stop_control(board)
    rov.stop_alert_system(board)
    # print runtime & return
    print(f'Total elapsed time: {sum(elapsedTimeList):.2f}s')
    displayString = round(sum(elapsedTimeList),2) + "s"
    ss.disp_seven_segment(board,displayString)
    ss.write_segment_off(board)
    time.sleep(.5)
    print('Returning to System Menu...\n\n')
    system_menu.progress_bar(100)


# Generates a display message from the tank's volume and calls to the seven_segment functions to display it
# no input parameters and no return value
def seven_segment_display():
    global tankVolumeState
    displayString = str(round(tankWaterVolumeList[-1], 2)) + "L"
    ss.disp_seven_segment(board, displayString, tankVolumeState)


# Detects and classifies the tank's measured volume into one of the following states: over full, near full,
# high, within normal range, low or nearly empty based on their respective threshold percentages
# Inputs
#     randomHeight - Random height value to simulate data from ultrasonic sensor, float
#     tankHeight - Height of the tank in cm, float
#     tankBaseArea - Base area of the tank in cm^2, float
# Return:
#     None
def tank_water_level_detection(gapHeight, tankHeight, tankBaseArea):

    global tankVolumeState, tankWaterHeight, maxTankVolume,tankVolumeStateList

    # converting distance measurement(cm) to volume measurement(L)
    tankWaterHeight = tankHeight - gapHeight
    tankWaterVolume = tankWaterHeight * tankBaseArea / 1000
    maxTankVolume = system_menu.maxTankVolume

    # converting percentage of tank water volume
    tankWaterPercentage = tankWaterVolume / maxTankVolume * 100

    # assigning state of tank according to calculated percentage of volume
    if tankWaterPercentage <= 0:
        tankWaterVolume = 0
        tankVolumeState = 'Empty'
        print('Tank is completely empty')
    elif tankWaterPercentage < 30:
        tankVolumeState = 'Near empty'
    elif 30 <= tankWaterPercentage < 40:
        tankVolumeState = 'Low'
    elif 40 <= tankWaterPercentage <= 60:
        tankVolumeState = 'Within normal range'
    elif 60 < tankWaterPercentage <= 70:
        tankVolumeState = 'High'
    elif 70 < tankWaterPercentage <= 100:
        tankVolumeState = 'Near full'
    elif tankWaterPercentage > 100:
        tankVolumeState = 'Overfull'
        tankWaterVolume = maxTankVolume

    # append data to list for data_observation needs
    tankWaterVolumeList.append(tankWaterVolume)
    tankVolumeStateList.append(tankVolumeState)

    print("")
    print(f'Tank Water Volume: {tankWaterVolume:.4f}')
    print(f'Tank State: {tankVolumeState}')

    if tankVolumeState == 'Overfull':
        print(
            '|| WARNING: Tank water level exceeds measurement range. Please inspect tank for overflows. ||'
        )


# Activates the input or output pump based on the state of water level and prints a console alert accordingly
# Inputs:
#     tankVolumeState - State of the tank volume assigned in the tank_water_level_detection function
# Return:
#     None
def pump_activation(tankVolumeState):

    global board
    board = system_menu.board

    # activate pumps (motor) according to state
    if tankVolumeState == 'Low':
        motor.motor_clockwise_control(board, 'LOW')

    elif tankVolumeState == 'Near empty' or tankVolumeState == 'Empty':
        motor.motor_clockwise_control(board, 'HIGH')

    elif tankVolumeState == 'Within normal range':
        motor.motor_stop_control(board)

    elif tankVolumeState == 'High':
        motor.motor_anticlockwise_control(board, 'LOW')

    elif tankVolumeState == 'Near full':
        motor.motor_anticlockwise_control(board, 'HIGH')

    elif tankVolumeState == 'Overfull':
        motor.motor_anticlockwise_control(board, 'HIGH')

    # shutdown
    elif tankVolumeState == 'Off':
        motor.motor_stop_control(board)


# Calculates the rate of volume change in the tank using dV/dt
# If the rate of volume change exceeds a predefined limit, it
# indicates that either the motor is faulty or there is a leak
# in the tank. Hence, the system will shutdown if the limit is
# exceeded.
# Inputs:
#     elaspedTimeList - List of elasped time values to access the change in time (dt)
#     tankWaterVolumeList - List of tank water volume values to calculate the change in volume (dV)


# Return:
#     True if rate of volume change does not exceed limit
#     False if rate of volume change exceeds limit, Boolean
def rate_of_volume_change(elaspedTimeList, tankWaterVolumeList):
    global board
    global limitRate, rateOfVolumeChange
    global rateOfVolumeChangeList
    limitRate = 1

    if len(elaspedTimeList) < 2:
        print(
            "Rate of volume change: INSUFFICIENT DATA. Must have at least 2 polled values."
        )
        return None

    index = (len(elaspedTimeList) - 1)
    changeInTime = elapsedTimeList[index]
    changeInVolume = tankWaterVolumeList[index] - tankWaterVolumeList[index -1]
    rateOfVolumeChange = changeInVolume / changeInTime
    print(f'Rate of volume change: {rateOfVolumeChange:.4f}L/s')
    # activate alert system if rate of water volume change exceeds the limit rate
    rov.rov_alert(board, abs(rateOfVolumeChange), limitRate)
    # check for abnormal volume changes, terminates pump
    if abs(rateOfVolumeChange) > limitRate:
        print(
            '\n|| WARNING: Volume change rate exceeds normal range. Please check for tank leaks/damages. ||'
        )
        try:
            rateOfVolumeChangeList.append(rateOfVolumeChange)
            return False
        except NameError:
            rateOfVolumeChangeList = [rateOfVolumeChange]
            return False

    else:
        # adding rate of volume change to list
        try:
            rateOfVolumeChangeList.append(rateOfVolumeChange)
            return True
        except NameError:
            rateOfVolumeChangeList = [rateOfVolumeChange]
            return True
