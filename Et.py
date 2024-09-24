import queue as file
import threading 
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
        self.tableauThread = {} #Clé = thread_id    valeur = File du thread
        self.tableauConnexion = {}  #Clé = num. de connexion     valeur = tuple(id_app, adresse destination, thread_id, "Attente de confirmation" ou "connexion établie")

    '''
    Définition : Fonction que le thread principal utilise
    Input : 
    Output :
    '''
    def run(self):
        #------------ Boucle ----------------------------------------------------------
        # 1. Regarder dans le fichier de donnee
        # 2. Si les data ne sont pas assigne a un numero de connexion dans le tableau
        #   2.1 Creer un thread de con avec start_thread_con(_numCon)
        #       2.1.1 voir run_thread_con()
        # 3. Si les data sont deja assignée à une connexion envoyer
        #   3.1 Envoyer au bon thread grâce au tableau de thread
        #------------------------------------------------------------------------------
        while True :
            pass

    '''
    Définition : Fonction que le thread enfant connexion utilise
    Input : int numCon
    Output :
    '''
    def run_thread_con(self, threadNumCon) :
        thread_local.threadNumCon = threadNumCon
        #-------- Lors de la création --------------------
        # 2.1.1 Creer sa fileT (file thread)
        # 2.1.2 Creer une entrée dans tableau connexion
        # 2.1.3 Creer une entrée dans tableau thread
        #-------------------------------------------------
        #---------- Boucle -------------------------------------------------------------------------------------------------------
        # 3. lire sur la fileEt et regarder si les donnes lui sont addresse avec threadNumCon et numCon des paquets
        #   3.1 Dépendament des données effectué quelque chose
        #   3.2 Effectue opération dépendament des données reçu de Er
        # 4.Continuellement lire sur sa propre file
        #   4.1 Il reçoit quelque chose sur sa file
        #   4.2 Effectue opération dépendament des données reçu de Et

        #-------------------------------------------------------------------------------------------------------------------------
        self.lire_Et(thread_local.numCon)
        while True :
            pass

    '''
    Définition : Créer un nouveau thread de connexion
    Input : int identifiant de thread
    Output : NA
    '''
    def start_thread_con(self, threadNumCon) :
        thread_con = threading.Thread(target=self.run_thread_con, args=(threadNumCon,))
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
            donnee = self.peek_Et(self)
            numCon = int(donnee[0])
            if numCon != identifiant_thread :
                pass
            else :
                return self.fileEt.get()

    '''
    Définition : Permettre d'allez mettre un paquet dans la file Er 
    Input : à déterminer
    Output : à déterminer
    '''
    def ecrire_Er(self) :
        pass

    '''
    Définition: Permettre de regarger(peek) le premier objet dans la file sans la defiler
    Input : NA
    Output : Première instance de la file 
    '''
    def peek_Et(self) :
        with self.fileEt.mutex :
            return self.fileEt.queue[0]

