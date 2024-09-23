import threading
import queue
import Format_paquet as FP
import Er
import Et

if __name__ == "__main__":
    fileEt = queue.Queue()
    fileEr = queue.Queue()

    et = Et.Et(fileEr, fileEt)
    er = Er.Er(fileEt, fileEr)

    et.start()
    er.start()
