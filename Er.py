import threading
import struct
import traceback
from enum import Enum
import time
import queue
import logging



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
        self.num_con = 0  # Initialize the connection number
        self.running = True  # Controlleur de thread
        self.lock = threading.Lock()  # Synchro des informations

    # Lire de transport va permettre de lire les paquets mis dans la file Er
    def lire_ER(self):
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

                elif type_paquet == 15 or type_paquet == 10:  # N_DISCONNECT_REQ
                    logging.info(f"Demande de deconnexion commence: {type_paquet}: {data}")
                    self.liberation_connexion(donnee=data)

                elif type_paquet == 0: # DATA.REQ
                    numCon, donnee = service_manipulation_donnees.unpack_N_DATA_req(data)
                    logging.info(f"envoie de donnee commence: {type_paquet}: {data}")
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

    def liberation_connexion(self, donnee):
        # Crée une instance de la classe Service_de_liaison
        from Service_de_liaison import Service_de_liaison
        service_liaison = Service_de_liaison()  # todo(): Trouver une place ou le mettre

        (
            num_con,
            type_p,
            addr_src,
            addr_dest,
        ) = service_manipulation_donnees.unpack_n_disconnect_req(donnee)
        logging.info(
            f"N_DISCONNECT_REQ reçu: NumCon={num_con}, TypePaquet={type_p}, AddrSrc={addr_src},"
            f" AddrDest={addr_dest}"
        )
        raison = "111"
        paquet_n_disconnect_ind = service_manipulation_donnees.pack_n_disconnect_ind(num_con, addr_src, addr_dest,
                                                                                    raison)

        service_liaison.liberation_de_connection(paquet_n_disconnect_ind)

        """
        # Est-ce qu'on enleve
        disconnect_ack = {
            "type_paquet": 25,
            "data": service_manipulation_donnees.pack_n_disconnect_ack(
                num_con
            ),
        }
        self.envoyer_ET(disconnect_ack)
        """

    def demande_connexion(self, donnee):
        # Crée une instance de la classe Service_de_liaison
        from Service_de_liaison import Service_de_liaison
        service_liaison = Service_de_liaison()  # todo(): Trouver une place ou le mettre
        (
            num_con,
            type_p,
            addr_src,
            addr_dest,
        ) = service_manipulation_donnees.unpack_n_connect(donnee)      #todo: Quelle format sera N_CONNECT.req

        with self.lock:
            self.num_con += 1
            _num_con = self.num_con

        logging.info(
            f"N_CONNECT reçu: NumCon={num_con}, TypePaquet={type_p}, "
            f"AddrSrc={addr_src}, AddrDest={addr_dest}"
        )

        if addr_src % 27 == 0:  # Refu si l’adresse de la station source est un multiple de 27
            result = (15  ,service_manipulation_donnees.pack_n_disconnect_ind(
                _numCon=num_con,
                _AddrSrc=addr_src,
                _AddrDest=addr_dest,
                _Raison=2) #'00000010' = 2
            )

        else:
            # Add the connection to the tableauConnexion
            with self.lock:
                self.tableauConnexion[_num_con] = {
                        'address_source': addr_src,
                        'address_dest': addr_dest,
                        'etat_conn': 'en_cour',
                        'id_ext_conn_res': addr_dest
                    }
                logging.info(f"Connection established: {self.tableauConnexion}")

            paquet_appel = service_manipulation_donnees.pack_paquet_d_appel(_numCon=_num_con, _AddrSrc=addr_src, _AddrDest=addr_dest)

            # Envoie demande vers couche de liaison
            reponse = service_liaison.demande_conn(data=paquet_appel)

            if reponse:
                packet_type = reponse[1]

                if packet_type == 15:  # Connection established '00001111' = 15
                    _num_con, type_p, addr_src, addr_dest = service_manipulation_donnees.unpack_comm_etablie(reponse)
                    result = ( 11 ,service_manipulation_donnees.pack_comm_etablie(
                        _numCon=_num_con, _AddrSrc=addr_src, _AddrDest=addr_dest)
                    )

                    # Change the state of connection in the tableauConnexion
                    with self.lock:
                        self.tableauConnexion[_num_con]['etat_conn'] = 'etablie'
                        logging.info(f"Connection established: {self.tableauConnexion}")

                elif packet_type == 19:  # Connection refused '00010011' = 19
                    _num_con, type_p, addr_src, addr_dest, raison = service_manipulation_donnees.unpack_n_disconnect_ind(
                        reponse)
                    result = ( 15, service_manipulation_donnees.pack_n_disconnect_ind(
                        _numCon=_num_con, _AddrSrc=addr_src,
                        _AddrDest=addr_dest, _Raison=raison)
                    )



            else:
                _num_con, type_p, addr_src, addr_dest, raison = service_manipulation_donnees.unpack_n_disconnect_ind(
                    reponse)
                logging.info(f"--------------: {_num_con}")
                result = (15, service_manipulation_donnees.pack_n_disconnect_ind(

                    _numCon=_num_con, _AddrSrc=addr_src,

                    _AddrDest=addr_dest, _Raison=raison
                ))


        return result # Todo(): Je return une primitive en un format de paquet



    def transfert_de_donnees(self, _numCon, donnee):
        # Crée une instance de la classe Service_de_liaison
        from Service_de_liaison import Service_de_liaison
        service_liaison = Service_de_liaison()  # todo(): Trouver une place ou le mettre

        try:
            # Vérifie si _numCon est défini.
            if _numCon in self.tableauConnexion:
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
                    logging.info(
                        f"Les donnees sont trop longues elles doivents etre segmenter: NumCon={_numCon}, Donnee={donnee}"
                    )
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
                    p_r, m, p_s, donnee = paquet

                    logging.info(f"p_r={p_r}, m={m}, p_s={p_s}")

                    ack_received = False
                    retry_count = 0

                    # Essaye d'envoyer le paquet (maximum 2 tentatives : une initiale + une réémission).
                    while not ack_received and retry_count < 2:
                        logging.info(f"Tentative d'envoi du paquet: {retry_count}")
                        # PACK les données.
                        paquet_a_envoyer = service_manipulation_donnees.pack_N_DATA_ind(
                            _numCon=_numCon,
                            _numProchainPaquet=p_r,
                            _dernierPaquet=m,
                            _numPaquet=p_s,
                            donnee=donnee,
                        )
                        logging.info(f"paquet_a_envoyer: {paquet_a_envoyer}")
                        # Simule un délai de 3 secondes avant l'envoi.
                        time.sleep(3)

                        logging.info(f"table: {self.tableauConnexion[_numCon]}")
                        # Envoie le paquet et reçoit l'accusé de réception.
                        address_source = self.tableauConnexion[_numCon]['address_source']
                        reponse = service_liaison.transfert_donnees(paquet=paquet_a_envoyer, addr_source=address_source)

                        if reponse is not None:
                            _ack_received, _numCon_received, _num_prochain_attendu = service_manipulation_donnees.unpack_acq_positif_or_negatif(
                                reponse)

                            logging.info(f"_ack_received={_ack_received}, _numCon={_numCon}, _num_prochain_attendu={_num_prochain_attendu}, p_r={p_r}")

                            # Vérifie si l'accusé de réception est correct.
                            if _ack_received and _num_prochain_attendu == int(p_r, 2):
                                logging.info(f"ack_status: Reçu, retry_count: {retry_count}")
                                ack_received = True
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

            _typePaquet = 19 #'00010011' = 19
            
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
    def pack_N_DATA_ind(
        _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee
    ):

        # Convertir les paramètres en entiers si ce sont des chaînes
        _numPaquet = int(_numPaquet)
        _dernierPaquet = int(_dernierPaquet)
        _numProchainPaquet = int(_numProchainPaquet)

        # Créer la structure Numero CON
        numCon = struct.pack(Format_paquet.NUMERO_CON.value, _numCon)

        # Créer la structure TYPE_PAQUET
        type_paquet = (
            (_numPaquet << 5) | (_dernierPaquet << 4) | (_numProchainPaquet << 1 | 0)
        )

        type_paquet_pack = struct.pack(Format_paquet.TYPE_PAQUET.value, type_paquet)
        return numCon + type_paquet_pack + donnee

    @staticmethod
    def unpack_paquet_de_donnees(pack_data):
        _numCon = pack_data[0]
        type_paquet = pack_data[1]
        _numPaquet = (type_paquet >> 5) & 0b111
        _dernierPaquet = (type_paquet >> 4) & 0b1
        _numProchainPaquet = (type_paquet >> 1) & 0b111
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

        logging.info(f"_numProchainAttendu:{_numProchainAttendu}, last_5_bits: {last_5_bits}")
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
            Format_paquet.N_CONNECT.value, _numCon, 15, _AddrSrc, _AddrDest     #'00001111' = 15
        )

    @staticmethod
    def unpack_comm_etablie(data):
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    def pack_paquet_d_appel(_numCon, _AddrSrc, _AddrDest):
        return struct.pack(
            Format_paquet.N_CONNECT.value, _numCon, 11, _AddrSrc, _AddrDest #'00001011' = 11
        )

    @staticmethod
    def unpack_paquet_d_appel(data):
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    @staticmethod
    def unpack_packet_rep_comm(data):
        packet_type = data[1]

        if packet_type == 15:       #'00001111' = 15
            return service_manipulation_donnees.unpack_comm_etablie(data)
        elif packet_type == 19:     #'00010011' = 19
            return service_manipulation_donnees.unpack_n_disconnect_ind(data)
        else:
            raise ValueError("Type de paquet inconnu")

    @staticmethod
    def unpack_N_DATA_req(data):
        _numCon = struct.unpack('B', data[0:1])[0]  # Extraire le premier octet
        _data = data[1:]  # Récupérer le reste des données après le premier octet

        return _numCon, _data

    @staticmethod
    def pack_N_DATA_req(_numCon, _data):
        if isinstance(_data, str):
            _data = _data.encode()  # Convertir la chaîne en bytes

        # On empaquette un octet pour le numéro de connexion suivi du paquet de données
        return struct.pack('B', _numCon) + _data


# Exemple d'utilisation
if __name__ == "__main__":
    """Effacer le contenu des fichiers L_ecr.txt et L_lec.txt."""
    with open("fichiers/L_ecr.txt", "w") as fichier:
        pass  # Écrire rien pour vider le fichier
    with open("fichiers/L_lec.txt", "w") as fichier:
        pass  # Écrire rien pour vider le fichier

    # Queue pour les messages de console
    fileEt = queue.Queue()
    fileEr = queue.Queue()

    # Commencer les threads
    thread_er = Er(fileEt, fileEr)
    thread_er.start()

    thread_sender = PacketSender(fileEt)
    thread_sender.start()
    """
    # Envoyer un example de N_CONNECT dans la console
    packet_n_connect = {
        "type_paquet": 11,
        "data": service_manipulation_donnees.pack_n_connect(1, 11, 233, 231)
    }
    fileEr.put(packet_n_connect)

    time.sleep(2)

    # Envoyer un example de N_CONNECT dans la console
    packet_n_connect = {
        "type_paquet": 0,
        "data": service_manipulation_donnees.pack_N_DATA_req(1, '111')
    }
    fileEr.put(packet_n_connect)
    
    time.sleep(2)"""

    # Envoyer un example de N_CONNECT dans la console
    packet_n_connect = {
        "type_paquet": 15,
        "data": service_manipulation_donnees.pack_n_disconnect_req(1, 16, 220, 200)
    }
    fileEr.put(packet_n_connect)

    # Donner du temps pour process la commande
    time.sleep(2)

    # Arrete les threads
    thread_er.stop()
    thread_sender.stop()
    thread_er.join()
    thread_sender.join()