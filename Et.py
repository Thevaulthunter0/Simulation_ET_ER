import queue as file
import threading 
import struct as struc

class Et(threading.Thread) :
    def __init__(self, fileEr, fileEt):
        super().__init__()
        self.fileEt = fileEt
        self.fileEr = fileEr

    ## permettre de lire les paquets mis dans la file Et
    def functionX(self) :
        pass

    ## permettre d'allez mettre un paquet dans la file Er
    def functionY(self) :
        pass

    def run(self):
        while True :
            pass