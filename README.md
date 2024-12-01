# **Projet d'Analyse des Genres Musicaux en Europe avec l'API Spotify**

## **Description**
Ce projet vise à fournir des informations clés aux labels musicaux sur la popularité des genres en Europe, l'évolution des tendances musicales, et les collaborations entre artistes de différents genres. Le site permet aux labels de suivre la croissance ou le déclin des genres musicaux et d'identifier les opportunités d'investissement dans des artistes ou des collaborations prometteuses.

## **Problématique**
**Comment les genres musicaux évoluent-ils et se popularisent-ils en Europe, et quels facteurs influencent cette dynamique, aidant ainsi les labels à prendre des décisions d'investissement stratégiques ?**

### **Objectifs**
- Suivre la popularité des genres musicaux dans différents pays européens.
- Analyser l'évolution des genres au fil du temps pour identifier les tendances futures.
- Étudier les collaborations entre artistes de genres différents et leur impact sur la diversité musicale.
- Proposer des visualisations interactives pour analyser les caractéristiques musicales et aider les labels à prendre des décisions stratégiques.

## **Structure du Projet**

### **1. Dossier `data`**
Ce dossier contient les scripts nécessaires pour initialiser et gérer la base de données MongoDB en récupérant les données via l'API Spotify, puis pour les stocker dans une base de données SQL locale, optimisant ainsi la rapidité des interactions.

## **Fetching**
- **`initialise_db.py`** : Ce script utilise les fichiers suivants pour construire une base de données MongoDB avec les données récupérées via l'API Spotify.
- **`auth_spotify.py`** : Gère l'authentification avec l'API Spotify.
- **`config.ini`** : Fichier de configuration A REMPLIR contenant les identifiants secrets de votre compte Spotify Developer, et du compte Mongo DB depuis lequel vous allez créer la base de données.
- **`constructeurDB.py`** : Contient les fonctions pour récupérer les données depuis l'API Spotify et les structurer dans la base MongoDB.

## **Migration**
- **`update_sql.py`** : Ce script sert à migrer les données de MongoDB vers une base de données SQLite (spotify.db). Il crée les tables nécessaires (artistes, albums, tracks), les met à jour avec les données récupérées de MongoDB, et ajoute des colonnes supplémentaires afin de faciliter l'exécution rapide de requêtes SQL.
- **`spotify.db`** : Fichier de base de données SQLite contenant les données structurées des artistes, albums, et tracks. Cette base de données est utilisée pour un accès plus rapide aux données lors des requêtes SQL, permettant de gérer efficacement les visualisations et analyses sans toujours interroger MongoDB.

## **Gestion**
- **`data_manager`** : Ce sous-dossier regroupe les classes orientées objets pour gérer les différentes tables (tracks, albums, artistes). Il contient aussi des fonctions permettant de construire des DataFrames adaptés à nos besoins de visualisation.

### **2. Dossier `static`**
Ce dossier contient les ressources statiques nécessaires au projet.

- **`custom.geo.json`** : Carte géographique pré-chargées
- **`enumerations.py`** : Fichier contenant les différentes énumérations liées aux nom des genres, des pays, des marchés, ainsi qu'aux couleurs associés, aux URL associés etc.Vous pouvez le modifier, notamment si vous souhaitez ajouter de nouveaux genres, pays, marchés, ou personnaliser les couleurs et URL associées pour répondre à des besoins spécifiques.
- **`festivals_europe.csv`** : Fichier généré par ChatGPT, listant des festivals de musique européens avec leur nom, pays, participants, prix moyen, mois et genres musicaux.
- **`style.css`** : Fichier de style gèrant les styles globaux (structure, navigation, boutons, footer, surbrillances..) pour garantir une interface sobre.


### **3. Dossier `pages`**
Ce dossier stocke les modules qui définissent les pages de l'application web Dash. Chaque fichier représente une page et contient le layout (structure HTML) et les callbacks (logique de mise à jour) associés à chaque fonctionnalité de visualisation de données. 

- **`accueil.py`** 
- **`caract_musicales.py`** 
- **`collaborations.py`**
- **`evolution_genres.py`**
- **`popularite.py`**


### **5. Fichier `requirements.txt`**
Ce fichier contient toutes les dépendances nécessaires pour exécuter l'application, incluant les packages Dash, requests, pymongo, Plotly, pycountry, Pandas, et leurs versions spécifiques pour garantir la compatibilité et le bon fonctionnement.

## **Fonctionnement de l'Application**

### **Installation**
1. Clonez ce repository sur votre machine locale.
2. Installez les dépendances avec la commande suivante :
```python
pip install -r requirements.txt
```

### **Mise à jour des bases de données**
🚧 Cette étape a déjà été effectuée lors de la configuration initiale du projet, donc il n'est généralement pas nécessaire de la relancer, sauf si vous souhaitez actualiser les données.

### **1. Mise à jour Mongo DB**

Si vous souhaitez créer ou mettre à jour la base de données MongoDB, vous pouvez vous rendre dans le dossier `data` et exécuter la commande suivante :
```python
python initialise_db.py
```
Ce script récupérera les données via l'API Spotify et mettra à jour les collections MongoDB (artistes, albums, tracks).

⚠️ Ne pas oublier de remplir config.ini avec les identifiants Spotify et MongoDB !!!!

Étant limités par l'API Spotify à un certain nombre de requêtes quotidiennes, de septembre à novembre 2023, nous avons récupéré les playlists populaires dans différents pays européens via l'API Spotify, puis extrait et stocké les informations sur les albums, les morceaux et les artistes associés, reconstituant ainsi un ensemble assez homogène des tendances musicales en Europe.

### **2. Mise à jour SQLite**
Si vous souhaitez migrer les données de MongoDB vers SQLite pour optimiser l'accès rapide aux données, exécutez le script suivant dans le dossier data :
```python
python update_sql.py
```
Ce script va créer et/ou mettre à jour la base de données `spotify.db` avec les tables d'artistes, d'albums, et de tracks, en récupérant les données depuis MongoDB et en les structurant pour des requêtes SQL efficaces.

### **Lancement de l'Application**
👩🏽‍💻
Pour lancer l'application, exécutez la commande suivante :
```python
python app.py
````
