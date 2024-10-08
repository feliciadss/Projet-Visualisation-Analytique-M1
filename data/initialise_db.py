from constructeurDB import (
    get_popular_albums, save_album_to_db,
    get_album_tracks, save_track_to_db,
    get_artist_info, save_artist_to_db,
    connect_to_db, get_popular_playlists, 
    get_playlist_tracks
)

def initialize_db():
    db = connect_to_db()

    european_countries = [
        "CZ", "DK", "EE", "FI", 
        "FR", "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", 
        "ME", "NL", "MK", "NO", "PL", "PT", "RO", "RS", "SK", "SI", 
        "ES", "SE", "CH", "UA", "GB"
    ]#attention je retire des pays a chaque relance, pour eviter les requetes doublons 

    try:
        for country in european_countries:
            print(f"Fetching popular playlists for {country}...")
            playlists = get_popular_playlists(country, limit=10)  

            for playlist in playlists:
                print(f"Fetching tracks for playlist {playlist['name']}...")
                tracks = get_playlist_tracks(playlist["id"])

                for item in tracks:
                    track = item["track"]
                    album = track["album"]

                    # Sauvegarder l'album et les artistes associés
                    save_album_to_db(album, country, db)
                    save_track_to_db(track, album["id"], db)

                    for artist in track["artists"]:
                        artist_info = get_artist_info(artist["id"])
                        save_artist_to_db(artist_info, db)

    except Exception as e:
        print(f"Error processing playlists: {e}")

# Exécution du script
if __name__ == "__main__":
    initialize_db()