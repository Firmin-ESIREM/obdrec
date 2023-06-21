# OBDrec
Ce projet vise à recréer un tableau de bord automobile, soit en se branchant sur la prise diagnostic OBD d’un véhicule,
soit en rejouant un trajet enregistré, soit en se connectant à un jeu vidéo Forza.


## Mise en route

### Enregistrer et visualiser en direct un trajet en voiture
* Il faudra dans un premier temps se connecter à la prise diagnostic OBD du véhicule à l’aide d’un adaptateur OBD - USB de
type ELM327.
* Il suffit ensuite de lancer le programme `retreive_data.py`. Dès qu’un roulage est détecté, les principales données du
véhicule (vitesse, régime moteur, température d’admission) seront consignées dans un fichier CSV, à la manière d’une
boîte noire.
* Si l’on souhaite visualiser un tableau de bord numérique en direct, il suffit de lancer `dashboard.py` avec l’argument
`live`.
* À la fin du trajet, il suffit d’arrêter les programmes, le CSV sera automatiquement sauvegardé.

__Démonstration :__ [Voir la vidéo sur YouTube](https://youtu.be/MJtWAfzlk-A).

### Rejouer un trajet en voiture
Afin de rejouer un trajet, il suffit de lancer `dashboard.py` avec comme premier argument `replay` et en deuxième
argument le chemin vers le fichier CSV enregistré.

### Visualiser en direct les données extraites d’un jeu vidéo de franchise Forza
* Il faut dans un premier temps activer la transmission UDP des données sur Forza Horizon ou Forza Motorsports
(programme testé sur Forza Horizon 4 et Forza Horizon 5). Pour ce faire, il faut aller dans _Paramètres_, puis _ATH et
gameplay_. Il faudra également y spécifier l’IP de l’ordinateur où le tableau de bord sera exécuté, ainsi qu’un port.
* Il faut ensuite lancer `retreive_data_forza.py` avec pour arguments l’adresse IP puis le port spécifiés dans les
paramètres du jeu.
* On lance enfin `dashboard.py` avec l’argument `live`.

___Attention :__ Forza Horizon et Forza Motorsports sont des marques déposées. Nous ne sommes en aucun cas affiliés à
Xbox Games Studios, Playground Games ou Turn 10 Studios._

## _____
Programme développé par [Gabin Blanchet](mailto:Gabin_Blanchet@etu.u-bourgogne.fr) et
[Firmin Launay](mailto:Firmin_Launay@etu.u-bourgogne.fr), en deuxième année de cycle préparatoire à
l’[ESIREM](https://esirem.u-bourgogne.fr/), dans le cadre du projet de programmation. Ce programme est distribué sous la
[licence MIT](./LICENSE)
