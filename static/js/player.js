class SpotifyPlayer {
    constructor() {
        this.player = null;
        this.deviceId = null;
    }

    async init() {
        // Load Spotify Web Playback SDK
        const script = document.createElement('script');
        script.src = 'https://sdk.scdn.co/spotify-player.js';
        document.body.appendChild(script);

        window.onSpotifyWebPlaybackSDKReady = () => {
            this.player = new Spotify.Player({
                name: 'Emotune Web Player',
                getOAuthToken: callback => {
                    // Get token from your backend
                    fetch('/get_spotify_token')
                        .then(response => response.json())
                        .then(data => callback(data.token));
                }
            });

            this.player.connect();
            
            this.player.addListener('ready', ({ device_id }) => {
                this.deviceId = device_id;
            });
        };
    }

    async playSong(spotifyUri) {
        await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${this.deviceId}`, {
            method: 'PUT',
            body: JSON.stringify({ uris: [spotifyUri] }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + await this.getAccessToken()
            }
        });
    }
} 