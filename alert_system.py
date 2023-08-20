# alert_system.py
# Warns the user of abnormalities during tank operations through an alert system 
# Created by: Team MF02 
#           1. SANDRA LO YII SHIN
#           2. MAJEED ABDUL MAJEED
#           3. TAY MING HUI
#           4. TEOH XHU WEI
#           5. VINCENT LAW YUN KAE
# Last modified: 21 MAY 2023

# functions that governise the alert system of the tank operations

from pymata4 import pymata4
import time
import random

# alert_setup function is used to setup the alert system which will response if abnormal tank operations detected
# Inputs:
#     board - current Arduino board
# Return:
#     None
def alert_setup(board):

    global alertPinROV, alertPinTankState, alertPinTankState5s, alertPinEnable

    alertPinROV = 11
    alertPinTankState = 2
    alertPinTankState5s = 3
    alertPinEnable = 4

    board.set_pin_mode_digital_output(alertPinROV)
    board.set_pin_mode_digital_output(alertPinTankState)
    board.set_pin_mode_digital_output(alertPinTankState5s)
    board.set_pin_mode_digital_output(alertPinEnable)

    board.digital_write(alertPinTankState,0)
    board.digital_write(alertPinTankState5s,0)

    print("ALERT SYSTEM setup complete.")
    time.sleep(2)

# rov_alert function is used to flash a yellow LED and generate buzzer alert
# when rate of volume change is out of range
# Inputs:
#     board - the arduino board used
#     rateOfVolumeChange - rate of water volume change in water tank
#     limitRate - limit rate before rate of volume change system is activated
# Return:
#     None
def rov_alert(board,rateOfVolumeChange,limitRate):
    global alertPinROV

    if rateOfVolumeChange > limitRate:
        board.digital_write(alertPinROV,1)
        print("|| WARNING: Rate of volume change exceeds normal amount. ||")
    else:
        board.digital_write(alertPinROV,0)

# tank_state_alert function is used to generate buzzer alerts when the tank is near empty or empty 
# and when the tank is empty, near empty, overfull, near full for 5 seconds
# Inputs:
#     board - the arduino board used
#     tankVolumeState - current tank state
#     tankVolumeStateTime - time sustained for current tank state
# Return:
#     None
def tank_state_alert(board,tankVolumeState,tankVolumeStateTime):
    global alertPinTankState, alertPinTankState, alertPinEnable
    board.digital_write(alertPinEnable,1)
    if (tankVolumeState == "Empty" or tankVolumeState == "Near empty" or tankVolumeState == "Near full" or tankVolumeState == "Overfull") and tankVolumeStateTime >= 5:
        board.digital_write(alertPinTankState,0)
        board.digital_write(alertPinTankState5s,1)
        print(f"|| WARNING: The tank has been {tankVolumeState} for more than 5s ||")
    elif tankVolumeState == "Empty" or tankVolumeState == "Near empty":
        board.digital_write(alertPinTankState,1)
    else:
        board.digital_write(alertPinTankState5s,0)
        board.digital_write(alertPinTankState,0)

# stop_alert_system function is used to stop the alert system when user quit the tank_operations
# Inputs:
#     board - the arduino board used
# Return:
#     None     
def stop_alert_system(board):
    board.digital_write(alertPinROV,0)
    board.digital_write(alertPinEnable,0)


# code for testing
if __name__ == "__main__":
    board = pymata4.Pymata4()
    alert_setup(board)
    
    # try:
    #     while True:
    #         lim = 1
    #         print(f"lim rate is {lim}")
    #         rov = 2
    #         print(f"rov is {rov}")
    #         rov_alert(board,rov,lim)
    #         time.sleep(5)
    # except KeyboardInterrupt:
    #     stop_alert_system(board)
    #     board.shutdown()
    tankVolumeStateTime = 0
    timeStart = time.time()
    try:
        while True:
            tank_state_alert(board,"Empty",tankVolumeStateTime)
            print("Tank state is empty")
            time.sleep(1)
            tankVolumeStateTime += 1
    except KeyboardInterrupt:
        board.digital_write(alertPinTankState,0)
        board.digital_write(alertPinTankState5s,0)
