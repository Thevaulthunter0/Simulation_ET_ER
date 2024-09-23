import threading
import struct
from enum import Enum
import time
import queue  # Make sure to import queue
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class Format_paquet(Enum):
    # --- Paquet d'établissement de connexion ---
    N_CONNECT = '!BBBB'

    # --- Refus de connexion et libération de connexion ---
    # --- Refus de connexion et libération de connexion ---
    N_DISCONNECT_IND = '!BBBBB'

    # --- Paquet transfert de données ---
    NUMERO_CON = '!B'
    TYPE_PAQUET = '!B'

    # --- Paquet d'acquittement ---
    N_AKN_POS = '!BB'
    N_AKN_NEG = '!BB'


class Er(threading.Thread):
    def __init__(self, fileET, fileER):
        super().__init__()
        self.fileEr = fileER
        self.fileEt = fileET
        self.running = True  # Contrôle du thread

    # Lire de transport va permettre de lire les paquets mis dans la file Er
    def lire_ER(self):
        try:
            while self.running:
                paquet_brut = self.fileEr.get(timeout=1)  # Attend paquet
                # Traitement du paquet
                type_paquet = paquet_brut.get('type_paquet')
                data = paquet_brut.get('data')

                if type_paquet == 11:  # N_CONNECT
                    num_con, type_p, addr_src, addr_dest = service_manipulation_donnees.unpack_n_connect(data)
                    logging.info(
                        f"N_CONNECT reçu: NumCon={num_con}, TypePaquet={type_p}, "
                        f"AddrSrc={addr_src}, AddrDest={addr_dest}")

                    ack_packet = {
                        'type_paquet': 21,  # Suppose 21 represents ACK
                        'data': service_manipulation_donnees.pack_n_ack(num_con)
                    }
                    self.envoyer_ET(ack_packet)

                elif type_paquet == 15:  # N_DISCONNECT_IND
                    num_con, type_p, addr_src, addr_dest, raison = service_manipulation_donnees.unpack_n_disconnect_ind(
                        data)
                    logging.info(
                        f"N_DISCONNECT_IND reçu: NumCon={num_con}, TypePaquet={type_p}, AddrSrc={addr_src},"
                        f" AddrDest={addr_dest}, Raison={raison}")

                    disconnect_ack = {
                        'type_paquet': 25,
                        'data': service_manipulation_donnees.pack_n_disconnect_ack(num_con)
                    }
                    self.envoyer_ET(disconnect_ack)
                self.fileEr.task_done()
        except queue.Empty:
            pass  # Pas de paquet disponible, continuer

    # Ecrire vers Transport va permettre d'aller mettre un paquet dans la file Et
    def envoyer_ET(self, paquet):
        self.fileEt.put(paquet)
        logging.debug(f"Info envoyé fileET: {paquet}")

    # Thread principal d'Er
    def run(self):
        while self.running:
            self.lire_ER()

    def stop(self):
        self.running = False


class service_manipulation_donnees:
    # Gestion du packing et unpacking des paquets.
    @staticmethod
    def pack_n_data_req(_numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee):
        # Créer la structure Numero CON
        numCon = struct.pack(Format_paquet.NUMERO_CON.value, _numCon)
        # Créer la structure TYPE_PAQUET
        type_paquet = (_numPaquet << 5) | (_dernierPaquet << 4) | (_numProchainPaquet << 1)
        type_paquet_pack = struct.pack(Format_paquet.TYPE_PAQUET.value, type_paquet)
        # Créer la structure de l'information
        if len(donnee) < 128:
            donnee = donnee.ljust(128, b'\x00')
        elif len(donnee) > 128:
            donnee = donnee[:128]  # Tronquer si nécessaire
        return numCon + type_paquet_pack + donnee

    @staticmethod
    def unpack_n_data_req(pack_data, longueur_donnee):
        _numCon = pack_data[0]
        type_paquet = pack_data[1]
        _numPaquet = (type_paquet >> 5) & 0b111
        _dernierPaquet = (type_paquet >> 4) & 0b1
        _numProchainPaquet = (type_paquet >> 1) & 0b111
        donnee = pack_data[2:2 + longueur_donnee]
        return _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee

    @staticmethod
    def pack_n_connect(_numCon, _typePaquet, _AddrSrc, _AddrDest):
        return struct.pack(Format_paquet.N_CONNECT.value, _numCon, _typePaquet,
                           _AddrSrc, _AddrDest)

    @staticmethod
    def unpack_n_connect(data):
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    @staticmethod
    def pack_n_disconnect_ind(_numCon, _typePaquet, _AddrSrc, _AddrDest, _Raison):
        return struct.pack(Format_paquet.N_DISCONNECT_IND.value, _numCon, _typePaquet,
                           _AddrSrc, _AddrDest, _Raison)

    @staticmethod
    def unpack_n_disconnect_ind(data):
        return struct.unpack(Format_paquet.N_DISCONNECT_IND.value, data)

    @staticmethod
    def pack_n_ack(_numCon):
        # Example packing for acknowledgment
        # Define the format as needed
        return struct.pack('!BB', _numCon, 21)  # Example values

    @staticmethod
    def pack_n_disconnect_ack(_numCon):
        # Example packing for disconnect acknowledgment
        # Define the format as needed
        return struct.pack('!BB', _numCon, 25)  # Example values


# Exemple d'utilisation
if __name__ == "__main__":
    # Création des files de messages
    fileEt = queue.Queue()
    fileEr = queue.Queue()

    # Création et démarrage du thread Er
    thread_er = Er(fileEt, fileEr)
    thread_er.start()

    # Exemple de paquet N_CONNECT à envoyer, va rester à l'adapter pour ET
    paquet_n_connect = {
        'type_paquet': 11,  # Correspond à N_CONNECT
        'data': service_manipulation_donnees.pack_n_connect(1, 11, 3, 4)
    }

    # Ajout du paquet à la file Er pour qu'il soit traité par le thread Er
    fileEr.put(paquet_n_connect)

    # Attendre un peu pour que le paquet soit traité
    time.sleep(2)

    # Consommer et afficher les données dans fileEt
    while not fileEt.empty():
        paquet = fileEt.get()
        logging.info(f"Consumed de ET: {paquet}")
        fileEt.task_done()

    # Arrêter les threads
    thread_er.stop()
    thread_er.join()
