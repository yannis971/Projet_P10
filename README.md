# Projet_P10
## Créer une API sécurisée RESTful en utilisant Django REST
### 1) Description de l'application

Ce projet consiste à développer une API sécurisée, pour le compte de la société SoftDesk, permettant d’accéder à une application de suivi de développement logiciel


#### 1.1) Frameworks utilisés

* **Django** : pour le développement de sites web en Python
* **Django REST Framework** : pour concevoir des sites web "responsive" avec des thèmes intégrés

#### 1.2) Langage utilisé

* **Python** : le langage de programmation interprété, multi-paradigmes et multiplateformes (classé N° 3 à l'index TIOBE en avril 2021), pour impléter la logique de l'application

#### 1.3) Packages supplémentaires

* **djangorestframework-jwt** : package pour gérer l'authentification via des JSON Web Token (JWT)
* **drf-nested-routers** : package pour gérer la redirection vers des View Set dans des "routers" imbriqués

### 2) Architecture du projet

![](images_for_readme/projet_rest_api.png)

#### 2.1) Le projet `rest_api`

C'est le projet au sens "Django" obtenu via la commande :

`django-admin startproject rest_api`

Il correspond au dossier `rest_api` contenu dans le répertoire `Projet_P10`.

Ce projet vient avec 2 fichiers :
- `db.sqlite3`: le fichier base de données fourni par défaut
- `manage.py` : script python contenant l'ensemble des opérations d'administration du site (création d'une , modification base de données, migration pour "synchroniser" le model avec la base de données etc..)

A l'intérieur de ce dossier projet, se trouvent les applications.

#### 2.2) L'application `rest_api`

![](images_for_readme/application_rest_api.png)

Elle est créée automatiquement lors de la création dy projet `rest_api`.

Elle contient notamment les 2 fichiers :

- `settings.py` : dans lequel se trouve l'ensemble de la configuration du projet
- `urls.py` : dans lequel on définit l'ensemble des points de terminaison (endpoints) de l'api

#### 2.3) L'application `soft_desk`

![](images_for_readme/application_soft_desk.png)

C'est l'application qui héberge le code de l'API.
- `admin.py` : pour pouvoir accéder aux tables via l'administration de Django
- `models.py` : module décrivant le modèle de données
  - `User` : classe personnalisée héritant de `django.contrib.auth.models.AbstractBaseUser`
  - `Project` : classe définissant un projet
  - `Contributor` : classe définissant un contributeur
  - `Issue` : classe définissant un problème, une anomalie, une tâche dans un projet
  - `Comment` : classe
- `permissions.py` : ensemble de classes définissant des permissions customisées
- `serializers.py` : module contenant les classes permettant de "sérialiser" les objects de la base de données
- `views.py` : module contenant l'ensemble des classes de type ViewSet appelées par l'API

#### 2.4) Configuration du projet livré dans le repository Github

Le projet publié dans Github est configuré en **mode production afin de permettre l'affichage de pages d'erreur 404 et 500 customisées**.

Ainsi, au niveau du fichier `settings.py` de l'application `rest_api`, on a les paramètres suivants :
- `ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'http://127.0.0.1:8000/', ]`
- `media` dans la liste `INSTALLED_APPS`
- `DEBUG=False`
- `MEDIA_URL = "/static/media/"`
- `MEDIA_ROOT = Path.joinpath(BASE_DIR, "media/static/media")`



#### GitFlow du projet

Le projet est organisé en 2 branches :

* Branche de développement : `p10_dev`
* Branche principale (version stable du projet) : `main`


### 3) Installation du projet Projet_P10 sur votre machine

Sur votre poste de travail, créer un dossier dans lequel vous allez installer le projet.
On nommera par exemple ce dossier `projects`. (vous pouvez le nommer autrement, c'est juste pour avoir une référence dans la suite des explications)

Aller sur le dépôt github : https://github.com/yannis971/Projet_P10

Pour l'installation, il y a 2 méthodes possibles.

#### 3.1) Première méthode : Téléchargement du fichier zip

![](images_for_readme/depot_github.png)

Dans l'onglet **<> Code** de la page ci-dessus, cliquer sur le bouton **Code** puis sur **Download ZIP**

Placer le fichier zip dans le dossier `projects` et le dézipper.

Ouvrir un terminal et se déplacer dans la racine du projet dossier '`projects/Projet_P10-main/`'

Passer à l'étape 4 pour configurer l'environnement virtuel

#### 3.2) Deuxième méthode : Clonage du dépôt avec git

Sur la figure précédente, copier le lien https : https://github.com/yannis971/Projet_P10.git

Ouvrir un terminal et se déplacer dans le dossier `projects` créé précédemment et taper la commande :

`git clone` suivi du lien https copié plus haut.

soit : `git clone https://github.com/yannis971/Projet_P10.git`

Se déplacer dans la racine du projet : dossier `projects/Projet_P10`

Passer à l'étape 4 pour configurer l'environnement virtuel

### 4) Configuration de l'environnement virtuel

#### Remarque

Les commandes ci-dessous (notamment celles concernant l'installation de pip pour python3) sont valables sur un système d'exploitation Linux de type Debian ou de ses dérivés.

Pour Windows, on utilise python et pip.

Pour Mac OS, on utilise python3 et pip3.

#### 4.1) Installer pip pour python3 si ce n'est pas déjà fait

Si la commande `pip3 --version` renvoie une erreur alors il convient d'installer pip

`sudo apt-get update && sudo apt-get install python3-pip`

Si l'installation a réussi, la commande vous renverra une ligne comme indiqué ci-dessous
`pip 20.2.3 from /soft_desk/yannis/.local/lib/python3.8/site-packages/pip (python 3.8)`

#### 4.2) Créer un environnement virtuel et l'activer

Se placer à la racine du projet (dossier `projects/Projet_P10`) et lancer la commande :

`python3 -m venv env`

Une fois l'environnement virtuel  `env` créé, l'activer avec la commande :

`source env/bin/activate`

#### 4.3) Installer les dépendances du projet

Toujours à la racine du projet, lancer l'une des 2 commandes suivantes :

`pip3 install -r requirements.txt`

`python3 -m pip install -r requirements.txt`

### 5) Exécution

#### 5.1) Lancer le serveur

Une fois l'environnement virtuel activé et les dépendances du projet Projet_P10 installées, en étant positionné dans le dossier `projects/Projet_P10`, se déplacer dans le répertoire du projet Django `rest_api` en tapant la commande :

`cd rest_api`

Dans ce dossier, on trouve le fameux fichier `manage.py` qui permet d'administrer le site.

Lancer le serveur Django en tapant la commande :

`./manage.py runserver`

#### 5.2) Tester l'API via Postman

Les 2 points de terminaison (endpoints) ne nécessitant pas d'un Token d'authentication sont :

Tous les autres endpoints sont accessibles uniquement à un utilisateur authentifié (voir pour certains uniquement au contributeur ou créateur de projet)

Un token unique est généré pour chaque utilisateur connecté avec un email et un mot de passe valide et pour une durrée définie

##### 5.2.1) Créer un compte utilisateur

##### 5.2.2) Se connecter pour obtenir un token JWT

##### 5.2.3) Test d'un point de terminaison nécessitant une authentification



### 6) Licence

Le code de ce projet est sous licence libre **GNU GPL V3**


### 7) Questions/Aide/Support

En cas de problème ou pour toute question relative à ce projet, vous pouvez me contacter via l'un des canaux suivants :

* e-mail : yannis.saliniere@gmail.com

* twitter : https://twitter.com/YSaliniere

* rubrique "issues" du projet github : https://github.com/yannis971/Projet_P10/issues
