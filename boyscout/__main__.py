import fire
import boyscout
from enum import IntEnum, Enum
from time import sleep as zzz

from boyscout.semaphore import letter


class State(IntEnum):
    IDLE = 0
    RECEIVING = 1
    TRANSMITTING = 2


def receive():
    # letter()
    return ControlSignal.KEEP_ALIVE


def send(s):
    pass


class ControlSignal(Enum):
    ACK = "u"
    KEEP_ALIVE = "v"
    NOT_ACK = "w"
    RTR = "x"
    RTT = "y"
    FEN = "r"


def main():
    x = boyscout.PySFSSConnection()
    state = State.IDLE

    while True:
        match state:
            case State.TRANSMITTING:
                # Receive frames indiscriminately
                in_frame_list = boyscout.py_bytes_to_frames(x.read_n(255))

                # Nothing to send
                if len(in_frame_list) == 0:
                    state = State.IDLE
                else:
                    # Send RTT
                    send(ControlSignal.RTT)
                    # Wait for RTR from friend
                    a = receive()
                    if a != ControlSignal.RTR:
                        # An error state has been reached!
                        # Return to idling
                        print("Error when attempting to send")
                        state = State.IDLE
                        continue

                    for in_frame in in_frame_list:
                        mess = ''.join(in_frame)
                        print(mess)
                        # Send frame
                        send(mess)

                        # Wait for ack
                        a = receive()
                        if a != ControlSignal.ACK:
                            break

                    # Return to idling after send
                    state = State.IDLE

            case State.IDLE:
                # Must send a keep-alive

                # look for a single new packet on the line
                a = receive()
                # If Keep-alive
                if a == ControlSignal.KEEP_ALIVE:
                    # Send Keep-alive
                    send(ControlSignal.KEEP_ALIVE)
                    print("Idling...")
                    zzz(5)
                    # Attempt to transmit
                    state = State.TRANSMITTING

                # If RTT
                elif a == ControlSignal.RTT:
                    # Send RTR
                    send(ControlSignal.RTR)
                    state = State.RECEIVING
                else:
                    # Else an error state has been reached!
                    # Ignore it lol
                    continue

            case State.RECEIVING:
                # Receive from camera and then
                buffer_ultra = []
                frame_no = 255
                while frame_no > 0:
                    buffer = []
                    while True:
                        x = letter()
                        buffer.append(x)

                        if x == ControlSignal.FEN:
                            break

                    (out_data, frame_no) = boyscout.py_frame_to_bytes(buffer)
                    x.write(out_data)

                    buffer_ultra += buffer

                send(buffer_ultra)

if __name__ == "__main__":
    fire.Fire(main)
