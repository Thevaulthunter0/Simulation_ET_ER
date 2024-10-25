import json
import queue as file
import threading 
import Service_manipulation_donnees as SMD
import time

# Permet de donner une variable local seulement aux sous-threads.
# Elle sera utilise pour assigner un numero de connection aux sous-threads.
thread_local = threading.local()

class Et(threading.Thread) :
    def __init__(self, fileEr, fileEt, addSrc):
        super().__init__()
        self.fileEt = fileEt
        self.fileEr = fileEr
        self.addSrc = addSrc
        self.compteurCon = 0  # Compteur pour numCon

        #Les différents locking pour le threading
        self.lockFileEt = threading.Lock()
        self.lockFileEr = threading.Lock()
        self.lockS_ecr = threading.Lock()
        self.lockFile = threading.Lock()
        self.lockThread = threading.Lock()
        self.lockCon = threading.Lock()

        #Les différents dictionnaire utilisé pour garder de l'information
        self.tableauFile = {}   #Clé = numCon    valeur = File du thread
        self.tableauThread = {}
        self.tableauConnexion = {}  #Clé = Tuple(id_app, adresse destination)     valeur = tuple(numCon, "Attente de confirmation" ou "connexion établie")

    '''
    Définition : Fonction que le thread principal utilise
    Input : NA
    Output : NA
    '''

    def run(self):
        #mettre les donnees dans une liste de dictionnaire
        data_file = self.read_data_file()
        #Parcourir la liste de dictionnaire(Simule l'envoie de donnee des couches applications)
        while len(data_file) != 0 :
            #Pop l'element
            data = data_file.pop(0)
            #Selon le type de donnee lue
            match data['data'] :
                #Demande de connexion d'un numero d'application et d'un numero de destination
                case 'con' :
                    newNum = self.validation_creation_connexion(data['id_app'],data['id_dest'])
                    if newNum != None :
                        self.compteurCon += 1     #Incrémente le compteur après avoir attribué un numéro
                        #Creer un thread de connexion
                        self.start_thread_con(newNum, data['id_dest'], data['id_app'])
                        time.sleep(0.5)         #Laisser le temps au thread de creer ces entrees dans les tableaux
                        #Envoyer une demande de connexion au thread enfant
                        with self.lockFile :
                            self.tableauFile[newNum].put("con")
                #Demende de deconnexion d'un numero d'application et d'un numero de destination
                case 'decon':
                    existingNumD = self.validation_creation_connexion(data['id_app'],data['id_dest'])
                    if existingNumD != None :
                        #Envoyer une demande de deconnexion au thread enfant
                        with self.lockFile :
                            self.tableauFile[existingNumD].put("decon")
                #Demande d'envoie de data a un numero d'application et d'un numero de destination
                case _ :
                    existingNum = self.validation_creation_connexion(data['id_app'],data['id_dest'])
                    if existingNum != None :
                        #Envoyer des donnees au thread enfant
                        with self.lockFile :
                            self.tableauFile[existingNum].put(data['data'])            
            #time.sleep(10)

        #Joindre tous les thread enfants
        with self.lockThread :
            for thread_id,thread in self.tableauThread.items() :
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
    def run_thread_con(self, numCon, addDest, id_app ) :
        running = True  #Flag pour sortir de la boucle infinie
        thread_local.threadNumCon = numCon      #Numero de connexion attribue a ce thread
        fileT = file.Queue()        #File attribue a ce thread

        #Enregistre sa file dans le tableau de file
        with self.lockFile:
            self.tableauFile[thread_local.threadNumCon] = fileT

        while running :
            #Lire sur sa propre file(FileT)    
            try : 
                donneeT = fileT.get(timeout=1)

                #Donnee de type demande de connexion
                if donneeT == "con" and self.tableauConnexion[(id_app, addDest)][1] == "Attente de confirmation":
                    print(f"{thread_local.threadNumCon} : CON")
                    #Creer un paquet de type n_connect
                    struct_n_connect_req = SMD.service_manipulation_donnees.pack_n_connect(thread_local.threadNumCon,
                        11,self.addSrc,addDest)
                    self.ecrire_Er(11,struct_n_connect_req)

                #Donnee de type demande de déconnexion 
                elif donneeT == "decon" and self.tableauConnexion[(id_app, addDest)][1] == "connexion établie":
                    print(f"{threading.get_ident()} : DECON")   
                    #Creer un paquet de type n_disconnect
                    struct_n_disconnect_req = SMD.service_manipulation_donnees.pack_n_disconnect_req(thread_local.threadNumCon,
                        19,self.addSrc,addDest)
                    self.ecrire_Er(10,struct_n_disconnect_req)

                #Les donnee a transferer a ER
                elif self.tableauConnexion[(id_app, addDest)][1] == "connexion établie" :
                    print(f"{threading.get_ident()} : DATA")  
                    pack_donneet = SMD.service_manipulation_donnees.pack_N_DATA_req(numCon, donneeT)
                    self.ecrire_Er(0,pack_donneet)

            except file.Empty :
                continue

            #Lire sur la fileET
            try :  
                donneeEt = self.lire_Et(id_app,addDest)
                if donneeEt != None :
                    type = donneeEt[0]
                    
                    #Reçoit N_CONNECT_CONF
                    if donneeEt != None:
                        if type == 11 :
                            #Écrire dans fichier réponse
                            self.write_in_response_file("Connexion établie pour " + str(thread_local.threadNumCon))
                            
                        #Reçoit N_DISCONNECT_IND
                        elif type == 15 :
                            #Libérer ressource du thread, tableaux...
                            #Écrire dans fichier réponse
                            running = False
                            del self.tableauFile[thread_local.threadNumCon]
                            del self.tableauConnexion[(id_app, addDest)]
                            self.write_in_response_file("Déconnexion confirmer pour " + str(thread_local.threadNumCon))

            except file.Empty :
                continue

    '''
    Définition : Créer un nouveau thread de connexion
    Input : int threadNumCon, identifiant de la connexion et du thread
            int addDest, identifiant de l'addresse du destinataire
            int id_app, identifiant de l'applicaiton utilisé
    Output : NA
    '''
    def start_thread_con(self, threadNumCon, addDest, id_app) :
        thread_con = threading.Thread(target=self.run_thread_con, args=(threadNumCon,addDest,id_app))
        #Enregistrer le thread dans le tableau des threads(va permettre de join)
        with self.lockThread :
            self.tableauThread[thread_con.ident] = thread_con
        thread_con.start()
    
    '''
    Définition : permettre de défiler première intance de la fileEt 
    Input : int id_app, identifiant de l'application
            int addDest, identifiant de l'addresse du destinataire
    Output : donnee unpack | None
    '''
    def lire_Et(self,id_app,addDest) :
        if self.fileEt.empty() == True :
            pass
        else :
            with self.lockFileEt :
                pack_donnee = self.peek_Et()
            type = pack_donnee[0]
            print(str(pack_donnee))
            match type :
                case 11:
                    unpack_donnee = SMD.service_manipulation_donnees.unpack_comm_etablie(pack_donnee[1])
                    with self.lockCon :
                        self.tableauConnexion[(id_app,addDest)] = (thread_local.threadNumCon, "connexion établie")

                case 15:
                    unpack_donnee = SMD.service_manipulation_donnees.unpack_n_disconnect_ind(pack_donnee[1])
                case 10:
                    unpack_donnee = SMD.service_manipulation_donnees.unpack_n_disconnect_ind(pack_donnee[1])
                case 21:
                    unpack_donnee = SMD.service_manipulation_donnees.unpack_n_akn_pos(pack_donnee[1])
                case __ :
                    return None      
            if unpack_donnee[0] != thread_local.threadNumCon :
                return None
            else :
                
                pop = self.fileEt.get(timeout=1)
                return (type, unpack_donnee)


    '''
    Définition : Permettre d'allez mettre un paquet dans la file Er 
    Input : int type_paquet, le type du paquet
            raw_data, bytes ayant une struct
    Output : NA
    '''
    def ecrire_Er(self, type_paquet ,raw_data) :
        with self.lockFileEr :
            donnee = {"type_paquet" : type_paquet, "data" : raw_data}
            self.fileEr.put(donnee)

    '''
    Définition: Permettre de regarger(peek) le premier objet dans la file sans la defiler
    Input : NA
    Output : Première instance de la file 
    '''
    def peek_Et(self) :
        return self.fileEt.queue[0]
        

    '''
    Définition: Permettre de lire le fichier de données
    Input : NA
    Output : Liste de dictionnaire | None
    '''
    def read_data_file(self):
        try: 
            with open('fichiers/S_lec.json', 'r') as file:
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
    Input : string input_string, le message a écrire dans le fichier
    Outpu : NA
    '''
    def write_in_response_file(self,input_string):
        filename = 'fichiers/S_ecr.txt'  # Chemin du fichier
        with self.lockS_ecr :
            with open(filename, 'a', encoding='utf-8') as file:
                file.write(input_string + "\n")

    '''
    Définition: Vérifie si la connexion existe, sinon il la crée
    Input : int id_app,
            int id_dest
            (id_app, id_dest) = cle
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
