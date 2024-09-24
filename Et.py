import json
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

    '''
    Définition : Fonction que le thread principal utilise
    Input : 
    Output :
    '''
    def run(self):
        # Regarder dans le fichier de donnee
        # Si les data ne sont pas assigne a un numero de connexion dans le tableau creer une nouvelle entree et un thread de con
        while True :
            pass

    '''
    Définition : Fonction que le thread enfant connexion utilise
    Input : int identifiant de thread
    Output :
    '''
    def run_thread_con(self, identifiant) :
        thread_local.identifiant = identifiant
        # Continuellement lire sur la fileEt et regarder si les donnes lui sont addresse avec identifiant_thread et numero de con
        # Dependament des donnees recu effectuer quelque chose.
        self.lire_Et(thread_local.identifiant)
        while True :
            pass

    '''
    Définition : Créer un nouveau thread de connexion
    Input : int identifiant de thread
    Output : NA
    '''
    def start_thread_con(self, identifiant_thread) :
        thread_con = threading.Thread(target=self.run_thread_con, args=(identifiant_thread,))
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
        with self.fileEt.mutex :   #Mutex because looking at the data in the queue isnt thread safe
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

