import json
import queue as file
import threading
import Service_manipulation_donnees as SMD
import time

# Permet de donner une variable local seulement aux sous-threads.
# Elle sera utilise pour assigner un numero de connection aux sous-threads.
thread_local = threading.local()


class Et(threading.Thread):
    def __init__(self, fileEr, fileEt, addSrc):
        super().__init__()
        self.fileEt = fileEt
        self.fileEr = fileEr
        self.addSrc = addSrc
        self.lockFile = threading.Lock()
        self.tableauFile = {}  # Clé = numCon    valeur = File du thread
        self.lockThread = threading.Lock()
        self.tableauThread = {}
        self.lockCon = threading.Lock()
        self.tableauConnexion = {}  # Clé = Tuple(id_app, adresse destination)     valeur = tuple(numCon, "Attente de confirmation" ou "connexion établie")
        self.compteurCon = 0  # Compteur pour numCon

    '''
    Définition : Fonction que le thread principal utilise
    Input : NA
    Output : NA
    '''

    def run(self):
        # ------------ Boucle ----------------------------------------------------------
        # 1. Regarder dans le fichier de donnee -> read_data_file()
        # 2. Regarder le type de donne
        #    - Connexion -> 3.
        #    - Envoie de donnée -> 4.
        #    - Déconnexion -> 5.
        # 3. Si la connexion n'est pas assigne a un numero de connexion dans le tableau -> validation_creation_connexion()
        #   3.1 Ajouter valeur à TableauConnexion                                       -> validation_creation_connexion()
        #   3.2 Creer un thread de con avec start_thread_con(_numCon)                   -->start_thread_con(self, threadNumCon, addDest, id_app)
        #       3.2.1 voir run_thread_con()                                             -->start_thread_con(self, threadNumCon, addDest, id_app)
        # 4. (envoie donnee) Si le numéro de con est deja assignée à une connexion
        #   4.1 Envoyer au bon thread grâce au tableau de thread
        # 5. (Deconnexion) Si le numéro de con est deja assignée à une connexion
        #   5.1 Envoyer au bon thread grâce au tableau de thread
        # ------------------------------------------------------------------------------
        # mettre les donnees dans une liste de dictionnaire
        data_file = self.read_data_file()
        # Parcourir la liste de dictionnaire(Simule l'envoie de donnee des couches applications)
        while len(data_file) != 0:
            # Pop l'element
            data = data_file.pop(0)
            # Selon le type de donnee lue
            match data['data']:
                # Demande de connexion d'un numero d'application et d'un numero de destination
                case 'con':
                    newNum = self.validation_creation_connexion(data['id_app'], data['id_dest'])
                    if newNum != None:
                        self.compteurCon += 1  # Incrémente le compteur après avoir attribué un numéro
                        # Creer un thread de connexion
                        self.start_thread_con(newNum, data['id_dest'], data['id_app'])
                        time.sleep(0.5)  # Laisser le temps au thread de creer ces entrees dans les tableaux
                        # Envoyer une demande de connexion au thread enfant
                        with self.lockFile:
                            print(f"Put Con in {newNum}")
                            self.tableauFile[newNum].put("con")
                # Demende de deconnexion d'un numero d'application et d'un numero de destination
                case 'decon':
                    existingNum = self.validation_creation_connexion(data['id_app'], data['id_dest'])
                    if existingNum != None:
                        # Envoyer une demande de deconnexion au thread enfant
                        with self.lockFile:
                            print(f"Put decon in {existingNum}")
                            self.tableauFile[existingNum].put("decon")
                # Demande d'envoie de date a un numero d'application et d'un numero de destination
                case _:
                    existingNum = self.validation_creation_connexion(data['id_app'], data['id_dest'])
                    if existingNum != None:
                        # Envoyer des donnees au thread enfant
                        with self.lockFile:
                            print(f"Put data in {existingNum}")
                            self.tableauFile[existingNum].put(data['data'])
                            # time.sleep(0.5)

        # Joindre tous les thread enfants
        with self.lockThread:
            for thread_id, thread in self.tableauThread.items():
                print(f"Joining thread {thread_id}")
                thread.join()

        print("Et join")

    '''
    Définition : Fonction que le thread enfant de connexion utilise
    Input : int numCon,
            int addDest,
            int id_app
    Output : NA
    '''

    def run_thread_con(self, numCon, addDest, id_app):
        # -------- Lors de la création --------------------
        # 2.2.1 Creer sa fileT (file thread)    [x]
        # 2.2.2 Creer une entrée dans tableau thread avec threadNumCon comme clé et sa file en valeur    [x]
        # -------------------------------------------------
        # ---------- Boucle -------------------------------------------------------------------------------------------------------
        # 3. lire sur la fileEt et regarder si les donnes lui sont addresse avec threadNumCon et numCon des paquets [x]
        #   3.1 Dépendament des données effectué quelque chose
        #   3.2 Effectue opération dépendament des données reçu de Er
        # 4.Continuellement lire sur sa propre file [x]
        #   4.1 Il reçoit quelque chose sur sa file [x]
        #   4.2 Effectue opération dépendament des données reçu de Et [x]
        # -------------------------------------------------------------------------------------------------------------------------
        running = True  # Flag pour sortir de la boucle infinie
        thread_local.threadNumCon = numCon  # Numero de connexion attribue a ce thread
        fileT = file.Queue()  # File attribue a ce thread

        # Enregistre sa file dans le tableau de file
        with self.lockFile:
            self.tableauFile[thread_local.threadNumCon] = fileT

        while running:
            # Lire sur sa propre file(FileT)
            try:
                donneeT = fileT.get(timeout=1)
                print(f"{threading.get_ident()} getFile : {donneeT}")

                # Donnee de type demande de connexion
                if donneeT == "con" and self.tableauConnexion[(id_app, addDest)][1] == "Attente de confirmation":
                    print(f"{threading.get_ident()} : CON")
                    # Creer un paquet de type n_connect
                    struct_n_connect_req = SMD.service_manipulation_donnees.pack_n_connect(thread_local.threadNumCon,
                                                                                           11, self.addSrc, addDest)
                    self.ecrire_Er(struct_n_connect_req)
                    # -----------------TO REMOVE(WILL ACTUALLY BE DONE IN THE SECTION BELOW(LIRE SUR LA FILEET))---------------------------------------------------------------------------------------------------------------------------
                    self.tableauConnexion[(id_app, addDest)] = (thread_local.threadNumCon, "connexion établie")
                    # -----------------TO REMOVE---------------------------------------------------------------------------------------------------------------------------

                # Donnee de type demande de déconnexion
                elif donneeT == "decon" and self.tableauConnexion[(id_app, addDest)][1] == "connexion établie":
                    print(f"{threading.get_ident()} : DECON")
                    # Creer un paquet de type n_disconnect
                    struct_n_disconnect_ind = SMD.service_manipulation_donnees.pack_n_disconnect_ind(
                        thread_local.threadNumCon,
                        0, self.addSrc, addDest, 1)
                    self.ecrire_Er(struct_n_disconnect_ind)
                    # -----------------TO REMOVE(WILL ACTUALLY BE DONE IN THE SECTION BELOW(LIRE SUR LA FILEET)---------------------------------------------------------------------------------------------------------------------------
                    running = False
                    # -----------------TO REMOVE---------------------------------------------------------------------------------------------------------------------------

                # Les donnee a transferer a ER
                elif self.tableauConnexion[(id_app, addDest)][1] == "connexion établie":
                    print(f"{threading.get_ident()} : DATA")
                    self.ecrire_Er(donneeT)

            except file.Empty:
                continue

            # Lire sur la fileET
            try:
                donneeEt = self.lire_Et(thread_local.threadNumCon)
                # Reçoit N_CONNECT_CONF
                if donneeEt is not None:
                    if len(donneeEt) == 32:
                        # Modifier l'état dans le tableauDeCon
                        # Écrire dans fichier réponse
                        pass
                    # Reçoit N_DISCONNECT_IND
                    elif len(donneeEt) == 40:
                        # Libérer ressource du thread, tableaux...
                        # Écrire dans fichier réponse
                        running = False
                        pass

            except file.Empty:
                continue

    '''
    Définition : Créer un nouveau thread de connexion
    Input : int identifiant de thread
    Output : NA
    '''

    def start_thread_con(self, threadNumCon, addDest, id_app):
        thread_con = threading.Thread(target=self.run_thread_con, args=(threadNumCon, addDest, id_app))
        thread_con.start()
        # Enregistrer le thread dans le tableau des threads(va permettre de join)
        with self.lockThread:
            self.tableauThread[thread_con.ident] = thread_con

    '''
    Définition : permettre de défiler première intance de la fileEt 
    Input : int identifiant du thread
    Output : data
    '''

    def lire_Et(self, identifiant_thread):
        if self.fileEt.empty() == True:
            pass
        else:
            donnee = self.peek_Et()
            numCon = int(donnee[0])
            if numCon != identifiant_thread:
                return None
            else:
                return self.fileEt.get(timeout=1)

    '''
    Définition : Permettre d'allez mettre un paquet dans la file Er 
    Input : raw_data
    Output : NA
    '''

    def ecrire_Er(self, raw_data):
        self.fileEr.put(raw_data)

    '''
    Définition: Permettre de regarger(peek) le premier objet dans la file sans la defiler
    Input : NA
    Output : Première instance de la file 
    '''

    def peek_Et(self):
        with self.fileEt.mutex:
            return self.fileEt.queue[0]

    '''
    Définition: Permettre de lire le fichier de données
    Input : NA
    Output : Liste de dictionnaire | None
    '''

    def read_data_file(self):
        try:
            with open('donnees.json', 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print('File not found.')
            return None
        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return None

    '''
    Définition: Permettre d'écrire dans le fichier de réponse
    Input : input_string 
    Outpu : NA
    '''

    def write_in_response_file(self, input_string):
        # créer le format de donnée à écrire
        data = {'réponse': input_string}
        # écrire les données dans le fichier de réponse
        with open('reponse.txt', 'w') as file:
            json.dump(data, file, indent=4)

    '''
    Définition: Vérifie si la connexion existe, sinon il la crée
    Input : int id_app,
            int id_dest
            Permet de faire la cle de recherche
    Output : int numero de connexion
    '''

    def validation_creation_connexion(self, id_app, id_dest):
        cle = (id_app, id_dest)
        if cle not in self.tableauConnexion:
            self.tableauConnexion[cle] = (self.compteurCon, "Attente de confirmation")
            print(f"Nouvelle connexion pour {id_app} {id_dest} : {self.compteurCon}")
            return self.compteurCon
        else:
            return self.tableauConnexion[cle][0]