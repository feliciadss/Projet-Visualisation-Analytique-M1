from constructeurDB import (
    get_popular_albums, save_album_to_db,
    get_album_tracks, save_track_to_db,
    get_artist_info, save_artist_to_db,
    connect_to_db
)

# Liste des pays européens
european_countries = [
    "AL", "AT", "BE", "BA", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", 
    "FR", "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", 
    "ME", "NL", "MK", "NO", "PL", "PT", "RO", "RS", "SK", "SI", 
    "ES", "SE", "CH", "UA", "GB"
]

def initialize_db():
    db = connect_to_db()

    try:
        # Pour chaque pays, récupérer les albums populaires
        for country in european_countries:
            print(f"Fetching popular albums for {country}...")
            albums = get_popular_albums(country, limit=50)  # Récupère les 50 albums populaires par pays

            # Sauvegarder chaque album dans la base de données
            for album in albums:
                save_album_to_db(album, country, db)

                # Récupérer les morceaux pour chaque album
                print(f"Fetching tracks for album {album['id']}...")
                tracks = get_album_tracks(album["id"])
                for track in tracks:
                    save_track_to_db(track, album["id"], db)

                    # Récupérer et sauvegarder les artistes associés à chaque morceau
                    for artist in track["artists"]:
                        print(f"Fetching artist {artist['id']} info...")
                        artist_info = get_artist_info(artist["id"])
                        save_artist_to_db(artist_info, db)

    except Exception as e:
        print(f"Error processing albums: {e}")

# Exécution du script
if __name__ == "__main__":
    initialize_db()
