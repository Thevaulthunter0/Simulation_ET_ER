import logging
import struct

from Format_paquet import Format_paquet


class service_manipulation_donnees:
    # Gestion du packing et unpacking des paquets
    """
    Définition : Crée un paquet N_DATA_REQ en empaquetant les données fournies.
    Input : _numCon (int), _numPaquet (int), _dernierPaquet (int), _numProchainPaquet (int), donnee (bytes)
    Output : (bytes) Paquet empaqueté
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
            donnee = donnee.ljust(128, b"\x00")  # Compléter avec des zéros si nécessaire
        elif len(donnee) > 128:
            donnee = donnee[:128]  # Tronquer si nécessaire
        return numCon + type_paquet_pack + donnee

    @staticmethod
    def unpack_n_data_req(pack_data, longueur_donnee):
        """
        Définition : Dépaquetage des données d'un paquet N_DATA_REQ.
        Input : pack_data (bytes), longueur_donnee (int)
        Output : (_numCon (int), _numPaquet (int), _dernierPaquet (int), _numProchainPaquet (int), donnee (bytes))
        """
        _numCon = pack_data[0]  # Extraire le numéro de connexion
        type_paquet = pack_data[1]  # Extraire le type de paquet
        _numPaquet = (type_paquet >> 5) & 0b111  # Extraire le numéro de paquet
        _dernierPaquet = (type_paquet >> 4) & 0b1  # Vérifier si c'est le dernier paquet
        _numProchainPaquet = (type_paquet >> 1) & 0b111  # Extraire le prochain numéro de paquet
        donnee = pack_data[2 : 2 + longueur_donnee]  # Extraire les données
        return _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee

    @staticmethod
    def pack_n_connect(_numCon, _typePaquet, _AddrSrc, _AddrDest):
        """
        Définition : Empaquetage des données de connexion.
        Input : _numCon (int), _typePaquet (int), _AddrSrc (int), _AddrDest (int)
        Output : (bytes) Paquet empaqueté
        """
        return struct.pack(
            Format_paquet.N_CONNECT.value, _numCon, _typePaquet, _AddrSrc, _AddrDest
        )

    @staticmethod
    def unpack_n_connect(data):
        """
        Définition : Dépaquetage des données de connexion.
        Input : data (bytes)
        Output : (_numCon (int), _typePaquet (int), _AddrSrc (int), _AddrDest (int))
        """
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    @staticmethod
    def pack_n_disconnect_ind(_numCon, _AddrSrc, _AddrDest, _Raison):
        """
        Définition : Empaquetage des données de déconnexion (indication).
        Input : _numCon (int), _AddrSrc (int), _AddrDest (int), _Raison (int)
        Output : (bytes) Paquet empaqueté
        """
        try:
            # S'assurer que tous les arguments sont des entiers
            _numCon = int(_numCon)
            _AddrSrc = int(_AddrSrc)
            _AddrDest = int(_AddrDest)
            _Raison = int(_Raison)

            _typePaquet = 19  # '00010011' = 19

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
        """
        Définition : Dépaquetage des données de déconnexion (indication).
        Input : data (bytes)
        Output : (_numCon (int), _AddrSrc (int), _AddrDest (int), _Raison (int))
        """
        return struct.unpack(Format_paquet.N_DISCONNECT_IND.value, data)

    @staticmethod
    def pack_n_disconnect_req(_numCon, _typePaquet, _AddrSrc, _AddrDest):
        """
        Définition : Empaquetage des données de demande de déconnexion.
        Input : _numCon (int), _typePaquet (int), _AddrSrc (int), _AddrDest (int)
        Output : (bytes) Paquet empaqueté
        """
        return struct.pack(
            Format_paquet.N_DISCONNECT_REQ.value,
            _numCon,
            _typePaquet,
            _AddrSrc,
            _AddrDest,
        )

    @staticmethod
    def unpack_n_disconnect_req(data):
        """
        Définition : Dépaquetage des données de demande de déconnexion.
        Input : data (bytes)
        Output : (_numCon (int), _typePaquet (int), _AddrSrc (int), _AddrDest (int))
        """
        return struct.unpack(Format_paquet.N_DISCONNECT_REQ.value, data)

    @staticmethod
    def pack_n_ack(_numCon):
        """
        Définition : Empaquetage des données d'accusé de réception.
        Input : _numCon (int)
        Output : (bytes) Paquet empaqueté
        """
        return struct.pack("!BB", _numCon, 21)  # Pack le numéro de connexion et le type d'accusé

    @staticmethod
    def pack_n_disconnect_ack(_numCon):
        """
        Définition : Empaquetage des données d'accusé de réception de déconnexion.
        Input : _numCon (int)
        Output : (bytes) Paquet empaqueté
        """
        return struct.pack("!BB", _numCon, 25)  # Pack le numéro de connexion et le type d'accusé de déconnexion

    @staticmethod
    def donnee_segmentation(donnees):
        """
        Définition : Segmentation des données en paquets de taille fixe.
        Input : donnees (bytes)
        Output : (list of bytes) Liste de paquets segmentés
        """
        paquets = []
        for i in range(0, len(donnees), 128):
            paquet = donnees[i : i + 128]  # Créer des paquets de 128 bytes
            paquets.append(paquet)
        return paquets

    @staticmethod
    def decimal_to_binary(decimal_num, num_bits):
        """
        Définition : Conversion d'un nombre décimal en binaire.
        Input : decimal_num (int), num_bits (int)
        Output : (str) Représentation binaire sous forme de chaîne
        """
        # Convertir en binaire et enlever le préfixe '0b'
        binary = bin(decimal_num)[2:]

        # Ajouter des zéros au début pour atteindre le nombre de bits souhaité
        return binary.zfill(num_bits)

    @staticmethod
    def pack_N_DATA_ind(
        _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee
    ):
        """
        Définition : Empaquetage des données d'indication N_DATA.
        Input : _numCon (int), _numPaquet (int), _dernierPaquet (int), _numProchainPaquet (int), donnee (bytes)
        Output : (bytes) Paquet empaqueté
        """
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
        """
        Définition : Dépaquetage des données d'un paquet.
        Input : pack_data (bytes)
        Output : (_numCon (int), _numPaquet (int), _dernierPaquet (int), _numProchainPaquet (int), donnee (bytes))
        """
        _numCon = pack_data[0]
        type_paquet = pack_data[1]
        _numPaquet = (type_paquet >> 5) & 0b111
        _dernierPaquet = (type_paquet >> 4) & 0b1
        _numProchainPaquet = (type_paquet >> 1) & 0b111
        donnee = pack_data[2:]
        return _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee

    @staticmethod
    def pack_acq_positif(_numCon, _numProchainAttendu):
        """
        Définition : Empaquetage des données d'acquittement positif.
        Input : _numCon (int), _numProchainAttendu (int)
        Output : (bytes) Paquet empaqueté
        """
        second_byte = (_numProchainAttendu << 5) | 0b00001
        return struct.pack("!BB", _numCon, second_byte)

    @staticmethod
    def pack_acq_negatif(_numCon, _numProchainAttendu):
        """
        Définition : Empaquetage des données d'acquittement négatif.
        Input : _numCon (int), _numProchainAttendu (int)
        Output : (bytes) Paquet empaqueté
        """
        second_byte = (_numProchainAttendu << 5) | 0b01001
        return struct.pack("!BB", _numCon, second_byte)

    @staticmethod
    def unpack_acq_positif_or_negatif(data):
        """
        Définition : Dépaquetage des données d'acquittement positif ou négatif.
        Input : data (bytes)
        Output : (bool, int, int) État de l'acquittement, _numCon, _numProchainAttendu
        """
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
        """
        Définition : Empaquetage des données de communication établie.
        Input : _numCon (int), _AddrSrc (int), _AddrDest (int)
        Output : (bytes) Paquet empaqueté
        """
        return struct.pack(
            Format_paquet.N_CONNECT.value, _numCon, 15, _AddrSrc, _AddrDest     #'00001111' = 15
        )

    @staticmethod
    def unpack_comm_etablie(data):
        """
        Définition : Dépaquetage des données de communication établie.
        Input : data (bytes)
        Output : (_numCon (int), _AddrSrc (int), _AddrDest (int))
        """
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    def pack_paquet_d_appel(_numCon, _AddrSrc, _AddrDest):
        """
        Définition : Empaquetage des données du paquet d'appel.
        Input : _numCon (int), _AddrSrc (int), _AddrDest (int)
        Output : (bytes) Paquet empaqueté
        """
        return struct.pack(
            Format_paquet.N_CONNECT.value, _numCon, 11, _AddrSrc, _AddrDest #'00001011' = 11
        )

    @staticmethod
    def unpack_paquet_d_appel(data):
        """
        Définition : Dépaquetage des données du paquet d'appel.
        Input : data (bytes)
        Output : (_numCon (int), _AddrSrc (int), _AddrDest (int))
        """
        return struct.unpack(Format_paquet.N_CONNECT.value, data)

    @staticmethod
    def unpack_packet_rep_comm(data):
        """
        Définition : Dépaquetage des données de réponse de communication.
        Input : data (bytes)
        Output : (tuple) Résultats du dépaquetage selon le type de paquet
        """
        packet_type = data[1]

        if packet_type == 15:       #'00001111' = 15
            return service_manipulation_donnees.unpack_comm_etablie(data)
        elif packet_type == 19:     #'00010011' = 19
            return service_manipulation_donnees.unpack_n_disconnect_ind(data)
        else:
            raise ValueError("Type de paquet inconnu")

    @staticmethod
    def unpack_N_DATA_req(data):
        """
        Définition : Dépaquetage des données d'une demande N_DATA.
        Input : data (bytes)
        Output : (_numCon (int), _data (bytes))
        """
        _numCon = struct.unpack('B', data[0:1])[0]  # Extraire le premier octet
        _data = data[1:]  # Récupérer le reste des données après le premier octet

        return _numCon, _data

    @staticmethod
    def pack_N_DATA_req(_numCon, _data):
        """
        Définition : Empaquetage des données d'une demande N_DATA.
        Input : _numCon (int), _data (str or bytes)
        Output : (bytes) Paquet empaqueté
        """
        if isinstance(_data, str):
            _data = _data.encode()  # Convertir la chaîne en bytes

        # On empaquette un octet pour le numéro de connexion suivi du paquet de données
        return struct.pack('B', _numCon) + _data