from Er import service_manipulation_donnees
import random
import logging

class Service_de_liaison():


    def transfert_donnees(self, paquet, addr_source):
        _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee = service_manipulation_donnees.unpack_n_data_req2(paquet)

        self.ecrire_vers_L_lec(f"{_numCon}{_numPaquet}{_dernierPaquet}{_numProchainPaquet}{donnee}")

        if addr_source % 15 == 0:
            reponse = "pas de reponse"
            result = None      # Todo(): Est-ce que je devrais return quelque chose ou implementer un timer?

        elif _numPaquet == service_manipulation_donnees.decimal_to_binary((random.randint(0, 7)), 3): # si = a un nombre entre 0 et 7
            reponse = "Refu"
            result = service_manipulation_donnees.pack_acq_negatif(_numCon=_numCon, _numProchainAttendu=_numPaquet)

        else:
            reponse = "Acceptation"
            result = service_manipulation_donnees.pack_acq_positif(_numCon=_numCon, _numProchainAttendu=_numProchainPaquet)

        logging.info(
            f"Reponse: {reponse} pour la connexion: {_numCon}")

        # Ecrire reponse dans fichier L_ecr.txt
        self.ecrire_vers_L_lec(reponse)

        return result

    def demande_conn(self, data):

        _numCon, _typePaquet, _AddrSrc, _AddrDest = service_manipulation_donnees.unpack_paquet_d_appel(data)
        self.ecrire_vers_L_lec(f"{_numCon}{_typePaquet}{_AddrSrc}{_AddrDest}")

        if _AddrSrc % 13: # refus de connexion
            self.ecrire_vers_L_ecr('refus de connexion')
            result = service_manipulation_donnees.pack_n_disconnect_ind(_numCon=_numCon, _AddrSrc= _AddrSrc, _AddrDest=_AddrDest, _Raison='00000010')

        elif _AddrSrc % 19: # aucune reponse
            self.ecrire_vers_L_ecr('aucune reponse')
            result = None

        else:
            self.ecrire_vers_L_ecr('Acceptation')
            result = service_manipulation_donnees.pack_comm_etablie(_numCon=_numCon, _AddrSrc=_AddrSrc, _AddrDest=_AddrDest)


        return result

    def ecrire_vers_L_ecr(self, message):

        # Ecrire reponse dans fichier L_ecr.txt
        with open("fichiers/L_ecr.txt", "a") as fichier:
            fichier.write(message)

    def ecrire_vers_L_lec(self, message):

        # Ecrire reponse dans fichier L_ecr.txt
        with open("fichiers/L_lec.txt", "a") as fichier:
            fichier.write(message)


