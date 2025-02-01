import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import deezer

SPOTIFY_FAVORITE_TRACKS_BATCH_SIZE = 50 # Spotify API limit
SPOTIFY_PLAYLIST_TRACKS_BATCH_SIZE = 100 # Spotify API limit

class MusicSync:
    def __init__(self):
        load_dotenv()
        
        # Initialize Spotify client
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
            scope='playlist-modify-public playlist-modify-private user-library-modify'
        ))
        
        # Initialize Deezer client
        self.deezer = deezer.Client()
        self.deezer_user_id = os.getenv('DEEZER_USER_ID')

    def search_spotify_track(self, isrc):
        query = f"isrc:{isrc}"
        results = self.spotify.search(q=query, type='track', limit=1)
        
        if results['tracks']['items']:
            return results['tracks']['items'][0]['id']
        return None

    def sync_favorites(self):
        print("Syncing favorites...")
        deezer_user = self.deezer.get_user(self.deezer_user_id)
        favorite_tracks = deezer_user.get_tracks()

        print(f"Found {len(favorite_tracks)} deezer favorites")
        
        # Process tracks by batches
        for i in range(0, len(favorite_tracks), SPOTIFY_FAVORITE_TRACKS_BATCH_SIZE):
            favorite_tracks_batch = favorite_tracks[i:i + SPOTIFY_FAVORITE_TRACKS_BATCH_SIZE]
            spotify_tracks = self._deezer_tracks_to_spotify_tracks(favorite_tracks_batch)
            print(f"Registering {len(spotify_tracks)} favorite tracks")
            self.spotify.current_user_saved_tracks_add(tracks=spotify_tracks)

    def sync_playlists(self):
        print("Syncing playlists...")
        deezer_user = self.deezer.get_user(self.deezer_user_id)
        deezer_playlists = deezer_user.get_playlists()
        spotify_user_id = self.spotify.current_user()['id']
        
        print(f"Found {len(deezer_playlists)} deezer playlists")
        
        for deezer_playlist in deezer_playlists:
            if deezer_playlist.title == "Coups de cœur": # Ignore favorites playlist
                continue
            
            playlist_tracks = deezer_playlist.get_tracks()

            # Create Spotify playlist
            spotify_playlist = self.spotify.user_playlist_create(
                user=spotify_user_id,
                name=deezer_playlist.title,
                public=False
            )
            
            # Process tracks by batches
            for i in range(0, len(playlist_tracks), SPOTIFY_PLAYLIST_TRACKS_BATCH_SIZE):
                playlist_tracks_batch = playlist_tracks[i:i + SPOTIFY_PLAYLIST_TRACKS_BATCH_SIZE]
                spotify_tracks = self._deezer_tracks_to_spotify_tracks(playlist_tracks_batch)
                print(f"Registering {len(spotify_tracks)} playlist tracks")
                self.spotify.playlist_add_items(spotify_playlist['id'], spotify_tracks)

    def _deezer_tracks_to_spotify_tracks(self, deezer_tracks):
        spotify_tracks = []
        for track in deezer_tracks:
            print(f"Searching for id={track.id} isrc={track.isrc} {track.artist.name} {track.title}", end=" - ")
            spotify_id = self.search_spotify_track(track.isrc)
            if spotify_id:
                print(f"Found id={spotify_id}")
                spotify_tracks.append(spotify_id)
            else:
                print("Not found")
        return spotify_tracks
         
def main():
    syncer = MusicSync()
    
    # Sync favorites
    syncer.sync_favorites()
    
    # Sync playlists
    syncer.sync_playlists()
    
    print("Sync completed!")

if __name__ == "__main__":
    main() 