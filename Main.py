import queue
import Format_paquet as FP
import Er
import Et
import random
import sys

if __name__ == "__main__":
    #Vérifie l'argument mis en ligne de commande.
    try : 
        if len(sys.argv) > 2 :
            raise ValueError("Veuillez fournir un seul argument entre 0 et 255")
        input = None
        if len(sys.argv) == 2 :
            input = int(sys.argv[1])
            if input < 0 or input > 255 :
                raise ValueError("L'argument doit etre entre 0 et 255")
    except ValueError as error :
        print(f"Erreur : {error}")
        sys.exit(1)

    #Efface le contenue des fichiers
    with open("fichiers/L_ecr.txt", "w") as fichier:
        pass  # Écrire rien pour vider le fichier
    with open("fichiers/L_lec.txt", "w") as fichier:
        pass  # Écrire rien pour vider le fichier
    with open("fichiers/S_ecr.txt" , "w") as fichier :
        pass 
    
    #Décide si l'addresse source est généré aléatoirement ou selon l'input
    if input == None :
        addSrc = random.randrange(0,256)
    else :
        addSrc = input

    #Initialise les queues
    fileEt = queue.Queue()
    fileEr = queue.Queue()

    #Initilialise les objets Et et Er couche transport et couche réseau
    et = Et.Et(fileEr, fileEt, addSrc)
    er = Er.Er(fileEt, fileEr)

    #Debute les threads principales
    et.start()
    er.start()

    #Une fois fini les thread principales sont join
    et.join()
    er.join()
    print("Main join")
