import pandas as pd
from Spotipy import update_playlist_csv

# Add at the top of the file
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 
                4: "Neutral", 5: "Sad", 6: "Surprised"}

def update_csv_files():
    emotions = ['happy', 'sad', 'angry', 'neutral', 'surprised']
    
    for emotion in emotions:
        try:
            # Read the CSV file
            df = pd.read_csv(f'songs/{emotion}.csv')
            
            # Add SpotifyURL column if it doesn't exist
            if 'SpotifyURL' not in df.columns:
                # Create search URLs
                df['SpotifyURL'] = df.apply(
                    lambda row: f"https://open.spotify.com/search/{row['Name'].replace(' ', '%20')}%20{row['Artist'].replace(' ', '%20')}", 
                    axis=1
                )
                
                # Save the updated CSV
                df.to_csv(f'songs/{emotion}.csv', index=False)
                print(f"Updated {emotion}.csv with Spotify URLs")
                
        except Exception as e:
            print(f"Error processing {emotion}.csv: {e}")

if __name__ == "__main__":
    for emotion_idx in range(7):  # 0 to 6 for all emotions
        print(f"Updating playlist for {emotion_dict[emotion_idx]}...")
        update_playlist_csv(emotion_idx)
        print(f"Completed {emotion_dict[emotion_idx]}") 