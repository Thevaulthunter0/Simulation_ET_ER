from Er import service_manipulation_donnees
import random
import logging

class Service_de_liaison():

    def transfert_donnees(self, paquet, addr_source):
        _numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee = service_manipulation_donnees.unpack_n_data_req2(paquet)

        if addr_source % 15:
            reponse = "pas de reponse"

        elif _numPaquet == service_manipulation_donnees.decimal_to_binary((random.randint(0, 7)), 3): # si = a un nombre entre 0 et 7
            reponse = "Refu"
            service_manipulation_donnees.pack_acq_negatif(_numCon=_numCon, _numProchainAttendu=_numPaquet)
            # Envoi de la reponse

        else:
            reponse = "Acceptation"
            service_manipulation_donnees.pack_acq_positif(_numCon=_numCon, _numProchainAttendu=_numProchainPaquet)
            # Envoi de la reponse

        logging.info(
            f"Reponse: {reponse} pour la connexion: {_numCon}")

        # Ecrire reponse dans fichier L_ecr.txt
        self.ecrire_vers_L_ecr(reponse)

        return reponse


    def demande_conn(self, addr_source):

        numCon, _typePaquet, _AddrSrc, _AddrDest, _Raison = 1, 1, 1, 1, " Ouin non"

        if addr_source % 13: # refus de connexion
            service_manipulation_donnees.pack_n_disconnect_ind(_numCon=numCon, _typePaquet=_typePaquet , _AddrSrc= _AddrSrc, _AddrDest=_AddrDest, _Raison=_Raison)
            self.ecrire_vers_L_ecr('refus de connexion')
            pass

        elif addr_source % 19: # aucune reponse
            self.ecrire_vers_L_ecr('aucune reponse')
            pass

        else:
            service_manipulation_donnees.pack_comm_etablie(_numCon=numCon, _AddrSrc=_AddrSrc, _AddrDest=_AddrDest)
            self.ecrire_vers_L_ecr('Acceptation')
            pass


    def ecrire_vers_L_ecr(self, message):

        # Ecrire reponse dans fichier L_ecr.txt

        with open("fichiers/L_ecr.txt", "a") as fichier:
            fichier.write(message)


