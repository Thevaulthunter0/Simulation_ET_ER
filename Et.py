import json
import queue as file
import threading 
import Service_manipulation_donnees as SMD
import struct
import random

# Permet de donner une variable local seulement aux sous-threads.
# Elle sera utilise pour assigner un numero de connection aux sous-threads.
thread_local = threading.local()

class Et(threading.Thread) :
    def __init__(self, fileEr, fileEt, addSrc):
        super().__init__()
        self.fileEt = fileEt
        self.fileEr = fileEr
        self.addSrc = addSrc
        self.tableauThread = {} #Clé = numCon    valeur = File du thread
        self.tableauConnexion = {}  #Clé = Tuple(id_app, adresse destination)     valeur = tuple(numCon, "Attente de confirmation" ou "connexion établie")

    '''
    Définition : Fonction que le thread principal utilise
    Input : 
    Output :
    '''
    def run(self):
        #------------ Boucle ----------------------------------------------------------
        # 1. Regarder dans le fichier de donnee
        # 2. Regarder le type de donne
        #    - Connexion -> 3.
        #    - Envoie de donnée -> 4.
        #    - Déconnexion -> 5.
        # 3. Si la connexion n'est pas assigne a un numero de connexion dans le tableau
        #   3.1 Ajouter valeur à TableauConnexion
        #   3.2 Creer un thread de con avec start_thread_con(_numCon)
        #       3.2.1 voir run_thread_con()
        # 4. Si le numéro de con est deja assignée à une connexion
        #   4.1 Envoyer au bon thread grâce au tableau de thread
        # 5. Si le numéro de con est deja assignée à une connexion
        #   5.1 Envoyer au bon thread grâce au tableau de thread 
        #------------------------------------------------------------------------------
        while True :

            pass

    '''
    Définition : Fonction que le thread enfant connexion utilise
    Input : int numCon
    Output :
    '''
    def run_thread_con(self, numCon, addDest, id_app ) :
        #-------- Lors de la création --------------------
        # 2.2.1 Creer sa fileT (file thread)    [x]
        # 2.2.2 Creer une entrée dans tableau thread avec threadNumCon comme clé et sa file en valeur    [x]
        #-------------------------------------------------
        #---------- Boucle -------------------------------------------------------------------------------------------------------
        # 3. lire sur la fileEt et regarder si les donnes lui sont addresse avec threadNumCon et numCon des paquets [x]
        #   3.1 Dépendament des données effectué quelque chose
        #   3.2 Effectue opération dépendament des données reçu de Er
        # 4.Continuellement lire sur sa propre file [x]
        #   4.1 Il reçoit quelque chose sur sa file [x]
        #   4.2 Effectue opération dépendament des données reçu de Et [x]
        #-------------------------------------------------------------------------------------------------------------------------

        thread_local.threadNumCon = numCon
        fileT = file.Queue()
        self.tableauThread[thread_local.threadNumCon] = fileT
        addDest = addDest 

        while True :
            #Lire sur la fileET
            try : 
                donneeEt = self.lire_Et(thread_local.threadNumCon)
                #Reçoit N_CONNECT_CONF
                if donneeEt is not None:
                    if len(donneeEt) == 32 :
                        #Modifier l'état dans le tableauDeCon
                        #Écrire dans fichier réponse
                        print("donneEt connexion")
                        pass
                    #Reçoit N_DISCONNECT_IND
                    elif len(donneeEt) == 40 :
                        #Libérer ressource du thread, tableaux...
                        #Écrire dans fichier réponse
                        print("donneEt disconnect")
                        pass

            except file.Empty :
                continue
        
            #Lire sur sa propre file(FileT)    
            try : 
                donneeT = fileT.get(timeout = 1)

                #Donnee de type demande de connexion
                if donneeT == "con" and self.tableauConnexion[(id_app, addDest)][1] == "connexion établie":  
                    struct_n_connect_req = SMD.service_manipulation_donnees.pack_n_connect(thread_local.threadNumCon,
                            11,self.addSrc,addDest,0)
                    self.ecrire_Er(struct_n_connect_req)

                #Donnee de type demande de déconnexion 
                elif donneeT == "decon" and self.tableauConnexion[(id_app, addDest)][1] == "connexion établie": 
                    struct_n_disconnect_ind = SMD.service_manipulation_donnees.pack_n_disconnect_ind(thread_local.threadNumCon,
                        0,self.addSrc,addDest,1)
                    self.ecrire_Er(struct_n_disconnect_ind)

                #Donnee a transferer a ER
                elif self.tableauConnexion[(id_app, addDest)][1] == "connexion établie" : 
                    self.ecrire_Er(donneeT)

            except file.Empty :
                continue
        pass
    '''
    Définition : Créer un nouveau thread de connexion
    Input : int identifiant de thread
    Output : NA
    '''
    def start_thread_con(self, threadNumCon, addDest, id_app) :
        thread_con = threading.Thread(target=self.run_thread_con, args=(threadNumCon,addDest,id_app))
        thread_con.start()

    
    '''
    Définition : permettre de défiler première intance de la fileEt 
    Input : int identifiant du thread
    Output : à déterminer 
    '''
    def lire_Et(self, identifiant_thread) :
        if self.fileEt.empty() == True :
            pass
        else :
            donnee = self.peek_Et()
            numCon = int(donnee[0])
            if numCon != identifiant_thread :
                return None
            else :
                return self.fileEt.get(timeout = 1)

    '''
    Définition : Permettre d'allez mettre un paquet dans la file Er 
    Input : à déterminer
    Output : à déterminer
    '''
    def ecrire_Er(self, raw_data) :
        print("ecrireEr")
        self.fileEr.put(raw_data)

    '''
    Définition: Permettre de regarger(peek) le premier objet dans la file sans la defiler
    Input : NA
    Output : Première instance de la file 
    '''
    def peek_Et(self) :
        with self.fileEt.mutex :
            return self.fileEt.queue[0]
        

    '''
    Définition: Permettre de lire le fichier de données
    '''
    def read_data_file():
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
    Définition: Permettre d'écrire dans le fichier de données
    '''
    def write_in_data_file(data, file_path='donnees.json'):   
        try:
            #tentative de lecture
            with open(file_path, 'r') as file:
                dataInFile = json.load(file)
        except FileNotFoundError:
            # dans le cas que le fichier n'existe pas
            dataInFile = []
        # Ajout des données à écrire 
        dataInFile.append(data)
        # Écriture dans le fichier
        with open(file_path, 'w') as file:
            json.dump(dataInFile, file, indent=4)
    '''
    Définition: Permettre d'écrire dans le fichier de réponse
    '''
    def write_in_response_file(input_string):
        # créer le format de donnée à écrire
        data = {'réponse' : input_string}
        # écrire les données dans le fichier de réponse
        with open('reponse.txt', 'w') as file:
            json.dump(data, file, indent=4)

