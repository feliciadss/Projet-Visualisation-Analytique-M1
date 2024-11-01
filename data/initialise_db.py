from constructeurDB import (
    save_album_to_db, save_track_to_db,
    get_artist_info, save_artist_to_db,
    connect_to_db, get_popular_playlists, 
    get_playlist_tracks
)
#from static.enumerations import european_countries


def initialize_db():
    db = connect_to_db()

    european_countries = [
        "RS", "SK", "SI", 
        "ES", "SE", "CH", "UA", "GB", "NO"
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

                    save_album_to_db(album, country, db)
                    save_track_to_db(track, album["id"], db)

                    for artist in track["artists"]:
                        artist_info = get_artist_info(artist["id"])
                        save_artist_to_db(artist_info, db)

    except Exception as e:
        print(f"Error processing playlists: {e}")

if __name__ == "__main__":
    initialize_db()