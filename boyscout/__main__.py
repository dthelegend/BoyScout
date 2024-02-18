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
    print("Getting letter...")
    x = letter()
    print("Received:", x)
    return x
    # return ControlSignal.KEEP_ALIVE


def send(s):
    print("Attempting to send:", s)


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
                print("Transmitting...")
                # Receive frames indiscriminately
                in_frame_list = boyscout.py_bytes_to_frames(x.read_n(255))

                # Nothing to send
                if len(in_frame_list) == 0:
                    print("Nothing to transmit")
                    state = State.IDLE
                else:
                    print("Transmitting time")
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
                        # Send frame
                        send(mess)

                        # Wait for ack
                        a = receive()
                        if a != ControlSignal.ACK:
                            break

                    # Return to idling after send
                    state = State.IDLE

            case State.IDLE:
                print("Idling...")

                # look for a single new packet on the line
                a = receive()
                # If Keep-alive
                if a == ControlSignal.KEEP_ALIVE:
                    # Here's where the timout logic would be
                    # IF WE HAD ANY!
                    pass
                # If RTT
                elif a == ControlSignal.RTT:
                    # Send RTR
                    send(ControlSignal.RTR)
                    state = State.RECEIVING
                else:
                    # Else an error state has been reached!
                    # Ignore it lol
                    # Send Keep-alive
                    send(ControlSignal.KEEP_ALIVE)
                    zzz(1)
                    # Attempt to transmit
                    state = State.TRANSMITTING
                    continue

            case State.RECEIVING:
                print("Receiving...")
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
