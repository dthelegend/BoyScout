import random

import fire
import boyscout
import serial
from enum import IntEnum, Enum
from time import sleep as zzz

from boyscout.semaphore import letter


class State(IntEnum):
    IDLE = 0
    RECEIVING = 1
    TRANSMITTING = 2


def receive(wait=5, time_between_detections=0.5, wilf=None):
    x = receive_helper([], wait, time_between_detections, wilf)
    if x is not None:
        x = x.lower()
    return x


def receive_helper(arr, time_remaining, decrement_by, wilf=None):
    x = letter()
    if x == wilf:
        return x
    elif time_remaining <= 0:
        arr = list(filter(lambda x : x != "-", arr))
        if len(arr) == 0:
            return None
        return max(set(arr), key=arr.count)
    arr.append(x)
    z_time = min(decrement_by, time_remaining)
    zzz(z_time)

    return receive_helper(arr, time_remaining - z_time, decrement_by)


def send(board, mess, time_between=6):
    print("Attempting to send: ", end="")
    for sub_mess in mess.upper():
        print(sub_mess, end="", flush=True)
        board.write(bytes(sub_mess, "utf-8"))
        zzz(time_between)
    print(flush=True)


class ControlSignal(Enum):
    ACK = "u"
    KEEP_ALIVE = "v"
    NOT_ACK = "w"
    RTR = "x"
    RTT = "y"
    FEN = "r"


def main():
    x = boyscout.PySFSSConnection()
    board = serial.Serial("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0042_95036303235351909121-if00", 9600)

    send(board, input("Flag 1 position > ")[:1] + input("Flag 2 position > ")[:1] + "?")

    state = State.IDLE

    while True:
        match state:
            case State.TRANSMITTING:
                print("Transmitting...")
                # Receive frames indiscriminately
                in_bytes = x.read_n(255)
                in_frame_list = boyscout.py_bytes_to_frames(in_bytes)

                # Nothing to send
                if len(in_frame_list) == 0:
                    print("Nothing to transmit")
                    state = State.IDLE
                else:
                    print("Transmitting time")
                    # Send RTT
                    send(board, ControlSignal.RTT.value)
                    # Wait for RTR from friend
                    a = receive(wilf=ControlSignal.RTR.value)
                    if a != ControlSignal.RTR.value:
                        # An error state has been reached!
                        # Return to idling
                        print("Error when attempting to send")
                        state = State.IDLE
                        continue

                    for in_frame in in_frame_list:
                        mess = ''.join(in_frame)
                        # Send frame
                        send(board, mess, time_between=7)

                        # Wait for ack
                        a = receive()
                        if a != ControlSignal.ACK.value:
                            break

                    # Return to idling after send
                    state = State.IDLE

            case State.IDLE:
                print("Idling...")

                # look for a single new packet on the line
                a = receive(wilf=ControlSignal.RTT.value)
                print("Received", a)
                # If Keep-alive
                if a == ControlSignal.KEEP_ALIVE.value:
                    # Here's where the timout logic would be
                    # IF WE HAD ANY!
                    pass
                # If RTT
                elif a == ControlSignal.RTT.value:
                    # Send RTR
                    send(board, ControlSignal.RTR.value)
                    state = State.RECEIVING
                else:
                    # Else an error state has been reached!
                    # Ignore it lol
                    # Send Keep-alive
                    send(board, ControlSignal.KEEP_ALIVE.value)
                    zzz(1)
                    # Attempt to transmit
                    state = State.TRANSMITTING
                    continue

            case State.RECEIVING:
                # Receive from camera and then
                buffer_ultra = []
                frame_no = 255
                while frame_no > 0:
                    buffer = []
                    print("Receiving buffer: ", end="", flush=True)
                    while True:
                        x = receive(wait=7,time_between_detections=1)
                        if x is None:
                            x = "A"
                        buffer.append(x.upper())
                        print(x, end="", flush=True)

                        if x != "Q" or x == ControlSignal.FEN.value.upper() or x == ControlSignal.RTR.value.upper():
                            zzz(random.randint(0,3))
                            break
                    print()

                    (out_data, frame_no) = boyscout.py_frame_to_bytes(''.join(buffer))
                    x.write(out_data)

                    buffer_ultra += buffer

                send(board, buffer_ultra)


if __name__ == "__main__":
    fire.Fire(main)
