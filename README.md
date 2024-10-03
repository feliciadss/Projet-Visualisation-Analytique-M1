# **Projet d'Analyse des Genres Musicaux en Europe avec l'API Spotify**

## **Description**
Ce projet vise à fournir des informations clés aux labels musicaux sur la popularité des genres en Europe, l'évolution des tendances musicales, et les collaborations entre artistes de différents genres. À travers l'analyse des données des trois dernières années, le projet permet aux labels de suivre la croissance ou le déclin des genres musicaux et d'identifier les opportunités d'investissement dans des artistes ou des collaborations prometteuses.

## **Problématique**
**Comment les genres musicaux évoluent-ils et se popularisent-ils en Europe, et quels facteurs influencent cette dynamique, aidant ainsi les labels à prendre des décisions d'investissement stratégiques ?**

### **Objectifs**
- Suivre la popularité des genres musicaux dans différents pays européens.
- Analyser l'évolution des genres au fil du temps pour identifier les tendances futures.
- Étudier les collaborations entre artistes de genres différents et leur impact sur la diversité musicale.
- Fournir des visualisations intuitives pour interpréter ces données et permettre aux labels de prendre des décisions éclairées.

## **Structure du Projet**

### **1. Dossier `data`**
Ce dossier contient les scripts nécessaires pour initialiser et gérer la base de données MongoDB, en récupérant les données via l'API Spotify.

- **`initialise_db.py`** : Ce script utilise les fichiers suivants pour construire une base de données MongoDB avec les données récupérées via l'API Spotify.
  - **`auth_spotify.py`** : Gère l'authentification avec l'API Spotify.
  - **`config`** : Fichier de configuration qui centralise les paramètres nécessaires à la récupération des données.
  - **`constructeurDB.py`** : Contient les fonctions pour récupérer les données depuis l'API Spotify et les structurer dans la base MongoDB.

- **`data_manager`** : Ce sous-dossier regroupe les classes orientées objets pour gérer les différentes collections (tracks, albums, artistes, genres, marchés). Il contient aussi des fonctions permettant de construire des DataFrames adaptés à nos besoins de visualisation.

### **2. Dossier `static`**
Ce dossier contient les ressources statiques nécessaires au projet.

- **Fichiers JSON** : Données statiques telles que des cartes géographiques (pour les heatmaps), ou d'autres informations pré-chargées.
- **`style.css`** : Fichier de style pour la mise en page des visualisations.
- **Énumérations** : Fichiers contenant les différentes énumérations liées aux genres, marchés, etc.

### **3. Dossier `template`**
Ce dossier contient les pages HTML pour l'interface utilisateur.

- **`base.html`** : Le fichier de base qui inclut le cadre principal pour toutes les pages.
- **`index.html`** : La page d'accueil du projet.
- **Pages HTML** : Chaque page de visualisation est stockée ici

### **4. Dossier `view`**
Ce dossier stocke les objets de visualisation.

- **`map.py`** 
- **`graph.py`**
- **`chart.py`**

### **5. Fichier `requirements.txt`**
Ce fichier contient toutes les dépendances nécessaires pour exécuter l'application. Il regroupe les packages et leurs versions, notamment Flask, MongoDB, Spotipy, Plotly, Pandas, et autres bibliothèques utilisées dans le projet.

## **Fonctionnement de l'Application**

### **Installation**
1. Clonez ce repository sur votre machine locale.
2. Installez les dépendances avec la commande suivante :
   ```bash
   pip install -r requirements.txt
   ```

### **Mise à jour de la base de données**
Si vous souhaitez créer ou mettre à jour la base de données MongoDB, vous pouvez vous rendre dans le dossier `data` et exécuter la commande suivante :
    ```bash
      python initialise_db.py
    ```

Cependant, cette étape a déjà été effectuée lors de la configuration initiale du projet, donc il n'est généralement pas nécessaire de la relancer à moins que vous souhaitiez actualiser les données.

### **Lancement de l'Application**
Pour lancer l'application, exécutez la commande suivante :
    ```bash
     python app.py
    ```
