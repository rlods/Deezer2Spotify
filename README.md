# Deezer2Spotify
Simple favorites and playlists importer from Deezer to Spotify

## Usage

1. Clone the repository

gh repo clone rlods/Deezer2Spotify

2. Install the required dependencies:

pip install -r requirements.txt

3. Set up your Spotify Developer account:

Go to https://developer.spotify.com/dashboard
Create a new application
Get your Client ID and Client Secret
Add http://localhost:8888/callback to your Redirect URIs in the app settings

4. Get your Deezer user ID:
Go to your Deezer profile
Your user ID will be in the URL (e.g., https://www.deezer.com/profile/12345678)

4. Update the .env file with your credentials

5. Run the script:

python deezer_spotify_sync.py
