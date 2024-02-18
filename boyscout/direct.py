import serial

from boyscout.__main__ import send

if __name__ == "__main__":
    board = serial.Serial("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0042_95036303235351909121-if00", 9600)

    while True:
        send(board, input("> "))