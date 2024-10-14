import threading
import struct
import traceback
from enum import Enum
import time
import queue
import logging

from Service_de_liaison import Service_de_liaison

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

    # --- Paquet de demande de liberation ---
    N_DISCONNECT_REQ = "!BBBB"

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

        self.tableauConnexion = {}  # Clé = Tuple(id_app, adresse destination)
        self.running = True  # Controlleur de thread
        self.lock = threading.Lock()  # Synchro des informations

    # Lire de transport va permettre de lire les paquets mis dans la file Er
    def lire_ER(self):
        from Service_de_liaison import Service_de_liaison

        try:
            while self.running:
                paquet_brut = self.fileEr.get(timeout=1)  # Attend paquet
                # Traitement du paquet
                type_paquet = paquet_brut.get("type_paquet")
                logging.info(
                    f"TypePaquet={type_paquet}"
                )
                data = paquet_brut.get("data")

                logging.info(f"Raw data before unpacking: {data}")

                if type_paquet == 11:  # N_CONNECT
                    logging.info(f"Demande de connexion commence: {type_paquet}: {data}")
                    paquet = self.demande_connexion(donnee=data)
                    return self.envoyer_ET(paquet)

                elif type_paquet == 15:  # N_DISCONNECT_REQ
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


                elif type_paquet == 0: # DATA.REQ
                    numCon, donnee = "00001010", "11111111111111111"
                    self.transfert_de_donnees(_numCon =numCon, donnee=donnee)

                self.fileEr.task_done()

        except queue.Empty:
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"Error in lire_ER: {e}, Line: {traceback.format_exc()}")


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


    def demande_connexion(self, donnee):
        # Crée une instance de la classe Service_de_liaison
        service_liaison = Service_de_liaison()  # todo(): Trouver une place ou le mettre
        (
            num_con,
            type_p,
            addr_src,
            addr_dest,
        ) = service_manipulation_donnees.unpack_n_connect(donnee)

        logging.info(
            f"N_CONNECT reçu: NumCon={num_con}, TypePaquet={type_p}, "
            f"AddrSrc={addr_src}, AddrDest={addr_dest}"
        )

        if addr_src % 27 == 0:  # Refu si l’adresse de la station source est un multiple de 27
            result = service_manipulation_donnees.pack_n_disconnect_ind(_numCon=num_con,
                                                               _AddrSrc=addr_src, _AddrDest=addr_dest,
                                                               _Raison='00000010')

        else:

            #Todo(): Si le processus ER accepte, il attribue à la demande un numéro de connexion. Il
            # construit ensuite le paquet d’appel. . Il mémorise les informations nécessaires relatives
            # à cette connexion : numéro de connexion, adresse source, adresse destinataire, , état de la
            # connexion (en cours d’établissement ou établie), identifiant d’extrémité de connexion réseau.

            paquet_appel = service_manipulation_donnees.pack_paquet_d_appel(_numCon=num_con, _AddrSrc=addr_src, _AddrDest=addr_dest)

            # Envoie demande vers couche de liaison
            reponse = service_liaison.demande_conn(data=paquet_appel)

            if reponse:
                packet_type = reponse[1]

                if packet_type == '00001111':
                    num_con, type_p, addr_src, addr_dest = service_manipulation_donnees.unpack_comm_etablie(reponse)
                    result = service_manipulation_donnees.pack_comm_etablie(_numCon=num_con, _AddrSrc=addr_src, _AddrDest=addr_dest)

                elif packet_type == '00010011':
                    num_con, type_p, addr_src, addr_dest, raison = service_manipulation_donnees.unpack_n_disconnect_ind(reponse)
                    result = service_manipulation_donnees.pack_n_disconnect_ind(_numCon=num_con, _AddrSrc=addr_src,
                                                                            _AddrDest=addr_dest, _Raison=raison )

            else:
                num_con, type_p, addr_src, addr_dest, raison = service_manipulation_donnees.unpack_n_disconnect_ind(reponse)
                result = service_manipulation_donnees.pack_n_disconnect_ind(_numCon=num_con, _AddrSrc=addr_src,
                                                                            _AddrDest=addr_dest, _Raison=raison)

        return result # Todo(): Je return une primitive en un format de paquet



    def transfert_de_donnees(self, _numCon, donnee):
        # Crée une instance de la classe Service_de_liaison
        service_liaison = Service_de_liaison()  # todo(): Trouver une place ou le mettre

        try:
            # Vérifie si _numCon est défini. Todo: vérifier si _numCon existe dans la table plus tard.
            if _numCon:
                logging.info(f"N_DATA.REQ reçu: NumCon={_numCon}, Donnee={donnee}")
                paquets_segmenter = []

                # Vérifie si la donnée est vide.
                if not donnee:
                    logging.warning(
                        f"N_DATA.REQ reçu: NumCon={_numCon}, Data is empty, Donnee={donnee}"
                    )

                # Vérifie si la donnée est trop longue pour être envoyée.
                elif len(donnee) > 1024:
                    logging.warning(
                        f"Les donnees sont trop longues pour envoyer: NumCon={_numCon}, Donnee={donnee}"
                    )

                # Si la donnée dépasse 128 octets, elle doit être segmentée.
                elif len(donnee) > 128:
                    # Segmente la donnée en paquets.
                    paquets = service_manipulation_donnees.donnee_segmentation(donnee)
                    number_of_paquets = len(paquets)

                    # Parcourt chaque segment et crée les champs nécessaires pour chaque paquet.
                    for i, paquet in enumerate(paquets):
                        # Génère les bits de fin de paquet et de numéro de séquence.
                        m = service_manipulation_donnees.decimal_to_binary(
                            (1 if i < number_of_paquets - 1 else 0), 3
                        )
                        p_s = service_manipulation_donnees.decimal_to_binary(i, 1)
                        p_r = service_manipulation_donnees.decimal_to_binary(
                            (i + 1 if i < number_of_paquets - 1 else i), 3
                        )

                        # Ajoute le paquet segmenté à la liste.
                        paquets_segmenter.append([p_r, m, p_s, paquet])

                # Si la donnée est inférieure à 128 octets, elle est envoyée en un seul bloc.
                else:
                    paquets_segmenter.append(
                        [
                            service_manipulation_donnees.decimal_to_binary(1, 3),  # p_r
                            service_manipulation_donnees.decimal_to_binary(0, 1),  # m
                            service_manipulation_donnees.decimal_to_binary(1, 3),  # p_s
                            donnee,
                        ]
                    )

                # Boucle sur chaque paquet segmenté pour les envoyer.
                for paquet in paquets_segmenter:
                    # Récupère les valeurs du paquet segmenté.
                    p_r, m, p_s, donnee = paquets_segmenter[paquet]

                    logging.info(f"p_r={p_r}, m={m}, p_s={p_s}")

                    ack_received = False
                    retry_count = 0

                    # Essaye d'envoyer le paquet (maximum 2 tentatives : une initiale + une réémission).
                    while not ack_received and retry_count < 2:
                        # PACK les données.
                        paquet_a_envoyer = service_manipulation_donnees.pack_n_data_req(
                            _numCon=_numCon,
                            _numProchainPaquet=p_r,
                            _dernierPaquet=m,
                            _numPaquet=p_s,
                            donnee=donnee,
                        )

                        # Simule un délai de 3 secondes avant l'envoi.
                        time.sleep(3)

                        # Envoie le paquet et reçoit l'accusé de réception.
                        reponse = service_liaison.transfert_donnees(paquet=paquet_a_envoyer, addr_source='15')
                        if reponse is not None:
                            _ack_received, _numCon_received, _num_prochain_attendu = service_manipulation_donnees.unpack_acq_positif_or_negatif(
                                reponse)

                            logging.info(f"_ack_received={_ack_received}, _numCon={_numCon}, _num_prochain_attendu={_num_prochain_attendu}, p_r={p_r}")

                            # Vérifie si l'accusé de réception est correct.
                            if _ack_received and _numCon_received == _numCon and _num_prochain_attendu == p_r:
                                logging.info(f"ack_status: Reçu, retry_count: {retry_count}")
                                break

                        # Si l'accusé n'est pas reçu, retente l'envoi ou échoue après deux tentatives.
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
    def pack_n_disconnect_ind(_numCon, _AddrSrc, _AddrDest, _Raison):
        try:
            # Ensure all arguments are integers
            _numCon = int(_numCon)
            _AddrSrc = int(_AddrSrc)
            _AddrDest = int(_AddrDest)
            _Raison = int(_Raison)

            _typePaquet = '00010011'
            
            return struct.pack(
                Format_paquet.N_DISCONNECT_IND.value,
                _numCon,
                _typePaquet,
                _AddrSrc,
                _AddrDest,
                _Raison,
            )
        except Exception as e:
            logging.error(f"Error in pack_n_disconnect_ind: {e}")
            raise

    @staticmethod
    def unpack_n_disconnect_ind(data):
        return struct.unpack(Format_paquet.N_DISCONNECT_IND.value, data)

    @staticmethod
    def pack_n_disconnect_req(_numCon, _typePaquet, _AddrSrc, _AddrDest):
        return struct.pack(
            Format_paquet.N_DISCONNECT_REQ.value,
            _numCon,
            _typePaquet,
            _AddrSrc,
            _AddrDest,
        )

    @staticmethod
    def unpack_n_disconnect_req(data):
        return struct.unpack(Format_paquet.N_DISCONNECT_REQ.value, data)

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
    def pack_acq_negatif(_numCon, _numProchainAttendu):
        second_byte = (_numProchainAttendu << 5) | 0b01001
        return struct.pack("!BB", _numCon, second_byte)

    @staticmethod
    def unpack_acq_positif_or_negatif(data):
        _numCon, second_byte = struct.unpack("!BB", data)

        # Extraire les 3 bits de gauche pour _numProchainAttendu
        _numProchainAttendu = (second_byte >> 5) & 0b111

        # Extraire les 5 derniers bits
        last_5_bits = second_byte & 0b11111  # Masque pour garder les 5 bits de droite

        # Vérifier si c'est un acquittement positif ou négatif
        if last_5_bits == 0b00001:  # Acquittement positif
            return True, _numCon, _numProchainAttendu
        elif last_5_bits == 0b01001:  # Acquittement négatif
            return False, _numCon, _numProchainAttendu
        else:
            raise ValueError("Données incorrectes : non reconnu comme acquittement positif ou négatif.")


    # Paquet de communication etablie
    @staticmethod
    def pack_comm_etablie(_numCon, _AddrSrc, _AddrDest):
        return struct.pack(
            Format_paquet.N_CONNECT.value, _numCon, '00001111', _AddrSrc, _AddrDest
        )

    @staticmethod
    def unpack_comm_etablie(data):
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    @staticmethod
    def pack_paquet_d_appel(_numCon, _AddrSrc, _AddrDest):
        return struct.pack(
            Format_paquet.N_CONNECT.value, _numCon, '00001011', _AddrSrc, _AddrDest
        )

    @staticmethod
    def unpack_paquet_d_appel(data):
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    @staticmethod
    def unpack_packet_rep_comm(data):
        packet_type = data[1]

        if packet_type == '00001111':
            return service_manipulation_donnees.unpack_comm_etablie(data)
        elif packet_type == '00010011':
            return service_manipulation_donnees.unpack_n_disconnect_ind(data)
        else:
            raise ValueError("Type de paquet inconnu")

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
        "data": service_manipulation_donnees.pack_n_connect(1, 11, 1, 2)
    }
    fileEr.put(packet_n_connect)

    # Donner du temps pour process la commande
    time.sleep(2)

    # Arrete les threads
    thread_er.stop()
    thread_sender.stop()
    thread_er.join()
    thread_sender.join()
