# seven_segment.py
# Displays a required message on the seven segment display and controls the static LED based on the tankVolumeState
# Created by: Team MF02 
#           1. SANDRA LO YII SHIN
#           2. ABDUL MAJEED
#           3. TAY MING HUI
#           4. TEOH XHU WEI
#           5. VINCENT LAW YUN KAE
# Last modified: 21 MAY 2023

from pymata4 import pymata4
import time



charMap = {
    # character segment binary code, segments in order a-g-d.p
    # reference: https://en.wikipedia.org/wiki/Seven-segment_display_character_representations 

    # letter
    "A": "11101110",
    "B": "00111110",
    "C": "10011100",
    "D": "01111010",
    "E": "10011110",
    "F": "10001110",
    "G": "10111100",
    "H": "01101110",
    "I": "10001000",
    "J": "01110000",
    "K": "10101110",
    "L": "00011100",
    "M": "10101010",
    "N": "00101010",
    "O": "00111010",
    "P": "11001110",
    "Q": "11100110",
    "R": "00001010",
    "S": "10110110",
    "T": "00011110",
    "U": "00111000",
    "V": "01111100",
    "W": "01010110",
    "X": "01101110",
    "Y": "01110110",
    "Z": "11010010",

    # numbers
    "0": "11111100",
    "1": "01100000",
    "2": "11011010",
    "3": "11110010",
    "4": "01100110",
    "5": "10110110",
    "6": "10111110",
    "7": "11100000",
    "8": "11111110", 
    "9": "11110110",

    # empty space
    " ": "00000000"
}

digitMap = {
    0: "0111",
    1: "1011",
    2: "1101",
    3: "1110",
    'off': "1111"
}


decimalIndex = 7    # index of decimal bit 


# Sets up the seven-segment display.
# Inputs:
#    board - current Arduino board
# Return:
#     None
def seven_segment_setup(board):
    # 74hc595 sr pins (Arduino digital OUT)
    ser = 5  # PIN14 SER data input
    rclk = 6  # PIN12 RCLK latch/reg clock
    srclk = 7  # PIN11 SRCLK clock
    global ctrlPins
    ctrlPins = [ser, rclk, srclk]
    for pin in ctrlPins:
        board.set_pin_mode_digital_output(pin)
        board.digital_write(pin, 0)


# Function converts a message to be displayed by the seven segment display into a 2D list of binary codes 
# Inputs:
#     strInput - Message to be printed, type str
# Return:
#     segCodes - 2D list of converted binary codes, with each nested list sorted into groups of 4 for printing
def seven_seg_code(strInput):
    msgCodes = []  # list of all binary codes
    segCodes = []  # 2D array for 7seg display codes, sets of 4 (4 digits) or less
    ind = 0

    # converting characters to binary code
    strInput = strInput.upper()
    for char in strInput:
        if char == '.':
            decimalString = msgCodes[ind - 1]
            decimalString = decimalString[:decimalIndex] + "1" + decimalString[decimalIndex+1:]
            msgCodes[ind - 1] = decimalString
        else:
            # append binary code to display list
            msgCodes.append(charMap[char])
        ind += 1

    # generate scrolling text
    tempList = []
    tempMsgList = msgCodes

    if len(msgCodes) >= 4:
        while len(tempMsgList) >= 4:
            # sort into groups of four
            for i in range(4):
                tempList.append(tempMsgList[i])
            tempMsgList.pop(0)
            segCodes.append(tempList)
            tempList = []
    else:
        for i in range(len(msgCodes)):
            tempList.append(tempMsgList[i])
        segCodes.append(tempList)

    # add empty space padding for messages with less than 4 chars
    firstCodeSet = segCodes[0]
    if len(firstCodeSet) < 4:
        for i in range(4 - len(firstCodeSet)):
            firstCodeSet.insert(0, charMap[" "])

    return segCodes

# Writes values to 1 seven-segment display digit through two shift registers
# Inputs:
#     board - current Arduino board
#     segCode - segment code to be written onto display
#     digit - digit of the 4-dig display to write segCode onto
#     tankVolumeState - current state in the water tank
# Return:
#     None
def write_segment(board, segCode, digit,tankVolumeState='Within normal range'):
    # writes the code on each digit
    global ctrlPins
    # push bits into sr
    flashCode = segCode + digitMap[digit]
    if tankVolumeState == 'Low' or tankVolumeState == "High":
        # turn on yellow LED
        flashCode += "100"
    elif tankVolumeState == 'Near empty' or tankVolumeState == "Near full":
        # turn on  red LED
        flashCode += "010"
    elif tankVolumeState == 'Overfull' or tankVolumeState == "Empty":
        # turn on blue LED
        flashCode += "001"
    elif tankVolumeState == "Within normal range":
        # turn off LEDs
        flashCode += "000"

    reversedflashCode = flashCode[::-1] # reverse list 
    
    # writing to 1 digit, 8 seg
    for i in range(len(reversedflashCode)):
  
        board.digital_write(ctrlPins[0], int(reversedflashCode[i]))
        # srclk to push/shift each ser bit
        board.digital_write(ctrlPins[2], 1)
        board.digital_write(ctrlPins[2], 0)
    # rclk (latch) to store all registered bits, displays them
    board.digital_write(ctrlPins[1], 1)
    time.sleep(0.01)  # delay for proper display
    board.digital_write(ctrlPins[1], 0)
    
# Function iterates through the 4 digits of the seven segment display and writes a scrolling display message onto each digit
# Inputs:
#     board - current Arduino board
#     segCodes - 2D array of segment codes to be displayed
#     tankVolumeState - current state in water tank
# Return:
#     None
def write_4_digits_scrolling(board, segCodes,tankVolumeState):
    # display duration for each set, in seconds
    dispDuration = 0.5
    # elapsed duration
    currDuration = 0
    # display scrolling message
    for i in range(len(segCodes)):
        start = time.time()
        while currDuration < dispDuration:
            for j in range(len(segCodes[i])):
                write_segment(board,segCodes[i][j],j,tankVolumeState)
                end = time.time()
                currDuration = end - start
        # reset timer
        currDuration = 0

# Function iterates through the 4 digits of the seven segment display and writes a 4-character message (or less) onto each digit
# Inputs:
#     board - current Arduino board
#     segCodes - 2D array of binary codes to be displayed
#     tankVolumeState - current state in water tank
# Return:
#     None
def write_4_digits_no_scroll(board, segCodes,tankVolumeState):
    # display duration, in seconds
    dispDuration = 1
    # elapsed duration
    currDuration = 0
    # display scrolling message
    start = time.time()
    while currDuration < dispDuration:
        for i in range(len(segCodes[0])):
            write_segment(board, segCodes[0][i], i,tankVolumeState)
        end = time.time()
        currDuration = end - start
    

# Displays the message onto the 4-digit seven segment display
# Inputs: 
#     board - current Arduino board
#     strInput - message string to be displayed
#     tankVolumeState - current state in water tank
# Return:
#     None
def disp_seven_segment(board, strInput,tankVolumeState="Within normal range"):
    segCodes = seven_seg_code(strInput)
    if len(segCodes) > 1:
        write_4_digits_scrolling(board, segCodes,tankVolumeState)
    else:
        write_4_digits_no_scroll(board, segCodes,tankVolumeState)
    time.sleep(0.1)  # process delay before initiating shutdown


# Turn off the seven segment display
# Inputs: 
#     board - current Arduino board
# Return:
#     None
def write_segment_off(board):
    # writes the code on each digit
    global ctrlPins
    # push bits into sr
    # writing to 1 digit, 8 seg
    for i in range(16):
        board.digital_write(ctrlPins[0], 0)
        # srclk to push/shift each ser bit
        board.digital_write(ctrlPins[2], 1)
        board.digital_write(ctrlPins[2], 0)
    # rclk (latch) to store all registered bits, displays them
    board.digital_write(ctrlPins[1], 1)
    board.digital_write(ctrlPins[1], 0)



# for individual testing purposes (in case the integration fails)
if __name__ == '__main__':

    board = pymata4.Pymata4()
    seven_segment_setup(board)
    while True:
        try:
            # disp_seven_segment(board, '12.3L')
            # disp_seven_segment(board, '45.678')
            disp_seven_segment(board, 'abcdefghijklmnopqrstuvwxyz')
            # disp_seven_segment(board, 'GOODBYE')
        except KeyboardInterrupt:
            write_segment_off(board)
            time.sleep(0.5)
            board.shutdown()
