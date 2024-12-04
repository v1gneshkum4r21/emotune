import numpy as np
import cv2
from PIL import Image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import img_to_array
import datetime
from threading import Thread
import time
import pandas as pd
import os

# Initialize face detection and emotion model
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
ds_factor = 0.6

# Initialize emotion model
emotion_model = Sequential()
emotion_model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48,48,1)))
emotion_model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Flatten())
emotion_model.add(Dense(1024, activation='relu'))
emotion_model.add(Dropout(0.5))
emotion_model.add(Dense(7, activation='softmax'))

try:
    emotion_model.load_weights('model.h5')
    print("Successfully loaded emotion model weights")
except Exception as e:
    print(f"Error loading emotion model: {e}")

# Dictionaries for emotions and music
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 
                4: "Neutral", 5: "Sad", 6: "Surprised"}
music_dist = {i: f"songs/{emotion.lower()}.csv" for i, emotion in emotion_dict.items()}

class VideoCamera(object):
    def __init__(self):
        print("Initializing camera...")
        self.is_analyzing = True
        self.current_emotion = "Neutral"
        self.last_emotion = None
        self.current_emotion_idx = 4  # Default to Neutral
        
        # Initialize camera with different backends
        self.video = None
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Any Available")
        ]
        
        for backend, name in backends:
            try:
                print(f"Trying {name} backend")
                self.video = cv2.VideoCapture(0, backend)
                if self.video.isOpened():
                    ret, frame = self.video.read()
                    if ret:
                        print(f"Successfully opened camera with {name}")
                        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.video.set(cv2.CAP_PROP_FPS, 30)
                        break
                    else:
                        self.video.release()
                        self.video = None
            except Exception as e:
                print(f"Error with {name}: {e}")
                if self.video:
                    self.video.release()
                    self.video = None
        
        # Initialize thread
        self.thread = None
        self.start_thread()

    def get_frame(self):
        if not hasattr(self, 'current_frame'):
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank_frame, "Initializing Camera...", (180, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, jpeg = cv2.imencode('.jpg', blank_frame)
            return jpeg.tobytes(), self._get_current_recommendations()
        
        try:
            _, jpeg = cv2.imencode('.jpg', self.current_frame)
            return jpeg.tobytes(), self._get_current_recommendations()
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None, None

    def _get_current_recommendations(self):
        try:
            df = pd.read_csv(music_dist[self.current_emotion_idx])
            df = df[['Name', 'Album', 'Artist', 'SpotifyURL']]
            return df.head(15)
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return pd.DataFrame(columns=['Name', 'Album', 'Artist', 'SpotifyURL'])

    def _capture_loop(self):
        while True:
            if self.video is None or not self.video.isOpened():
                time.sleep(0.1)
                continue
            
            try:
                success, frame = self.video.read()
                if not success:
                    continue

                frame = cv2.resize(frame, (600, 500))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 2)
                    roi_gray = gray[y:y + h, x:x + w]
                    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                    
                    if self.is_analyzing:
                        prediction = emotion_model.predict(cropped_img)
                        self.current_emotion_idx = int(np.argmax(prediction))
                        self.current_emotion = emotion_dict[self.current_emotion_idx]
                        
                    cv2.putText(frame, self.current_emotion, 
                              (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 
                              1, (255, 255, 255), 2, cv2.LINE_AA)

                self.current_frame = frame

            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.1)

    def start_thread(self):
        if self.thread is None:
            self.thread = Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()

    def stop_analysis(self):
        self.is_analyzing = False
        return self.current_emotion

    def start_analysis(self):
        self.is_analyzing = True

    def __del__(self):
        try:
            if hasattr(self, 'thread') and self.thread and self.thread.is_alive():
                self.thread.join()
            if hasattr(self, 'video') and self.video and self.video.isOpened():
                self.video.release()
        except Exception as e:
            print(f"Error in cleanup: {e}")

def music_rec(emotion=None):
    try:
        if emotion is None:
            emotion = "Neutral"
        emotion_idx = list(emotion_dict.values()).index(emotion)
        df = pd.read_csv(music_dist[emotion_idx])
        df = df[['Name', 'Album', 'Artist']]
        return df.head(15)
    except Exception as e:
        print(f"Error in music recommendation: {e}")
        return pd.DataFrame(columns=['Name', 'Album', 'Artist'])
