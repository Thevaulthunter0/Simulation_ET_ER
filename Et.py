import queue as file
import threading 
import struct as struc

# Permet de donner une variable local seulement aux sous-threads.
# Elle sera utilise pour assigner un numero de connection aux sous-threads.
thread_local = threading.local()
class Et(threading.Thread) :
    def __init__(self, fileEr, fileEt):
        super().__init__()
        self.fileEt = fileEt
        self.fileEr = fileEr

    ## Thread principal Et
    def run(self):
        # Regarder dans le fichier de donnee
        # Si les data ne sont pas assigne a un numero de connexion dans le tableau creer une nouvelle entree et un thread de con
        while True :
            pass

    ## Thread enfant con
    def run_thread_con(self, identifiant) :
        thread_local.identifiant = identifiant
        # Continuellement lire sur la fileEt et regarder si les donnes lui sont addresse avec identifiant_thread et numero de con
        # Dependament des donnees recu effectuer quelque chose.
        # 
        self.lire_Et(thread_local.identifiant)
        while True :
            pass

    ## Pour creer un nouveau thread
    def start_thread_con(self, identifiant_thread) :
        identifiant = identifiant_thread
        thread_con = threading.Thread(target=self.run_thread_con, args=(identifiant,))
        thread_con.start()

    ## permettre de lire les paquets mis dans la file Et
    def lire_Et(self, identifiant_thread) :
        if self.fileEt.empty() == True :
            pass
        else :
            donnee = self.peek_Et(self)
            numCon = int(donnee[0])
            if numCon != identifiant_thread :
                pass
            else :
                return self.fileEt.get()

    ## permettre d'allez mettre un paquet dans la file Er
    def ecrire_Er(self) :
        pass

    ## Permettre de regarger(peek) le premier objet dans la file sans la defiler
    def peek_Et(self) :
        with self.fileEt.mutex :   #Mutex because looking at the data in the queue isnt thread safe
            return self.fileEt.queue[0]

