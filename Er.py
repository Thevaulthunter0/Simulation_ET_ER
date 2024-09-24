import queue as file
import threading 
import struct as struc

class Er(threading.Thread):
    def __init__(self, fileEt, fileEr,addSrc):
        super().__init__()
        self.fileEr = fileEr
        self.fileEt = fileEt
        self.addSrc = addSrc

    ##Lire de transport va permettre de lire les paquets mis dans la file Er
    def functionX(self) :
        
        pass

    ##Ecrire vers Transport va permettre d'allez mettre un paquet dans la file Et
    def functionY(self) :
        pass

    ## Thread principal d'Er
    def run(self):
        while True :
            pass