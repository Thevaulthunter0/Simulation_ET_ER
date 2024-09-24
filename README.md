# Structure #
![Architecture](https://github.com/Thevaulthunter0/Simulation_ET_ER/blob/main/Image/TP1_Diagrammedrawio.png)

# Threading et Queue #
À partir du main, deux threads sont créés. L'un pour la couche réseau et l'autre pour la couche transport. Chaque couche(thread original) devront créer leur threads à chaque fois qu'un nouveau numéro de connexion sera utilisé.

![Threading](https://github.com/Thevaulthunter0/Simulation_ET_ER/blob/main/Image/TP1_DiagrammeThread.drawio.png)

Ce sont les thread enfants des thread Er et Et, par exemple Thread Er con 1, qui doivent lire et écrire dans les files et non les thread principaux(thread Er/Et).

Pour envoyer des données entre couche nous allons les envoyers dans la Queue(file) de l'autre couche pour leur permettre d'y accèder quand bon leur semble.**Les queues de lib/queue sont déja thread-safe!**

Pour savoir qu'elle fonction unpack a utiliser, trouver la taille des donnees. Par exemple, si les donnees ont 32 bits on sait qu'elle sera de primitive N_CONNECT. **Voir Format_paquet.py** pour la taille des differents paquets.

Par contre l'accès aux fichier(S_lec, S_ect, L_ect, L_lec) ne sont pas thread-safe.

# Struct #
Dans le fichier Service_manipulation_donnees.py se trouve les fonctions nécessaire pour pack et unpack les différents paquets.
Dans le fichier Format_paquet.py se trouve tous les paquets(définition et attributs) que les couches devront se transmettre.
Par exemple, si je suis "Er" et que je veux envoyer un paquet à "Et", il faut pack les données et puis l'envoyer dans la fileEt. "Et" elle devra unpack pour pouvoir accèder au données voulu.

pack donne des bytes : '\x01\x0f\x03\x04'
unpack donne un tuple : (10,4,9)

# Déroulement d'une connexion #
1 - "Et" effectue lecture dans S_lec

2 - "Et" envoie une demande de connexion vers "Er"

    - Le numéro de demande + C_CONNECT.req

3 - "Et" mis à jour de la table de connexion et créer un thread pour cette connexion

    - Deux états : Attente de confirmation | connexion établie

4 - "Er" réponse à la demande de connexion 

    - Accepter
        - Attribut à la demande un numéro de connexion et creer un thread pour s'occuper de ce numero de connexion
        - Construit le paquet d'appel
        - "Er" écrit le paquet d'appel dans L-ecr
        - "Er" envoie N_CONNECT.conf à "Et" -> voir étape 5

    - Refus de connexion par le fournisseur de service
        - "Er" envoie libération à "Et" (N_DISCONNECT.ind)
        - "Et" libère les ressource et écrit dans S_ecr
        - fin

    - Refus de la part du distant
        - "Er" envoie libération à "Et" (N_DISCONNECT.ind)
        - "Et" libère les ressource et écrit dans S_ecr
        - fin
        
5 -  "Et" si réception N_CONNECT.conf
    - Modifier état de la connexion

6 - "Et" envoie N_DATA.req à "Er"

7 - "Er" construit le paquet de donnée
    - Segmentation si donnée > 128 bytes

8 - "Er" ecrit les paquets de données dans L-ecr

9 - Réponse reçus (paragraphe 3.5)

10 - "Et" veut libérer connexion.
    - "Et" envoie N_DISCONNECT.req à "ER"
    - "Er" l'écrit dans L-ect


# Setup GitHub #
## 1. Cloner le repo
```
git clone https://github.com/Thevaulthunter0/Simulation_ET_ER
```

## 2. Creer votre branche
```
git checkout -b nom_de_branche
```

## 3. Push vos changement
```
git add .
git commit -m "Description de vos changements"
git push origin nom_de_branche
```
**Seulement push sur votre branches**

## 4. Merger votre branche sur le main
Allez dans la section Pull Request sur github pour en créer une.

## 5. Syncronisation de la branche main
Effectuer régulièrement une syncronisation de la branche main pour pouvoir accèder au nouveau code.
```
git checkout main
git fetch origin
git pull origin main
```

# Documentation #
Threading : https://docs.python.org/3/library/threading.html

Queue : https://docs.python.org/3/library/queue.html

Struct : https://docs.python.org/3/library/struct.html
