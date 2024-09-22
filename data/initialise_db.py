from constructeurDB import (
    get_genre_artists, save_artists_to_db,
    get_genre_albums, save_albums_to_db,
    get_album_tracks, save_tracks_to_db,
    get_popular_playlists, save_playlists_to_db,
    get_audio_features, save_audio_features_to_db,
    analyze_and_save_collaborations, connect_to_db
)

def initialize_db():
    db = connect_to_db()
    genres = [
    "pop", "rock", "hip-hop", "jazz", "classical", 
    "electronic", "indie", "reggae", "blues", "metal",
    "folk", "country", "r&b", "soul"]

    european_countries = [
    "AL", "AT", "BE", "BA", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", 
    "FR", "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", 
    "ME", "NL", "MK", "NO", "PL", "PT", "RO", "RS", "SK", "SI", 
    "ES", "SE", "CH", "UA", "GB"]


    for genre in genres:
        for market in european_countries:
            try:
                # Récupération et stockage des artistes
                print(f"Fetching artists for genre {genre} in market {market}...")
                artists = get_genre_artists(genre, market)
                save_artists_to_db(artists, db)

                # ... albums
                print(f"Fetching albums for genre {genre} in market {market}...")
                albums = get_genre_albums(genre, market)
                save_albums_to_db(albums, db)

                # ... morceaux des albums
                for album in albums:
                    print(f"Fetching tracks for album {album['id']}...")
                    tracks = get_album_tracks(album["id"])
                    save_tracks_to_db(tracks, db)

                    # ... caractéristiques audio
                    track_ids = [track["id"] for track in tracks]
                    audio_features = get_audio_features(track_ids)
                    save_audio_features_to_db(audio_features, db)

                # ... playlists
                print(f"Fetching playlists for market {market}...")
                playlists = get_popular_playlists(market)
                save_playlists_to_db(playlists, db)

                # Analyser et sauvegarder les collaborations entre artistes
                analyze_and_save_collaborations(playlists, db)

            except Exception as e:
                print(f"Error processing genre {genre} in market {market}: {e}")

if __name__ == "__main__":
    initialize_db()
