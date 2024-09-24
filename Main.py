import queue
import Format_paquet as FP
import Er
import Et
import random

if __name__ == "__main__":
    addSrc = random.randrange(0,255)

    fileEt = queue.Queue()
    fileEr = queue.Queue()

    et = Et.Et(fileEr, fileEt, addSrc)
    er = Er.Er(fileEt, fileEr, addSrc)

    et.start()
    er.start()


