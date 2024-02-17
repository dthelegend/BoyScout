from contextlib import contextmanager
import struct
from fcntl import ioctl
from time import sleep as zzz
import ctypes

TUN_PATH = "/dev/net/tun"

class Tun:
    LINUX_IFF_TUN = 0x0001
    LINUX_IFF_NO_PI = 0x1000
    LINUX_TUNSETIFF = 0x400454CA

    def __init__(self, name, tun_fd) -> None:
        self.tun_fd = tun_fd

        flags = self.LINUX_IFF_TUN | self.LINUX_IFF_NO_PI
        ifs = struct.pack("16sH22s", name, flags, b"")
        ioctl(self.tun_fd, self.LINUX_TUNSETIFF, ifs)

    @staticmethod
    @contextmanager
    def open(name, /, *, tun_path=TUN_PATH):
        tun_file = open(tun_path, "r+b", buffering=0)
        yield Tun(bytes(name, "utf-8"), tun_file)
        tun_file.close()
            
    
    def write(self, *args, **kwargs):
        self.tun_fd.write(*args, **kwargs)
    
    def read(self, *args, **kwargs):
        self.tun_fd.read(*args, **kwargs)

if __name__=="__main__":
    with Tun.open("sfss0") as tunny:
        while True:
            try:
                tunny.write(b"TEST")
                zzz(5)
            except KeyboardInterrupt:
                break