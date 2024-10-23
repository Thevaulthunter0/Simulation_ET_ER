import threading
import time
import logging

class PacketSender(threading.Thread):
    def __init__(self, fileET):
        super().__init__()
        self.fileEt = fileET
        self.running = True

    # Méthode exécutée lorsque le thread est démarré
    def run(self):
        while self.running:
            # Vérifie si la file contient des paquets à envoyer
            if not self.fileEt.empty():
                paquet_er = self.fileEt.get()
                # Simule l'envoi du paquet
                logging.info(f"Envoi du paquet depuis fileET : {paquet_er}")
                self.fileEt.task_done()
            time.sleep(1)  # Contrôle la fréquence d'envoi des paquets

    # Arrête le thread en changeant le drapeau 'running'
    def stop(self):
        self.running = False