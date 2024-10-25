from Er import service_manipulation_donnees
import random
import logging

class Service_de_liaison():
    def transfert_donnees(self, paquet, addr_source):
        _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee = service_manipulation_donnees.unpack_paquet_de_donnees(paquet)

        self.ecrire_vers_L_lec(f"_numCon:{_numCon}, _numPaquet:{_numPaquet}, _dernierPaquet:{_dernierPaquet}, _numProchainPaquet:{_numProchainPaquet}, donnee:{donnee}")

        logging.info(
            f"Les donnees sont dans le service de liaison: NumCon={_numCon}, _numPaquet:{_numPaquet}, _numProchainPaquet:{_numProchainPaquet}, addr_source:{addr_source} Donnee={donnee}")

        if int(addr_source) % 15 == 0:
            logging.info(
                f"pas de reponse pour le transfert de donnees _numCon: {_numCon}"
            )
            reponse = f"pas de reponse pour le transfert de donnees _numCon: {_numCon}"
            result = None      # Todo(): Est-ce que je devrais return quelque chose ou implementer un timer?

        elif _numPaquet == random.randint(0, 7): # si = a un nombre entre 0 et 7
            reponse = f"Refu pour le transfert de donnees _numCon: {_numCon}"
            result = service_manipulation_donnees.pack_acq_negatif(_numCon=_numCon, _numProchainAttendu=_numPaquet)

        else:
            reponse = f"Acceptation pour le transfert de donnees _numCon: {_numCon}"
            result = service_manipulation_donnees.pack_acq_positif(_numCon=_numCon, _numProchainAttendu=_numProchainPaquet)

        logging.info(
            f"Reponse: {reponse} pour la connexion: {_numCon}")

        # Ecrire reponse dans fichier L_ecr.txt
        self.ecrire_vers_L_ecr(reponse)

        return result

    def demande_conn(self, data):

        _numCon, _typePaquet, _AddrSrc, _AddrDest = service_manipulation_donnees.unpack_paquet_d_appel(data)
        self.ecrire_vers_L_lec(f"_numCon:{_numCon}, _typePaquet:{_typePaquet}, _AddrSrc:{_AddrSrc}, _AddrDest:{_AddrDest}")

        if _AddrSrc % 13 == 0: # refus de connexion
            self.ecrire_vers_L_ecr(f'refus de connexion pour le _numCon{_numCon}')
            result = service_manipulation_donnees.pack_n_disconnect_ind(_numCon=_numCon, _AddrSrc= _AddrSrc, _AddrDest=_AddrDest, _Raison=2)   # Raison '00000010' = 2

        elif _AddrSrc % 19 == 0: # aucune reponse
            self.ecrire_vers_L_ecr(f"aucune reponse pour _numCon {_numCon}")
            result = None

        else:
            self.ecrire_vers_L_ecr(f"Acceptation de la connexion pour _numCon {_numCon}")
            result = service_manipulation_donnees.pack_comm_etablie(_numCon=_numCon, _AddrSrc=_AddrSrc, _AddrDest=_AddrDest)


        return result

    def liberation_de_connection(self, data):
        _numCon, _typePaquet, _AddrSrc, _AddrDest, _raison = service_manipulation_donnees.unpack_n_disconnect_ind(data)
        self.ecrire_vers_L_lec(
        f"_numCon:{_numCon}, _AddrSrc:{_AddrSrc}, _AddrDest:{_AddrDest}, _raison:{_raison}")
        self.ecrire_vers_L_ecr(f"Liberation de la connexion pour _numCon {_numCon}")

    def ecrire_vers_L_ecr(self, message):

        # Ecrire reponse dans fichier L_ecr.txt
        with open("fichiers/L_ecr.txt", "a") as fichier:
            fichier.write(message + "\n")

    def ecrire_vers_L_lec(self, message):

        # Ecrire reponse dans fichier L_ecr.txt
        with open("fichiers/L_lec.txt", "a") as fichier:
            fichier.write(message + "\n")


