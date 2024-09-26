import threading
import struct
from enum import Enum
import time
import queue
import logging

import os

# Logging pour tests
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Format_paquet(Enum):
    # --- Paquet d'établissement de connexion ---
    N_CONNECT = "!BBBB"

    # --- Refus de connexion et libération de connexion ---
    # --- Refus de connexion et libération de connexion ---
    N_DISCONNECT_IND = "!BBBBB"

    # --- Paquet transfert de données ---
    NUMERO_CON = "!B"
    TYPE_PAQUET = "!B"

    # --- Paquet d'acquittement ---
    N_AKN_POS = "!BB"
    N_AKN_NEG = "!BB"


class Er(threading.Thread):
    def __init__(self, fileET, fileER):
        super().__init__()
        self.fileEr = fileER
        self.fileEt = fileET
        self.running = True  # Controlleur de thread
        self.lock = threading.Lock()  # Synchro des informations

    # Lire de transport va permettre de lire les paquets mis dans la file Er
    def lire_ER(self):
        try:
            while self.running:
                paquet_brut = self.fileEr.get(timeout=1)  # Attend paquet
                # Traitement du paquet
                type_paquet = paquet_brut.get("type_paquet")
                data = paquet_brut.get("data")

                if type_paquet == 11:  # N_CONNECT
                    (
                        num_con,
                        type_p,
                        addr_src,
                        addr_dest,
                    ) = service_manipulation_donnees.unpack_n_connect(data)
                    logging.info(
                        f"N_CONNECT reçu: NumCon={num_con}, TypePaquet={type_p}, "
                        f"AddrSrc={addr_src}, AddrDest={addr_dest}"
                    )

                    ack_packet = {
                        "type_paquet": 21,  # Suppose 21 represents ACK
                        "data": service_manipulation_donnees.pack_n_ack(num_con),
                    }
                    self.envoyer_ET(ack_packet)

                elif type_paquet == 15:  # N_DISCONNECT_IND
                    (
                        num_con,
                        type_p,
                        addr_src,
                        addr_dest,
                        raison,
                    ) = service_manipulation_donnees.unpack_n_disconnect_ind(data)
                    logging.info(
                        f"N_DISCONNECT_IND reçu: NumCon={num_con}, TypePaquet={type_p}, AddrSrc={addr_src},"
                        f" AddrDest={addr_dest}, Raison={raison}"
                    )

                    disconnect_ack = {
                        "type_paquet": 25,
                        "data": service_manipulation_donnees.pack_n_disconnect_ack(
                            num_con
                        ),
                    }
                    self.envoyer_ET(disconnect_ack)
                self.fileEr.task_done()
        except queue.Empty:
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"Error in lire_ER: {e}")

    # Ecrire vers Transport va permettre d'aller mettre un paquet dans la file Et
    def envoyer_ET(self, paquet):
        with self.lock:  # Garanti un accès thread-safe aux ressources partagées
            self.fileEt.put(paquet)
            logging.debug(f"Packet sent to fileET: {paquet}")

    # Thread principal d'Er
    def run(self):
        # La méthode va commencer seulement si le threading est débuté
        while self.running:
            self.lire_ER()

    def stop(self):
        self.running = False

    def receiving_data_from_ET(self):
        try:
            _numCon, donnee = "00001010", "11111111111111111"

            if (
                _numCon
            ):  # vérifier si _numCon est dans la table lorsque la table aura ete implementer
                logging.info(f"N_DATA.REQ reçu: NumCon={_numCon}, Donnee={donnee}")
                paquets_segmenter = []

                if len(donnee) > 1024:
                    logging.warning(
                        f"Les donnees sont trop longues pour envoyer: NumCon={_numCon}, Donnee={donnee}"
                    )

                elif len(donnee) > 128:
                    paquets = service_manipulation_donnees.donnee_segmentation(donnee)
                    number_of_paquets = len(paquets)

                    for i, paquet in enumerate(paquets):
                        m = service_manipulation_donnees.decimal_to_binary(
                            (1 if i < number_of_paquets - 1 else 0), 3
                        )
                        p_s = service_manipulation_donnees.decimal_to_binary(i, 1)
                        p_r = service_manipulation_donnees.decimal_to_binary(
                            (i + 1 if i < number_of_paquets - 1 else i), 3
                        )

                        paquets_segmenter.append([p_r, m, p_s, paquet])

                elif not donnee:
                    logging.warning(
                        f"N_DATA.REQ reçu: NumCon={_numCon}, Data is empty, Donnee={donnee}"
                    )

                else:
                    paquets_segmenter.append(
                        [
                            service_manipulation_donnees.decimal_to_binary(1, 3),  # p_r
                            service_manipulation_donnees.decimal_to_binary(0, 1),  # m
                            service_manipulation_donnees.decimal_to_binary(1, 3),  # p_s
                            donnee,
                        ]
                    )

                for paquet in paquets_segmenter:
                    p_r, m, p_s, donnee = paquets_segmenter[paquet]

                    ack_received = False
                    retry_count = 0

                    while (
                        not ack_received and retry_count < 2
                    ):  # Une tentative initiale + une réémission
                        service_manipulation_donnees.pack_n_data_req(
                            _numCon=_numCon,
                            _numProchainPaquet=p_r,
                            _dernierPaquet=m,
                            _numPaquet=p_s,
                            donnee=donnee,
                        )

                        # Fonction pour envoyer a la couche liaison le paquet parametre = (paquet, addr_source)
                        time.sleep(5)

                        # ack_received = reponse de la fonction pour recevoir la reponse de la couche liaison

                        if ack_received:
                            logging.info(f"ack_status: Recu retry_count: {retry_count}")
                            break

                        if not ack_received:
                            if retry_count == 0:
                                logging.warning(f"Réémission du paquet")
                                retry_count += 1
                            else:
                                logging.error(
                                    f"Échec de l'émission du paquet après une tentative de réémission"
                                )
                                break

            else:
                logging.warning(f"NumCon non trouvé: {_numCon}")

        except Exception as e:
            logging.error(f"Une erreur inattendue s'est produite: {e}")

        return "Data"


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


class service_manipulation_donnees:
    # Gestion du packing et unpacking des paquets.

    """
    Because N_DATA_REQ is a complexe structure(a struct insine of a struct)
    We need to create it by combining multiples structure.
    _numCon need to be a 8 bits integer
    _numPaquet need to be 3 bits integer
    _dernierPaquet need to be 1 bit integer
    _numProchainPaquet need to be 3 bits integer
    data need to be smaller or equal to 128 Bytes and of type bytes
    """

    @staticmethod
    def pack_n_data_req(
        _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee
    ):
        # Créer la structure Numero CON
        numCon = struct.pack(Format_paquet.NUMERO_CON.value, _numCon)
        # Créer la structure TYPE_PAQUET
        type_paquet = (
            (_numPaquet << 5) | (_dernierPaquet << 4) | (_numProchainPaquet << 1)
        )
        type_paquet_pack = struct.pack(Format_paquet.TYPE_PAQUET.value, type_paquet)
        # Créer la structure de l'information
        if len(donnee) < 128:
            donnee = donnee.ljust(128, b"\x00")
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
        donnee = pack_data[2 : 2 + longueur_donnee]
        return _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee

    @staticmethod
    def pack_n_connect(_numCon, _typePaquet, _AddrSrc, _AddrDest):
        return struct.pack(
            Format_paquet.N_CONNECT.value, _numCon, _typePaquet, _AddrSrc, _AddrDest
        )

    @staticmethod
    def unpack_n_connect(data):
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    @staticmethod
    def pack_n_disconnect_ind(_numCon, _typePaquet, _AddrSrc, _AddrDest, _Raison):
        return struct.pack(
            Format_paquet.N_DISCONNECT_IND.value,
            _numCon,
            _typePaquet,
            _AddrSrc,
            _AddrDest,
            _Raison,
        )

    @staticmethod
    def unpack_n_disconnect_ind(data):
        return struct.unpack(Format_paquet.N_DISCONNECT_IND.value, data)

    @staticmethod
    def pack_n_ack(_numCon):
        # Example packing for acknowledgment
        # Define the format as needed
        return struct.pack("!BB", _numCon, 21)  # Example values

    @staticmethod
    def pack_n_disconnect_ack(_numCon):
        # Example packing for disconnect acknowledgment
        # Define the format as needed
        return struct.pack("!BB", _numCon, 25)  # Example values

    @staticmethod
    def donnee_segmentation(donnees):
        paquets = []
        for i in range(0, len(donnees), 128):
            paquet = donnees[i : i + 128]
            paquets.append(paquet)
        return paquets

    @staticmethod
    def decimal_to_binary(decimal_num, num_bits):
        # Convertir en binaire et enlever le préfixe '0b'
        binary = bin(decimal_num)[2:]

        # Ajouter des zéros au début pour atteindre le nombre de bits souhaité
        return binary.zfill(num_bits)

    @staticmethod
    def pack_n_data_req2(
        _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee
    ):
        # Créer la structure Numero CON
        numCon = struct.pack(Format_paquet.NUMERO_CON.value, _numCon)
        # Créer la structure TYPE_PAQUET
        type_paquet = (
            (_numPaquet << 5) | (_dernierPaquet << 4) | (_numProchainPaquet << 1)
        )
        type_paquet_pack = struct.pack(Format_paquet.TYPE_PAQUET.value, type_paquet)
        return numCon + type_paquet_pack + donnee

    @staticmethod
    def unpack_n_data_req2(pack_data):
        _numCon = pack_data[0]
        type_paquet = pack_data[1]
        _numPaquet = (type_paquet >> 5) & 0b111
        _dernierPaquet = (type_paquet >> 4) & 0b1
        _numProchainPaquet = (type_paquet) & 0b111
        donnee = pack_data[2:]
        return _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee

    @staticmethod
    def pack_acq_positif(_numCon, _numProchainAttendu):
        second_byte = (_numProchainAttendu << 5) | 0b00001
        return struct.pack("!BB", _numCon, second_byte)

    @staticmethod
    def unpack_acq_positif():
        pass

    @staticmethod
    def pack_acq_negatif(_numCon, _numProchainAttendu):
        second_byte = (_numProchainAttendu << 5) | 0b01001
        return struct.pack("!BB", _numCon, second_byte)

    @staticmethod
    def unpack_acq_negatif():
        pass


# Exemple d'utilisation
if __name__ == "__main__":
    # Queue pour les messages de console
    fileEt = queue.Queue()
    fileEr = queue.Queue()

    # Commencer les threads
    thread_er = Er(fileEt, fileEr)
    thread_er.start()

    thread_sender = PacketSender(fileEt)
    thread_sender.start()

    # Envoyer un example de N_CONNECT dans la console
    packet_n_connect = {
        "type_paquet": 11,
        "data": service_manipulation_donnees.pack_n_connect(1, 1, 1, 2)
    }
    fileEr.put(packet_n_connect)

    # Donner du temps pour process la commande
    time.sleep(2)

    # Arrete les threads
    thread_er.stop()
    thread_sender.stop()
    thread_er.join()
    thread_sender.join()
