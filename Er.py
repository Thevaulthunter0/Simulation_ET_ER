import threading
import traceback
import time
import queue
import logging

from Service_manipulation_donnees import service_manipulation_donnees

# Logging pour tests
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class Er(threading.Thread):
    def __init__(self, fileET, fileER):
        super().__init__()
        self.fileEr = fileER
        self.fileEt = fileET

        self.tableauConnexion = {}  # Clé = Tuple(id_app, adresse destination)
        self.num_con = 0  # Initialize the connection number
        self.running = True  # Controlleur de thread
        self.lock = threading.Lock()  # Synchro des informations


    def lire_ER(self):
        """
        Définition : Lit les paquets dans la file Er et les traite en fonction du type de paquet.
        Input : NA
        Output : NA
        """
        try:
            while self.running:
                paquet_brut = self.fileEr.get(timeout=0.5)  # Attend paquet
                
                # Traitement du paquet
                type_paquet = paquet_brut.get("type_paquet")
                logging.info(
                    f"TypePaquet={type_paquet}"
                )
                data = paquet_brut.get("data")

                logging.info(f"Raw data before unpacking: {data}")

                if type_paquet == 11:  # N_CONNECT_REQ
                    logging.info(f"Demande de connexion commence: {type_paquet}: {data}")
                    paquet = self.demande_connexion(donnee=data)
                    self.envoyer_ET(paquet)

                elif type_paquet == 15 or type_paquet == 10:  # N_DISCONNECT_REQ
                    logging.info(f"Demande de deconnexion commence: {type_paquet}: {data}")
                    self.liberation_connexion(donnee=data)

                elif type_paquet == 0: # DATA.REQ
                    numCon, donnee = service_manipulation_donnees.unpack_N_DATA_req(data)
                    logging.info(f"envoie de donnee commence: {type_paquet}: {data}")
                    self.transfert_de_donnees(_numCon =numCon, donnee=donnee)

                self.fileEr.task_done()

        except queue.Empty:
            pass
        except Exception as e:
            logging.error(f"Error in lire_ER: {e}, Line: {traceback.format_exc()}")


    def envoyer_ET(self, paquet):
        """
        Définition : Envoie un paquet dans la file Et.
        Input : paquet (données à envoyer)
        Output : NA
        """
        with self.lock:  # Garanti un accès thread-safe aux ressources partagées
            self.fileEt.put(paquet)
            logging.debug(f"Packet sent to fileET: {paquet}")


    def run(self):
        """
        Définition : Méthode principale exécutée lorsque le thread est lancé.
        Input : NA
        Output : NA
        """
        # La méthode va commencer seulement si le threading est débuté
        while self.running:
            self.lire_ER()


    def stop(self):
        """
        Définition : Arrête l'exécution du thread.
        Input : NA
        Output : NA
        """
        self.running = False


    def liberation_connexion(self, donnee):
        """
        Définition : Gère la libération d'une connexion avec le paquet de déconnexion.
        Input : donnee (données de la connexion à libérer)
        Output : NA
        """
        # Crée une instance de la classe Service_de_liaison
        from Service_de_liaison import Service_de_liaison
        service_liaison = Service_de_liaison()  # todo(): Trouver une place ou le mettre

        (
            num_con,
            type_p,
            addr_src,
            addr_dest,
        ) = service_manipulation_donnees.unpack_N_DISCONNECT_REQ(donnee)
        logging.info(
            f"N_DISCONNECT_REQ reçu: NumCon={num_con}, TypePaquet={type_p}, AddrSrc={addr_src},"
            f" AddrDest={addr_dest}"
        )
        paquet_n_disconnect_ind = service_manipulation_donnees.pack_N_DISCONNECT_IND(_numCon=num_con, _AddrSrc=addr_src, _AddrDest=addr_dest,
                                                                                     _Raison=0) # 00000000

        service_liaison.liberation_de_connection(paquet_n_disconnect_ind)


    def demande_connexion(self, donnee):
        """
        Définition : Traite la demande de connexion et crée un paquet de réponse.
        Input : donnee (données de la demande de connexion)
        Output : paquet de connexion ou de refus
        """
        # Crée une instance de la classe Service_de_liaison
        from Service_de_liaison import Service_de_liaison
        service_liaison = Service_de_liaison()
        (
            num_con,
            type_p,
            addr_src,
            addr_dest,
        ) = service_manipulation_donnees.unpack_N_CONNECT_REQ(donnee)
        old_num = num_con
        
        with self.lock:
            _num_con = self.num_con
            self.num_con += 1

        logging.info(
            f"N_CONNECT reçu: NumCon={_num_con}, TypePaquet={type_p}, "
            f"AddrSrc={addr_src}, AddrDest={addr_dest}"
        )

        if addr_src % 27 == 0:  # Refu si l’adresse de la station source est un multiple de 27
            result = (15  ,service_manipulation_donnees.pack_N_DISCONNECT_IND(
                _numCon= old_num,
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

            paquet_appel = service_manipulation_donnees.pack_N_CONNECT_IND(_numCon=_num_con, _AddrSrc=addr_src, _AddrDest=addr_dest)

            # Envoie demande vers couche de liaison
            reponse = service_liaison.demande_conn(data=paquet_appel)

            if reponse:
                packet_type = reponse[1]

                if packet_type == 15:  # Connection established '00001111' = 15
                    _num_con, type_p, addr_src, addr_dest = service_manipulation_donnees.unpack_N_CONNECT_RESP(reponse)
                    result = ( 11 ,service_manipulation_donnees.pack_N_CONNECT_CONF(
                        _numCon=_num_con, _AddrSrc=addr_src, _AddrDest=addr_dest)
                    ,old_num)

                    # Change the state of connection in the tableauConnexion
                    with self.lock:
                        self.tableauConnexion[_num_con]['etat_conn'] = 'etablie'
                        logging.info(f"Connection established: {self.tableauConnexion}")

                elif packet_type == 19:  # Connection refused '00010011' = 19
                    _num_con, type_p, addr_src, addr_dest = service_manipulation_donnees.unpack_N_DISCONNECT_REQ(
                        reponse)
                    result = ( 15, service_manipulation_donnees.pack_N_DISCONNECT_IND(
                        _numCon=old_num, _AddrSrc=addr_src,
                        _AddrDest=addr_dest, _Raison=1) #00000001
                    )



            else:
                _num_con, type_p, addr_src, addr_dest = service_manipulation_donnees.unpack_N_DISCONNECT_REQ(
                    reponse)
                logging.info(f"--------------: {_num_con}")
                result = (15, service_manipulation_donnees.pack_N_DISCONNECT_IND(

                    _numCon=old_num, _AddrSrc=addr_src,

                    _AddrDest=addr_dest, _Raison=1
                )) #00000001


        return result


    def transfert_de_donnees(self, _numCon, donnee):
        """
        Définition : Transfert les données segmentées ou complètes vers la couche de liaison.
        Input : _numCon (numéro de connexion), donnee (données à transférer)
        Output : NA
        """
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
