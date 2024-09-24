from Er import service_manipulation_donnees
import random
import logging

class Service_de_liaison():

    def receive_data_from_Er(self, paquet, addr_source):
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

        # Ecrire reponse dans fichier L_lec.txt
        with open("fichiers/L_lec.txt", "a") as fichier:
            fichier.write(f"la connexion: {_numCon} envoi un paquet, réponse du service de liaison: {reponse}\n")

        return reponse

