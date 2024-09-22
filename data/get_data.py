from pymongo import MongoClient
import pandas as pd
import configparser

# Charger le fichier de configuration
config = configparser.ConfigParser()
config.read("C:/Users/PC/OneDrive/Documents/projet-visualisation-analytique-m1/data/config.ini")

# Connexion à MongoDB et récupération des données depuis une collection spécifique
def get_data_from_mongodb(collection_name):
    """
    Récupère les données d'une collection MongoDB et les retourne sous forme de DataFrame.
    
    :param collection_name: Nom de la collection MongoDB à récupérer
    :return: Un DataFrame contenant les données de la collection
    """
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])  # Remplace par ton URI MongoDB
    db = client[config['MONGO_DB']['DB_NAME']]  # Utilise le nom de la base de données du fichier config
    collection = db[collection_name]
    
    # Convertir les données MongoDB en liste puis en DataFrame
    data = list(collection.find())
    df = pd.DataFrame(data)
    
    return df
