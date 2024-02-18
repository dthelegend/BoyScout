import serial

from boyscout.__main__ import send, ARDUINO

if __name__ == "__main__":
    board = serial.Serial(ARDUINO, 9600)

    while True:
        send(board, input("> "))