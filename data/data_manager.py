import pandas as pd
from pymongo import MongoClient
import configparser

# Charger la configuration pour MongoDB
config = configparser.ConfigParser()
config.read("./data/config.ini")

# Fonction pour récupérer une collection depuis MongoDB
def get_collection_from_db(collection_name):
    client = MongoClient(config['MONGO_DB']['MONGO_URI'])
    db = client[config['MONGO_DB']['DB_NAME']]
    collection = db[collection_name]
    return collection

# Classe pour représenter un Album
class Album:
    def __init__(self, album_json):
        self.id = album_json.get('id')
        self.name = album_json.get('name')
        self.artists = [artist['id'] for artist in album_json.get('artists', [])] 
        self.market = album_json.get('market')
        self.release_date = album_json.get('release_date') 

# Classe pour représenter un Artiste
class Artist:
    def __init__(self, artist_json):
        self.id = artist_json.get('id')
        self.genre = artist_json.get('genre')
        self.market = artist_json.get('market')



class DataManager:
    def __init__(self):
        self.albums_collection = get_collection_from_db('albums')  # Collection des albums
        self.artists_collection = get_collection_from_db('artists')  # Collection des artistes

    def create_albums_artists_dataframe(self, genre_filter=None):
        albums_cursor = self.albums_collection.find()
        albums_list = list(albums_cursor)
        print(f"Nombre d'albums récupérés : {len(albums_list)}")

        data = []
        
        # Parcourir chaque album pour extraire les artistes et leur marché
        for album_json in albums_list:
            album = Album(album_json)
            
            # Parcourir les artistes associés à cet album
            for artist_id in album.artists:
                artist_json = self.artists_collection.find_one({"id": artist_id})
                if artist_json:
                    artist = Artist(artist_json)

                    # Filtrer par genre si un genre est spécifié
                    if genre_filter is None or artist.genre == genre_filter:
                        # Ajouter seulement les artistes avec un marché valide
                        if artist.market:
                            data.append({
                                'album_id': album.id,
                                'artist_id': artist.id,
                                'artist_genre': artist.genre,
                                'artist_market': artist.market
                            })

        # Créer un DataFrame avec les informations extraites
        df = pd.DataFrame(data)
        print(f"DataFrame final créé : {len(df)} lignes")
        return df