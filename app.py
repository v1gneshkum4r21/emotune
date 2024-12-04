from flask import Flask, render_template, Response, jsonify, send_file
from camera import VideoCamera, music_rec
import pandas as pd
import time
import os

app = Flask(__name__)

# Global variables
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 
                4: "Neutral", 5: "Sad", 6: "Surprised"}
music_dist = {i: f"songs/{emotion.lower()}.csv" for i, emotion in emotion_dict.items()}

camera = VideoCamera()
current_df = None
headings = ("Name", "Album", "Artist", "Action")

@app.route('/')
def index():
    global current_df
    if current_df is None:
        # Initialize with neutral emotion songs
        current_df = pd.read_csv(music_dist[4])  # 4 is Neutral in emotion_dict
    
    # Convert DataFrame to list of dictionaries
    data = current_df.to_dict('records') if current_df is not None else []
    
    return render_template('index.html', headings=headings, data=data)

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(camera):
    while True:
        try:
            frame, music_df = camera.get_frame()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            global df1
            if music_df is not None and not music_df.empty:
                df1 = music_df
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage
        except Exception as e:
            print(f"Error in gen: {e}")
            time.sleep(0.5)  # Longer delay on error
            continue

@app.route('/t')
def gen_table():
    global df1
    try:
        if df1 is not None and not df1.empty:
            # Ensure all required columns exist
            required_columns = ['Name', 'Album', 'Artist', 'SpotifyURL', 'Duration', 'ImageURL']
            for col in required_columns:
                if col not in df1.columns:
                    if col == 'Duration':
                        df1[col] = '0:00'
                    elif col == 'ImageURL':
                        df1[col] = '/static/images/default-album.jpg'
                    else:
                        df1[col] = ''
            
            data = df1.to_dict('records')
            return jsonify(data)
        return jsonify([])
    except Exception as e:
        print(f"Error in gen_table: {e}")
        return jsonify([])

@app.route('/start_analysis')
def start_analysis():
    camera.start_analysis()
    return jsonify({"status": "Analysis started"})

@app.route('/stop_analysis')
def stop_analysis():
    last_emotion = camera.stop_analysis()
    try:
        if last_emotion:
            current_df = music_rec(last_emotion)
        else:
            current_df = music_rec("Neutral")
        return jsonify({"status": "success", "emotion": last_emotion or "Neutral"})
    except Exception as e:
        print(f"Error in stop_analysis: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/current_emotion')
def get_current_emotion():
    return jsonify({"emotion": camera.current_emotion})

@app.route('/play/<song_name>')
def play_song(song_name):
    try:
        # Assuming songs are stored in a 'songs' directory
        song_path = os.path.join('songs', f"{song_name}.mp3")
        if os.path.exists(song_path):
            return send_file(song_path, mimetype='audio/mp3')
        else:
            return jsonify({"error": "Song not found"}), 404
    except Exception as e:
        print(f"Error playing song: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.debug = True
    app.run()
