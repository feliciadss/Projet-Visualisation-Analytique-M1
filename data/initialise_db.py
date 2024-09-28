from constructeurDB import (
    get_genre_albums, save_albums_to_db,
    get_album_tracks, save_tracks_to_db,
    get_artists_from_tracks, save_artists_to_db,  # Correction des noms
    connect_to_db
)

def initialize_db():
    db = connect_to_db()
    genres = [
        "pop", "rock", "hip-hop", "jazz", "classical", 
        "electronic", "indie", "reggae", "blues", "metal",
        "folk", "country", "r&b", "soul"
    ]

    european_countries = [
        "AL", "AT", "BE", "BA", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", 
        "FR", "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", 
        "ME", "NL", "MK", "NO", "PL", "PT", "RO", "RS", "SK", "SI", 
        "ES", "SE", "CH", "UA", "GB"
    ]

    for genre in genres:
        for market in european_countries:
            try:
                # Récupération et stockage des albums
                print(f"Fetching albums for genre {genre} in market {market}...")
                albums = get_genre_albums(genre, market)
                save_albums_to_db(albums, genre, market, db)

                # Récupération et stockage des morceaux des albums
                for album in albums:
                    print(f"Fetching tracks for album {album['id']}...")
                    tracks = get_album_tracks(album["id"])
                    save_tracks_to_db(tracks, album["id"], db)
                    
                    for track in tracks:
                        print(f"Fetching artists for track {track['id']}...")
                        artists = get_artists_from_tracks([track])  # On passe chaque track un par un
                        save_artists_to_db(artists, genre, market, db)

            except Exception as e:
                print(f"Error processing genre {genre} in market {market}: {e}")

if __name__ == "__main__":
    initialize_db()
