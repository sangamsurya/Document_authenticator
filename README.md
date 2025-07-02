# Voice Steganography & Matcher Project

This project is a full-stack application for secure audio steganography and voice matching. It allows users to embed audio data into images, extract audio from stego images, and perform voice matching, all through a user-friendly web interface.

## Project Structure

```
Backend/   # Python Flask API for steganography, audio/image processing, and voice matching
Frontend/  # React web application for user interaction
```

---

## Features

- **Audio Steganography:** Embed audio files into images using cyclic LSB steganography.
- **Audio Extraction:** Extract audio and metadata from stego images.
- **Voice Matching:** Generate and compare audio fingerprints for voice verification.
- **User-Friendly Interface:** Modern React frontend for easy interaction.
- **Secure Processing:** File validation, size checks, and secure handling.
- **Database Integration:** Stores audio fingerprints and metadata for matching.

---

## Backend (Flask API)

### Main Endpoints

- `POST /embed`  
  Embed an audio file (WAV) into an image (PNG/JPG). Returns a stego image and unique ID.

- `POST /extract`  
  Extract audio and metadata from a stego image.

- `POST /compare_audio`  
  Compare an uploaded audio file with stored fingerprints for matching.

### Technologies

- Python 3
- Flask, Flask-CORS
- NumPy, Pillow, Pydub, Librosa, SciPy
- PyMongo (MongoDB)
- Scikit-learn, Matplotlib

### Setup

```bash
cd Backend
pip install -r requirements.txt
python app.py
```

---

## Frontend (React)

### Features

- Upload images and audio for embedding.
- Extract audio from stego images.
- Voice matching and verification.
- Real-time feedback and results.

### Setup

```bash
cd Frontend
npm install
npm start
```

The frontend runs on [http://localhost:3000](http://localhost:3000) and connects to the backend API.

---

**Note:**  
- Ensure MongoDB is running if you want to use the fingerprint database features.
- Default backend runs on [http://localhost:5000](http://localhost:5000).
- Update CORS settings in `Backend/app.py` if deploying to production.
