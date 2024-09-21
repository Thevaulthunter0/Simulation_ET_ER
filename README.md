# Structure #
![Architecture](https://github.com/Thevaulthunter0/Simulation_ET_ER/blob/main/Image/TP1_Diagrammedrawio.png)

# Threading et Queue #
À partir du main, deux threads sont créés. L'un pour la couche réseau et l'autre pour la couche transport. Chaque couche(thread original) devront créer leur threads à chaque fois qu'un nouveau numéro de connexion sera utilisé.

![Threading](https://github.com/Thevaulthunter0/Simulation_ET_ER/blob/main/Image/TP1_DiagrammeThread.drawio.png)

Ce sont les thread enfants des thread Er et Et, par exemple Thread Er con 1, qui doivent lire et écrire dans les files et non les thread principaux(thread Er/Et).

Pour envoyer des données entre couche nous allons les envoyers dans la Queue(file) de l'autre couche pour leur permettre d'y accèder quand bon leur semble.**Les queues de lib/queue sont déja thread-safe!**

Par contre l'accès aux fichier(S_lec, S_ect, L_ect, L_lec) ne sont pas thread-safe.

# Struct #
Dans le fichier Service_manipulation_donnees.py se trouve les fonctions nécessaire pour pack et unpack les différents paquets.
Dans le fichier Format_paquet.py se trouve tous les paquets(définition et attributs) que les couches devront se transmettre.
Par exemple, si je suis "Er" et que je veux envoyer un paquet à "Et", il faut pack les données et puis l'envoyer dans la fileEt. "Et" elle devra unpack pour pouvoir accèder au données voulu.

pack donne des bytes : '\x01\x0f\x03\x04'
unpack donne un tuple : (10,4,9)

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
