import queue
import Format_paquet as FP
import Er
import Et
import random
from PacketSender import PacketSender

if __name__ == "__main__":
    """Effacer le contenu des fichiers"""
    with open("fichiers/L_ecr.txt", "w") as fichier:
        pass  # Écrire rien pour vider le fichier
    with open("fichiers/L_lec.txt", "w") as fichier:
        pass  # Écrire rien pour vider le fichier
    with open("S_ecr.txt" , "w") as fichier :
        pass 

    addSrc = random.randrange(0,255)

    fileEt = queue.Queue()
    fileEr = queue.Queue()

    et = Et.Et(fileEr, fileEt, addSrc)
    er = Er.Er(fileEt, fileEr)

    thread_sender = PacketSender(fileEt)
    thread_sender.start()

    et.start()
    er.start()

    et.join()
    er.join()
    thread_sender.join()
    print("Main join")
