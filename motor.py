# motor.py
# Operates a bi-directional motor through a L293D motor driver
# Created by: Team MF02 
#           1. SANDRA LO YII SHIN
#           2. ABDUL MAJEED
#           3. TAY MING HUI
#           4. TEOH XHU WEI
#           5. VINCENT LAW YUN KAE
# Last modified: 21 MAY 2023



from pymata4 import pymata4
import time
import system_menu



# motor_setup function is used to setup a 5V DC motor simulate inlet and outlet pumps of the tank.
# Inputs:
#     board - the arduino board used
# Return:
#     None
def motor_setup(board):
  
    global motorPins, en12Pin,pin1A,pin2A
    en12Pin = 10    # PIN1 EN12 pin
    pin1A = 9       # PIN2 1A input
    pin2A = 8       # PIN7 2A input

    global motorSpeedHigh, motorSpeedLow, motorFullSpeed
    motorFullSpeed = 250
    motorSpeedHigh = 175
    motorSpeedLow = 125
    motorPins = [en12Pin,pin1A,pin2A]

    # pin setup 
    for i in range(len(motorPins)):
        if i == 0:
            board.set_pin_mode_pwm_output(motorPins[i])
            board.pwm_write(motorPins[i], 0)
        else:
            board.set_pin_mode_digital_output(motorPins[i])
            board.digital_write(motorPins[i], 0)
            
    print('MOTOR setup complete.')
    print(f'Allocated pins [EN12A, 1A, 2A]: {motorPins}')



# motor_clockwise_control function is used to activate the 5V DC motor to turn in the clockwise direction
# according to the speed "high" or "low"
# Inputs:
#     board - the arduino board used
#     speed - the speed of the motor activation, among high or low or full speed
# Return:
#     None
def motor_clockwise_control(board, speed):

    global pin1A,pin2A,en12Pin
    global motorSpeedHigh, motorSpeedLow, motorFullSpeed

    board.digital_write(pin1A, 0)
    board.digital_write(pin2A, 1)
    time.sleep(0.01)
    if speed == "LOW":
        board.pwm_write(en12Pin, motorSpeedLow)
    elif speed == "HIGH":
        board.pwm_write(en12Pin, motorSpeedHigh)
    else:
        board.pwm_write(en12Pin, motorFullSpeed)

    print(
    f'PUMP ACTIVATED: Motor turning in CLOCKWISE direction and in {speed} speed.')



# motor_anticlockwise_control function is used to activate the 5V DC motor to 
# turn in the anticlockwise direction according to the speed "high" or "low" or "full"
# Inputs:
#     board - the arduino board used
#     speed - the speed of the motor activation, either high or low
# Return:
#     None
def motor_anticlockwise_control(board, speed):

    global pin1A,pin2A,en12Pin
    global motorSpeedHigh, motorSpeedLow, motorFullSpeed

    board.digital_write(pin1A, 1)
    board.digital_write(pin2A, 0)
    time.sleep(0.01)
    if speed == "LOW":
        board.pwm_write(en12Pin, motorSpeedLow)
    elif speed == "HIGH":
        board.pwm_write(en12Pin, motorSpeedHigh)
    else:
        board.pwm_write(en12Pin, motorFullSpeed)

    print(
    f'PUMP ACTIVATED: Motor turning in ANTICLOCKWISE direction and in {speed} speed.')



        
# motor_stop_control function is used to deactivate the 5V DC motor 
# Inputs:
#     board - the arduino board used
# Return:
#     None        
def motor_stop_control(board):

    global pin1A,pin2A,en12Pin
    global motorSpeedHigh, motorSpeedLow

    board.pwm_write(en12Pin, 0)
    print("PUMP DEACTIVATED. MOTOR turning off...")
    time.sleep(0.01)

        

# for individual testing purposes (in case the integration fails)
if __name__ == '__main__':
    
    board = pymata4.Pymata4()
    motor_setup(board)
    while True:
        try:
            motor_anticlockwise_control(board, 'FULL')
            time.sleep(5)
            print("Activated full speed anticlockwise")
            motor_anticlockwise_control(board, 'HIGH') 
            time.sleep(5)
            # motor_anticlockwise_control(board, 'LOW') 
            # time.sleep(3)
            motor_clockwise_control(board,'FULL')
            time.sleep(3)
            motor_clockwise_control(board, 'HIGH')
            time.sleep(3)
            # motor_clockwise_control(board, 'LOW')
            # time.sleep(3)
        except KeyboardInterrupt:
            motor_stop_control(board)
            break

    board.shutdown()