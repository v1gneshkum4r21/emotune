from Spotipy import update_playlist_csv, emotion_dict

def update_all_playlists():
    for emotion_index in emotion_dict.keys():
        print(f"Updating {emotion_dict[emotion_index]} playlist...")
        update_playlist_csv(emotion_index)
        print(f"Updated {emotion_dict[emotion_index]} playlist")

if __name__ == "__main__":
    update_all_playlists() 