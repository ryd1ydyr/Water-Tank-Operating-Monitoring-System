# system_menu.py
# The file that displays the system interface to allow user to switch between modes with its associated functions
# Created by: Team MF02
#           1. SANDRA LO YII SHIN
#           2. ABDUL MAJEED
#           3. TAY MING HUI
#           4. TEOH XHU WEI
#           5. VINCENT LAW YUN KAE
# Last modified: 21 MAY 2023

import time
import matplotlib.pyplot as plt
import tank_operations
from pymata4 import pymata4
import seven_segment
import motor
import alert_system as rov


# system_menu_and_data is a function that displays a user-interface system that allows the user to choose and
# switch between modes: tank operation, system settings, data observation, admin access, and quit program
# no input parameters and no return value
def system_menu_and_data():

    global password, adminMasterKey, tempAdminStatus

    system_start_up()
    while True:

        try:
            print('\n\n====================================')
            print('SYSTEM MENU'.center(40))
            print('====================================\n')
            print("""
            1 tank operation
            2 system settings
            3 data observation
            4 admin access
            5 quit program
                            """)

            # mode selection
            prompt = "Select Mode (1/2/3/4/5): "
            acceptedValues = ["1", "2", "3", "4", "5"]

            choice = validate_input(prompt, acceptedValues, "int")

            # option: tank operation
            if choice == "1":
                print('Commencing tank operation...\n')
                progress_bar(100)
                print()
                tank_operation()

            # option: system settings
            elif choice == "2":
                print('Loading system settings...\n')
                progress_bar(100)
                print()
                admin_lock_out()
                if tempAdminStatus == False and adminStatus == False:
                    system_settings(password)
                else:
                    update_system_setting()

            # option: data observation
            elif choice == "3":
                print('Commencing data observation...\n')
                progress_bar(100)
                print()
                data_observation()

            # option: admin access
            elif choice == "4":
                admin_lock_out()
                if adminStatus == False and tempAdminStatus == False:
                    prompt = "\nPlease enter admin masterkey: "
                    acceptedValues = []

                    keyCheck = validate_input(prompt, acceptedValues, "int")

                    if keyCheck == adminMasterKey:
                        if tempAdminStatus == False and adminStatus == False:
                            tempAdminStatus = True
                            start_temp_admin_timer()
                        print('Loading admin menu...\n')
                        progress_bar(100)
                        admin_access()
                    else:
                        print(
                            "\nINCORRECT MASTERKEY: admin access denied. Returning to system menu...\n\n"
                        )
                        progress_bar(100)
                else:
                    admin_access()

            # option: quit program
            else:
                end_program()
                break
        except KeyboardInterrupt:
            print('\nKEYBOARD INTERRUPT DETECTED: Already in system menu.')

            # option: quit program
            prompt = "Would you like to quit the program (Y/N)?: "
            acceptedValues = ["Y", "N"]

            option = validate_input(prompt, acceptedValues, "str")

            if option == 'Y':
                end_program()
                break

            else:
                print('\nReturning to system menu...')
                continue


# tank_operation is a function to monitor and control the tank operation once called
# no input parameters and no return value


def tank_operation():

    tank_operations.polling_loop()
    return None


# system_settings is a function that prompts the user to input the password before granting access to the
# system settings. The user has three attempts to input the correct
# password before a lockout period of 5 minutes. During which a countdown
# timer will be printed every 10 seconds. Confirmation messages will be
# printed to the console to notify the user whether the password is correct
# or incorrect.
# Input:
#  userPassword - pre-defined password to access the system settings
# Return:
#  None
def system_settings(userPassword):

    global lockOut, errorCount

    stayInFunction = True

    while stayInFunction:
        try:
            if lockOut == False:

                num_of_trials = 3
                while True:
                    # password check
                    inputPassword = input("\nPlease key in the password: ")
                    if inputPassword == userPassword:
                        errorCount = 0
                        print(
                            "PASSWORD ACCEPTED: Loading system parameters...\n"
                        )
                        progress_bar(100)

                        update_system_setting()
                        return
                    else:
                        errorCount += 1
                        print(
                            f"Incorrect Password. Attempts left: {num_of_trials - (errorCount)}\n"
                        )

                    if errorCount == 3:
                        print("Incorrect Password. No Attempts left.")
                        print(
                            "UPDATE SYSTEM PARAMETERS feature disabled for 5 minutes. User may still access all other tank features while under lockout."
                        )
                        print('[CTRL+C to return to system menu]\n\n')

                        # lockout when out of trials
                        start_lock_out_timer()
                        lock_out()
                        break

            # lockout ongoing
            else:
                lock_out()
        except KeyboardInterrupt:
            print(
                "\nKEYBOARD INTERRUPT DETECTED: Returning to system menu...\n\n"
            )
            progress_bar(100)
            stayInFunction = False
            return

    return


# update_system_setting is a function that allows the user to view and update system parameters
# which include: tankBaseArea,tankHeight and motorSpeed after successfully inputting the password.
# Confimation messages will be printed to the console after every successful
# change.
# no input parameters and return value
def update_system_setting():
    global tankBaseArea, tankHeight, maxTankVolume, motorSpeedLow, motorSpeedHigh, pollingMinRate, pollingMaxRate, observationTime
    global adminStatus, tempAdminStatus

    # dictionaries of all modifiable parameters and their units
    allParams = {
        '1': 'TANK BASE AREA',
        '2': 'TANK HEIGHT',
        '3': 'MAX. TANK VOLUME',
        '4': 'MOTOR SPEED (LOW)',
        '5': 'MOTOR SPEED (HIGH)',
        '6': 'MIN. POLLING RATE',
        '7': 'MAX. POLLING RATE',
        '8': 'OBSERVATION DURATION'
    }

    allParamUnits = {
        '1': 'cm^2',
        '2': 'cm',
        '3': 'L',
        '4': 'PWM',
        '5': 'PWM',
        '6': 's',
        '7': 's',
        '8': 's'
    }

    print('\n\n====================================')
    print('SYSTEM PARAMETERS'.center(40))
    print('====================================\n')
    print(f"""
    1 base area = {tankBaseArea}{allParamUnits['1']}
    2 tank height = {tankHeight}{allParamUnits['2']}
    3 max. tank volume = {maxTankVolume}{allParamUnits['3']}
    4 motor speed (LOW) = {motorSpeedLow}{allParamUnits['4']}
    5 motor speed (HIGH) = {motorSpeedHigh}{allParamUnits['5']}
    6 min. polling rate = {pollingMinRate}{allParamUnits['6']}
    7 max. polling rate = {pollingMaxRate}{allParamUnits['7']}
    8 observation duration = {observationTime}{allParamUnits['8']}
    """)

    prompt = "Would you like to change the system setting? (Y/N)\n"
    acceptedValues = ["Y", "N"]

    userDecision = validate_input(prompt, acceptedValues, "str")

    # option: no changes
    if userDecision == "N":

        print('\nREVIEW COMPLETE. Returning to system menu...\n\n')
        progress_bar(100)
        return

    # option: change settings
    else:
        stayInFunction = True
        while stayInFunction:

            print("\n\n----------- UPDATE SYSTEM PARAMETERS ------------")
            print("""
            1 update TANK BASE AREA 
            2 update TANK HEIGHT
            3 update MAX. TANK VOLUME   
            4 update MOTOR SPEED (LOW)
            5 update MOTOR SPEED (HIGH)
            6 update MIN. POLLING RATE
            7 update MAX. POLLING RATE 
            8 update OBSERVATION DURATION
            9 return to system menu
            """)
            prompt = "Please enter your selection (1/2/3/4/5/6/7/8/9): "
            acceptedValues = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

            userParamChoice = validate_input(prompt, acceptedValues, "int")

            if userParamChoice != "9":

                # obtain parameter name and unit
                paramChoice = allParams[userParamChoice]
                paramUnit = allParamUnits[userParamChoice]

                # modify tank base area
                if userParamChoice == "1":

                    tempParam = tankBaseArea
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f"Enter new {paramChoice} value: "
                    acceptedValues = []

                    tankBaseArea = float(
                        validate_input(prompt, acceptedValues, "float"))
                    newParam = tankBaseArea

                # modify tank height
                elif userParamChoice == "2":

                    tempParam = tankHeight
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f'Enter new {paramChoice} value: '
                    acceptedValues = []

                    tankHeight = float(
                        validate_input(prompt, acceptedValues, "float"))
                    newParam = tankHeight

                # modify maximum tank volume
                elif userParamChoice == "3":
                    tempParam = maxTankVolume
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f'Enter new {paramChoice} value: '
                    acceptedValues = []

                    maxTankVolume = float(
                        validate_input(prompt, acceptedValues, "float"))
                    newParam = maxTankVolume

                # modify motor speed, low
                elif userParamChoice == "4":

                    tempParam = motorSpeedLow
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f"Enter new {paramChoice} value: "
                    acceptedValues = motorSpeedHigh

                    motorSpeedLow = int(
                        validate_input(prompt, acceptedValues,
                                       "intLessThanMotor"))
                    newParam = motorSpeedLow

                # modify motor speed, high
                elif userParamChoice == "5":

                    tempParam = motorSpeedHigh
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f"Enter new {paramChoice} value: "
                    acceptedValues = motorSpeedLow

                    motorSpeedHigh = int(
                        validate_input(prompt, acceptedValues,
                                       "intMoreThanMotor"))
                    newParam = motorSpeedHigh

                # modify min polling rate
                elif userParamChoice == "6":

                    tempParam = pollingMinRate
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f"Enter new {paramChoice} value: "
                    acceptedValues = pollingMaxRate

                    pollingMinRate = int(
                        validate_input(prompt, acceptedValues, "intLessThan"))
                    newParam = pollingMinRate

                # modify max polling rate
                elif userParamChoice == "7":

                    tempParam = pollingMaxRate
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f"Enter new {paramChoice} value: "
                    acceptedValues = pollingMinRate

                    pollingMaxRate = int(
                        validate_input(prompt, acceptedValues, "intMoreThan"))
                    newParam = pollingMaxRate

                # modify observation duration
                elif userParamChoice == "8":

                    tempParam = observationTime
                    print(f'Current {paramChoice} = {tempParam}{paramUnit}')
                    prompt = f"Enter new {paramChoice} value: "
                    acceptedValues = []

                    observationTime = int(
                        validate_input(prompt, acceptedValues, "int"))
                    newParam = observationTime

                # update confirmation message
                print('\n\nUpdating parameter..\n\n')
                progress_bar(100)
                print('\n\n')
                print(
                    f'UPDATE SUCCESSFUL: Changed {paramChoice} from {tempParam}{paramUnit} to {newParam}{paramUnit}'
                )
                time.sleep(1)

            # option: return to menu
            else:

                print('\nREVIEW COMPLETE. Displaying system parameters...\n')
                progress_bar(100)
                print('\n\n')
                print('\n\n====================================')
                print('UPDATED SYSTEM PARAMETERS'.center(40))
                print('====================================\n')

                print(f"""
                    1 base area = {tankBaseArea}{allParamUnits['1']}
                    2 tank height = {tankHeight}{allParamUnits['2']}
                    3 max. tank volume = {maxTankVolume}{allParamUnits['3']}
                    4 motor speed (LOW) = {motorSpeedLow}{allParamUnits['4']}
                    5 motor speed (HIGH) = {motorSpeedHigh}{allParamUnits['5']}
                    6 min. polling rate = {pollingMinRate}{allParamUnits['6']}
                    7 max. polling rate = {pollingMaxRate}{allParamUnits['7']}
                    8 observation duration = {observationTime}{allParamUnits['8']}
                    """)

                time.sleep(2)
                print('\n\nReturning to system menu...\n')
                progress_bar(100)
                stayInFunction = False


# validate_input is universal function to check and validate all inputs inside the code to ensure they are
# acceptable. Will repeatedly prompt the user to re-enter the input until a valid input is given.
# Inputs:
#     inputPrompt - the prompt used to ask user for input
#     acceptableValues - a list of acceptable values to the input. If acceptable values are too broad, an empty
#                        list is accepted
#     type - the type of input to be validated, either an integer or string
# Return:
#     validated input as a string
def validate_input(inputPrompt, acceptableValues, type):
    invalid = True

    while invalid:
        if "int" in type:
            try:
                test = input(inputPrompt)
                intCheck = int(str(test))

                if intCheck <= 0:
                    print(
                        "INVALID INPUT: Input must be greater than 0. Please try again."
                    )
                    invalid = True
                elif acceptableValues == []:
                    return test
                elif "LessThan" in type:
                    if "Motor" in type:
                        if intCheck > acceptableValues:
                            print(
                                f"Minimum value must be lesser than the Maximum Value of {acceptableValues}. Please try again."
                            )
                            invalid = True
                        elif intCheck not in range(30, 256):
                            print(
                                "Value must be within the range of 30-255 pwm. Please try again."
                            )
                            invalid = True
                        else:
                            return test
                    elif intCheck > acceptableValues:
                        print(
                            f"Minimum value must be lesser than the Maximum Value of {acceptableValues}. Please try again."
                        )
                        invalid = True
                    else:
                        return test

                elif "MoreThan" in type:
                    if "Motor" in type:
                        if intCheck < acceptableValues:
                            print(
                                f"Maximum value must be greater than the Minimum Value of {acceptableValues}. Please try again."
                            )
                            invalid = True
                        elif intCheck not in range(30, 256):
                            print(
                                f"Value must be within the range of 30-255 pwm. Please try again."
                            )
                            invalid = True
                        else:
                            return test
                    elif intCheck < acceptableValues:
                        print(
                            f"Maximum value must be greater than the Minimum Value of {acceptableValues}. Please try again."
                        )
                        invalid = True
                    else:
                        return test
                else:
                    if test not in acceptableValues:
                        print(
                            "INVALID INPUT: Input out of acceptable range. Please try again."
                        )
                        invalid = True

                    else:
                        return test

            except ValueError:
                print(
                    "INVALID INPUT: Detected non-integer input. Please try again."
                )
                invalid = True

        elif type == "str":
            test = input(inputPrompt)
            intList = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

            # test: input contains numerical input
            for _ in range(len(test)):
                if test[_] in intList:
                    intCheck = True
                else:
                    intCheck = False

            if intCheck:
                print(
                    "INVALID INPUT: Detected numerical input. Please try again."
                )
                invalid = True
            else:
                # test: input not in acceptable values list
                if test.upper() not in acceptableValues:
                    print(
                        "INVALID INPUT: Input out of acceptable values. Please try again."
                    )
                    invalid = True

                # return
                else:
                    return test.upper()

        elif type == 'float':

            try:
                test = input(inputPrompt)
                floatCheck = float(test)

                if floatCheck <= 0:
                    print(
                        "INVALID INPUT: Input must be greater than 0. Please try again."
                    )
                    invalid = True
                else:
                    return floatCheck

            except ValueError:
                print(
                    'INVALID INPUT: Detected non-numerical input. Please try again.'
                )
                invalid = True


# system_start_up is a function that initialises all global variables needed in the code, displays the default
# parameters of the system and checks whether the user is a normal user or admin.
# :return: None
def system_start_up():

    # initalises the required global variables
    global tankBaseArea, tankHeight, maxTankVolume, motorSpeedLow, motorSpeedHigh, pollingMinRate, pollingMaxRate, observationTime
    global password, adminMasterKey, lockOut, errorCount, lockOutTimeSecond, adminStatus,adminLockOutTime,tempAdminStatus
    global board

    tankBaseArea = 24 * 24  # cm^2
    tankHeight = 21  # cm
    maxTankVolume = 10  # L
    motorSpeedLow = 90  # PWM
    motorSpeedHigh = 250  # PWM
    pollingMinRate = 1  # s
    pollingMaxRate = 5  # s
    observationTime = 20  # s
    lockOut = False

    #For marking and testing purposes, lock out time can be modified here
    lockOutTimeSecond = 50
    adminLockOutTime = 30 
    errorCount = 0

    password = "332450"
    adminMasterKey = "1111"
    tempAdminStatus = False
    adminStatus = False

    # printing start up screen
    print('====================================')
    print('TANK MONITORING SYSTEM'.center(40))
    print('====================================')
    time.sleep(1)
    print('\nSystem starting up...\n\n')
    progress_bar(100)
    board = pymata4.Pymata4()
    motor.motor_setup(board)
    seven_segment.seven_segment_setup(board)
    rov.alert_setup(board)
    print('ULTRASONIC SENSOR setup complete.')
    print('THERMISTOR setup complete.')
    print('\n\nSYSTEM START UP SUCCESSFUL. Displaying system parameters.')
    seven_segment.disp_seven_segment(board,"WELCOME")
    # displays default system paramters
    print('\n\n====================================')
    print('DEFAULT SYSTEM PARAMETERS'.center(40))
    print('====================================\n')
    print(f"""
    1 tank base area = {tankBaseArea}cm^2
    2 tank height = {tankHeight}cm
    3 max. tank volume = {maxTankVolume}L
    4 motor speed (LOW) = {motorSpeedLow}PWM
    5 motor speed (HIGH) = {motorSpeedHigh}PWM
    6 min. polling rate = {pollingMinRate}s
    7 max. polling rate = {pollingMaxRate}s
    8 observation duration = {observationTime}s

    """)

    time.sleep(1)

    # checking user status (normal user or admin)
    print('====================================')
    print('USER ACCOUNT SELECTION'.center(40))
    print('====================================\n')
    print("1 guest user")
    print("2 admin")

    prompt = "\nPlease select account type (1/2): "
    acceptedValues = ["1", "2"]

    user = validate_input(prompt, acceptedValues, "int")

    if user == "1":
        adminStatus = False
        print('\n\nGUEST USER ACCOUNT selected. Loading user menu...\n\n')
        progress_bar(100)
        print("\n\n----------- WELCOME USER ------------")
        return

    else:
        # this person has admin access
        print('ADMIN ACCOUNT selected.')
        prompt = "\nPlease enter admin masterkey: "
        acceptedValues = []

        keyCheck = validate_input(prompt, acceptedValues, "int")

        if keyCheck == adminMasterKey:
            adminStatus = True
            print('Loading admin menu...\n')
            progress_bar(100)
            admin_access()
            return
        else:
            print("\nINCORRECT MASTERKEY: accessing as GUEST USER...")
            adminStatus = False
            progress_bar(100)
            print("\n\n----------- WELCOME USER ------------")
            return


# admin_access is a function that grants additional functions and authority over the system to the admin.
# Allowing the admin to update system password or parameters while also providing the option to override the
# lock out status of the system
# :return: None
def admin_access():

    global password, adminStatus, lockOut, errorCount
    stayInFunction = True

    print("\n\n----------- WELCOME ADMIN ------------")

    while stayInFunction:
        print('\n\n====================================')
        print('ADMIN ACCESS'.center(40))
        print('====================================\n')
        print("""
        1 display system password
        2 update system parameters 
        3 override lockout status
        4 return to system menu
                            """)
        prompt = "Please select mode (1/2/3/4): "
        acceptedValues = ["1", "2", "3", "4"]

        adminDecision = validate_input(prompt, acceptedValues, "int")

        # option: display password
        admin_lock_out()
        if adminDecision == "1"and (tempAdminStatus == True or adminStatus == True):
            print(f"Current system password: {password} ")

            # option: change password
            prompt = "Would you like to edit the password (Y/N)?: "
            acceptedValues = ["Y", "N"]

            option = validate_input(prompt, acceptedValues, "str")

            admin_lock_out()
            if option == "Y" and (tempAdminStatus == True or adminStatus == True):
                prompt = "Please enter new password: "
                acceptedValues = []

                password = validate_input(prompt, acceptedValues, "int")
                print('Updating password...\n')
                progress_bar(100)
                print(f"\n\nPASSWORD UPDATE SUCCESSFUL. Password: {password} ")

            else:
                stayInFunction = True

        # option: update system settings
        elif adminDecision == "2" and (tempAdminStatus == True or adminStatus == True):
            update_system_setting()

        # option: override lockout
        elif adminDecision == "3" and (tempAdminStatus == True or adminStatus == True):
            if lockOut == False:
                print("\n\nUser is not under lockout.")
                time.sleep(1)
            else:
                lockOut = False
                errorCount = 0
                progress_bar(100)
                print("\n\nUser lockout terminated.")
                time.sleep(1)

        # option: return to system menu
        else:
            stayInFunction = False
            print('\n\nReturning to system menu...\n')
            progress_bar(100)
            return

    return


# data_observation is a function to enable visualisation of the water volume of the tank through a formatted
# graph. The graph is plotted based on data from elaspedTimeList and tankWaterVolumeList in the last 20 seconds
# no input parameters and return value
def data_observation():

    global observationTime 
    stayInFunction = True

    while stayInFunction:
        try:
            print('\n\n====================================')
            print('DATA OBSERVATION'.center(40))
            print('====================================\n')
            print("""
            1 Water Volume against Time
            2 Rate of Change of Water Volume against Time 
            3 Water Level against Time
            4 return to system menu
                                """)
            prompt = "Please select mode (1/2/3/4): "
            acceptedValues = ["1", "2", "3", "4"]

            user = validate_input(prompt, acceptedValues, "int")

            # check if enough data for plotting
            if sum(tank_operations.elapsedTimeList) < observationTime:
                print(
                    f"INSUFFICIENT DATA: Polling duration must exceed {observationTime}s"
                )
                time.sleep(1)
                print('\n\nReturning to system menu...\n')
                progress_bar(100)
            else:
                # filter lists to contain only last 20s worth of data
                plotElaspedTimeList = tank_operations.elapsedTimeList[:]
                plotTankWaterVolumeList = tank_operations.tankWaterVolumeList[:]
                plotRateOfVolumeChangeList = tank_operations.rateOfVolumeChangeList[:]
                plotTankWaterLevelList = tank_operations.tankWaterLevelList[:]

                while sum(plotElaspedTimeList) > observationTime:
                    plotElaspedTimeList.pop(0)
                    # retain last removed volume value for plotting
                    lastPoppedVolume = plotTankWaterVolumeList.pop(0)
                    lastPoppedRate = plotRateOfVolumeChangeList.pop(0)
                    lastPoppedLevel = plotTankWaterLevelList.pop(0)

                cumulativeTimeList = []
                for timeIndex in range(len(plotElaspedTimeList)):
                    cumulativeTimeList.append(
                        plotElaspedTimeList[timeIndex] +
                        sum(plotElaspedTimeList[0:timeIndex]))

                # set reference origin
                cumulativeTimeList.insert(0, 0)
                cumulativeTimeList[-1] = observationTime
                plotTankWaterVolumeList.insert(0, lastPoppedVolume)
                plotRateOfVolumeChangeList.insert(0, lastPoppedRate)
                plotTankWaterLevelList.insert(0, lastPoppedLevel)

            if user == "1":
                print('\n\nSUFFICIENT DATA: Plotting Water Volume against Time graph...\n')
                print(
                    "NOTICE: Please close the graph to continue using the system")
                progress_bar(100)
                while len(cumulativeTimeList) != len(plotTankWaterVolumeList):
                    if len(cumulativeTimeList) > len(plotTankWaterVolumeList):
                        cumulativeTimeList.pop(0)
                    else:
                        plotTankWaterVolumeList.pop(0)
                # plotting Water Volume against Time graph
                plt.plot(cumulativeTimeList, plotTankWaterVolumeList[0:len(cumulativeTimeList)], 'o-b')
                plt.xlabel("Time (second, s)")
                plt.ylabel("Water Volume (litre, L)")
                plt.title("Graph of Water Volume against Time (L/s)")
                graphName = "Graph_of_Water_Volume_against_Time.png"
                plt.savefig(graphName)
                plt.show()
            
            elif user == "2":
                # plotting Rate of Change of Water Volume against Time graph
                print('\n\nSUFFICIENT DATA: Plotting Rate of Change of Water Volume against Time graph...\n')
                print(
                    "NOTICE: Please close the graph to continue using the system")
                progress_bar(100)   
                while len(cumulativeTimeList) != len(plotRateOfVolumeChangeList):
                    if len(cumulativeTimeList) > len(plotRateOfVolumeChangeList):
                        cumulativeTimeList.pop(0)
                    else:
                        plotRateOfVolumeChangeList.pop(0)
                plt.plot(cumulativeTimeList, plotRateOfVolumeChangeList[0:len(cumulativeTimeList)], 'o-b')
                plt.xlabel("Time (second,s )")
                plt.ylabel("Change In Water Volume (litre, L)")
                plt.title("Graph of Rate of Change of Water Volume against Time (L/s^2)")
                graphName = "Graph_of_Rate_of_Change_of_Water_Volume_against_Time.png"
                plt.savefig(graphName)
                plt.show()        

            elif user == "3":
                # plotting Water Level against Time graph
                print('\n\nSUFFICIENT DATA: Plotting Water Level against Time graph...\n')
                print(
                    "NOTICE: Please close the graph to continue using the system")
                progress_bar(100)   
                while len(cumulativeTimeList) != len(plotTankWaterLevelList):
                    if len(cumulativeTimeList) > len(plotTankWaterLevelList):
                        cumulativeTimeList.pop(0)
                    else:
                        plotTankWaterLevelList.pop(0)
                plt.plot(cumulativeTimeList, plotTankWaterLevelList[0:len(cumulativeTimeList)], 'o-b')
                plt.xlabel("Time (second,s )")
                plt.ylabel("Water Level (metre, m)")
                plt.title("Graph of Water Level against Time (m/s)")
                graphName = "Graph_of_Water_Level_against_Time.png"
                plt.savefig(graphName)
                plt.show()        

            else:
                print('\n\nReturning to system menu...\n')
                progress_bar(100)
                return

        except KeyboardInterrupt:
            print("\nKEYBOARD INTERRUPT DETECTED: Returning to system menu.")
            progress_bar(100)
            return

        except AttributeError:
            print(
                "NO DATA COLLECTED: Please go to tank operation to collect enough data."
            )
            time.sleep(1)
            print('\n\nReturning to system menu...\n')
            progress_bar(100)
            return


# end_program is a function to end the program and shutdown all neccessary components
# no input parameters and return value
def end_program():

    print('\n\n====================================')
    print('END PROGRAM'.center(40))
    print('====================================')

    # Graph save to a file
    # print("\nSaving all plotted graphs into files...\n")
    # progress_bar(100)

    print("\nShutting down all tank features...\n")
    progress_bar(100)

    # shutdown tank features
    print()
    print('ULTRASONIC SENSOR turning off...')
    time.sleep(.5)
    print('THERMISTOR turning off...')
    time.sleep(.5)
    tank_operations.pump_activation('Off')
    time.sleep(.5)
    print('ALERT SYSTEM turning off...')
    time.sleep(.5)
    print('SEVEN-SEGMENT DISPLAY turning off...')
    seven_segment.disp_seven_segment(board,"GOODBYE")
    seven_segment.write_segment(board, "00000000", 'off')
    time.sleep(.8)
    print('ARDUINO BOARD shutting down...')
    board.shutdown()
    time.sleep(.5)
    print("\n\nFeature shutdown complete. Ending program...\n\n")
    progress_bar(50)
    print('\n\n====================================')
    print('GOODBYE'.center(40))
    print('====================================\n')


# start_lock_out_timer is a function that starts a timer once the user is under lock out.
# no input parameters and return value
def start_lock_out_timer():

    global lockOutStart
    lockOutStart = time.time()


# lock_out is a function that locks out the user after three incorrect password attempts. The function acts as
# the timekeeper for the lock out  duration and will update the user on the remaining lock out time every 5
# seconds if system_settings() is called
# no input parameters and return value
def lock_out():
    global lockOutStart, lockOutTimeSecond, remainingTime, lockOut, errorCount

    currentTime = time.time()
    timePassed = currentTime - lockOutStart

    # print remaining lock out time every 5 seconds
    if timePassed < lockOutTimeSecond:
        lockOut = True
        remainingTime = lockOutTimeSecond - timePassed
        if (int(remainingTime) % 5) == 0:
            print(
                f'UNDER LOCKOUT: Lockout time remaining: {int(remainingTime)}s ',
                end='\r')
    else:
        print()
        print("\nLockout ended.")
        errorCount = 0
        lockOut = False


# progress_bar is a function that displays a progress bar to simulate and visualise the delay in code execution
# Input
#  totalIteration - amount of 'skips' in progress bar
#  removeBar - option for progress bar to disapper after it finishes running
#Return
#  None
def progress_bar(totalIteration, removeBar=True):

    length = 50  # bar length
    fill = '█'  # bar 'skip' icon

    # generating progress bar
    for iteration in range(totalIteration + 1):
        percent = int(100 * (iteration / float(totalIteration)))
        filledLength = int(length * iteration // totalIteration)
        bar = (fill * filledLength) + '-' * (length - filledLength)

        print(f'\rProgress |{bar}| {percent}% Complete', end='\r')
        time.sleep(0.01)

    time.sleep(0.25)
    if removeBar == True:
        print(f'\r{" "*100}', end='\r')
    else:
        print()


# start_temp_admin_timer is a function that starts a timer once the user is granted temporary admin access.
# no input parameters and return value
def start_temp_admin_timer():
    global adminLockOutStart, adminLockOutTime,tempAdminStatus, printOnce

    adminLockOutStart = time.time()
    print(f"Temporary admin access has been granted for {adminLockOutTime/60} minutes")
    tempAdminStatus = True
    printOnce = True
    time.sleep(2)
    return

# admin_lock_out is a function that revokes the user's admin access after the specified time frame is passed.
# no input parameters and return value
def admin_lock_out():
    global adminLockOutStart, adminLockOutTime, tempAdminStatus,printOnce

    try:
        currentTime = time.time()
        timePassed = currentTime - adminLockOutStart

        if timePassed >= adminLockOutTime:
            tempAdminStatus = False
            if printOnce:
                print("Temporary admin access has been revoked")
                printOnce = False
    
        return
    
    except Exception:
        return


