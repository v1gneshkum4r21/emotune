class EmotionDetector {
    constructor() {
        this.video = document.createElement('video');
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.model = null;
    }

    async init() {
        // Load TensorFlow.js model
        this.model = await tf.loadLayersModel('/static/model/emotion_model/model.json');
        
        // Setup webcam
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        this.video.srcObject = stream;
        this.video.play();
        
        // Start detection loop
        this.detect();
    }

    async detect() {
        // Process video frame
        this.ctx.drawImage(this.video, 0, 0, 48, 48);
        const imageData = this.ctx.getImageData(0, 0, 48, 48);
        
        // Preprocess for model
        const tensor = tf.browser.fromPixels(imageData)
            .mean(2)
            .expandDims(2)
            .expandDims(0)
            .div(255.0);

        // Get prediction
        const prediction = await this.model.predict(tensor).data();
        const emotion = this.getEmotion(prediction);
        
        // Update recommendations
        this.updateRecommendations(emotion);
        
        requestAnimationFrame(() => this.detect());
    }

    getEmotion(prediction) {
        const emotions = ['Angry', 'Disgusted', 'Fearful', 'Happy', 'Neutral', 'Sad', 'Surprised'];
        return emotions[prediction.indexOf(Math.max(...prediction))];
    }

    async updateRecommendations(emotion) {
        const response = await fetch(`/get_recommendations/${emotion}`);
        const songs = await response.json();
        // Update UI with new recommendations
        updateSongList(songs);
    }
} 