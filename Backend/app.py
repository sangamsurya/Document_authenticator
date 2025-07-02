from flask import Flask, request, jsonify
from io import BytesIO
from stego_rev import embed_data_rgb, extract_data_from_image, audio_to_binary, binary_to_audio
from unique_id import unique_id_generator
from fingetprint import generate_fingerprint, match_audio
from database import db_manager
from logger import logger
from config import config
import numpy as np
import base64
from typing import Dict, Any
import os
from werkzeug.utils import secure_filename
import librosa
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
from scipy.io import wavfile
import io
from pydub import AudioSegment
import tempfile
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive 'Agg'
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

app = Flask(__name__)

# Configure CORS
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000"],  # Your React app's URL
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True
     }},
     supports_credentials=True)

# Set Flask configuration from our config
app.config['MAX_CONTENT_LENGTH'] = config['MAX_FILE_SIZE']
app.config['SECRET_KEY'] = config['SECRET_KEY']

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file_size(file) -> bool:
    """Validate if the file size is within limits."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= config['MAX_FILE_SIZE']

@app.route('/embed', methods=['POST'])
def embed() -> Dict[str, Any]:
    """
    Embed audio data into an image using steganography.
    Expected request:
    - image: Image file (PNG/JPG)
    - audio: Audio file (WAV)
    Returns:
    - JSON response with stego image and status
    """
    try:
        # Validate request
        if 'image' not in request.files or 'audio' not in request.files:
            logger.warning("Missing required files in embed request")
            return jsonify({"error": "Missing required files"}), 400

        image_file = request.files['image']
        audio_file = request.files['audio']

        # Validate file types
        if not allowed_file(image_file.filename, config['ALLOWED_IMAGE_EXTENSIONS']):
            logger.warning(f"Invalid image file type: {image_file.filename}")
            return jsonify({"error": "Invalid image file type"}), 400
        if not allowed_file(audio_file.filename, config['ALLOWED_AUDIO_EXTENSIONS']):
            logger.warning(f"Invalid audio file type: {audio_file.filename}")
            return jsonify({"error": "Invalid audio file type"}), 400

        # Validate file sizes
        if not validate_file_size(image_file) or not validate_file_size(audio_file):
            logger.warning("File size exceeds limit")
            return jsonify({"error": "File size exceeds limit"}), 413

        # Secure filenames
        image_filename = secure_filename(image_file.filename)
        audio_filename = secure_filename(audio_file.filename)

        logger.info(f"Processing files: {image_filename}, {audio_filename}")

        # Read files into memory
        image_data = BytesIO(image_file.read())
        audio_data = BytesIO(audio_file.read())

        # Generate fingerprint and unique ID
        try:
            generated_fp = generate_fingerprint(audio_data)
            unique_id = unique_id_generator()
            
            # Store in database using the new database manager
            db_result = db_manager.store_fingerprint(unique_id, generated_fp, audio_filename)
            logger.info(f"Fingerprint stored with unique_id: {unique_id}")
            
            unique_id = format(unique_id, '032b')
            
            # Reset audio_data pointer for audio_to_binary
            audio_data.seek(0)
            binary_data, frame_rate = audio_to_binary(audio_data)
            
        except ValueError as e:
            logger.error(f"Error processing audio: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except IOError as e:
            logger.error(f"Error processing audio: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return jsonify({"error": "Error processing audio file"}), 400

        # Embed data into image
        try:
            output_image_path = os.path.join(config['OUTPUT_FOLDER'], 'stego_image_rev_flask.png')
            stego_image = embed_data_rgb(
                image_data,
                frame_rate,
                unique_id,
                binary_data,
                output_image_path
            )
        except Exception as e:
            logger.error(f"Error embedding data: {str(e)}")
            return jsonify({"error": "Error embedding data into image"}), 500

        # Convert to base64
        try:
            image_buffer = BytesIO()
            stego_image.save(image_buffer, format="PNG")
            image_buffer.seek(0)
            encoded_image = base64.b64encode(image_buffer.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return jsonify({"error": "Error encoding image"}), 500

        logger.info("Embedding completed successfully")
        return jsonify({
            "saved_image_path": output_image_path,
            "stego_image_base64": encoded_image,
            "message": "Embedding completed successfully",
            "unique_id": unique_id
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error in embed endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route('/extract', methods=['POST'])
def extract() -> Dict[str, Any]:
    """
    Extract audio data from a stego image.
    
    Expected request:
    - image: Stego image file
    
    Returns:
    - JSON response with extraction status and match result
    """
    try:
        if 'image' not in request.files:
            logger.warning("No image file provided in extract request")
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        
        if not allowed_file(image_file.filename, config['ALLOWED_IMAGE_EXTENSIONS']):
            logger.warning(f"Invalid image file type: {image_file.filename}")
            return jsonify({"error": "Invalid image file type"}), 400

        if not validate_file_size(image_file):
            logger.warning("File size exceeds limit")
            return jsonify({"error": "File size exceeds limit"}), 413

        image_filename = secure_filename(image_file.filename)
        logger.info(f"Processing extraction for: {image_filename}")

        # Read image into memory
        image_data = BytesIO(image_file.read())

        # Extract data
        try:
            extracted_binary, frame_rate, unique_id = extract_data_from_image(image_data)
            logger.info(f"Data extracted successfully: unique_id={unique_id}, frame_rate={frame_rate}")
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            return jsonify({"error": "Error extracting data from image"}), 400

        # Convert to audio
        try:
            extracted_audio_file = os.path.join(config['OUTPUT_FOLDER'], 'extracted_audio_flask.wav')
            binary_to_audio(extracted_binary, frame_rate, extracted_audio_file)
            logger.info("Audio data generated successfully")
        except Exception as e:
            logger.error(f"Error converting binary to audio: {str(e)}")
            return jsonify({"error": "Error converting binary to audio"}), 400

        # Fetch stored fingerprint using the new database manager
        try:
            stored_fp_data = db_manager.get_fingerprint(unique_id)
            if not stored_fp_data:
                logger.warning(f"Fingerprint not found for unique_id: {unique_id}")
                return jsonify({"error": "Fingerprint not found"}), 404
            stored_fp = stored_fp_data["fingerprint"]
        except Exception as e:
            logger.error(f"Error fetching fingerprint: {str(e)}")
            return jsonify({"error": "Error fetching fingerprint"}), 500

        # Generate and match fingerprint
        try:
            extracted_fp = generate_fingerprint(extracted_audio_file)
            match_result = match_audio(extracted_fp, stored_fp)
            logger.info(f"Audio match result: {match_result}")
        except Exception as e:
            logger.error(f"Error matching fingerprints: {str(e)}")
            return jsonify({"error": "Error matching fingerprints"}), 500

        logger.info("Extraction completed successfully")
        return jsonify({
            "message": "Audio extracted and processed successfully",
            "match_result": match_result,
            "original_filename": stored_fp_data.get("original_filename", "unknown")
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error in extract endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500



def convert_to_wav(audio_file, filename):
    """Convert audio file to WAV format."""
    try:
        # Create a temporary file to store the original audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_input:
            audio_file.save(temp_input.name)
            
            # Load the audio file using pydub
            audio = AudioSegment.from_file(temp_input.name)
            
            # Create a temporary file for the WAV output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
                # Export as WAV
                audio.export(temp_output.name, format='wav')
                return temp_output.name
    except Exception as e:
        logger.error(f"Error converting audio to WAV: {str(e)}")
        raise
    finally:
        # Clean up the temporary input file
        if 'temp_input' in locals():
            os.unlink(temp_input.name)

@app.route('/compare_audio', methods=['POST', 'OPTIONS'])
def compare_audio() -> Dict[str, Any]:
    if request.method == 'OPTIONS':
        return '', 200

    temp_path1 = None
    temp_path2 = None
    wav_path1 = None
    wav_path2 = None

    try:
        # Validate request
        if 'audio1' not in request.files or 'audio2' not in request.files:
            logger.warning("Missing required audio files in compare request")
            return jsonify({
                "error": "Missing required audio files",
                "details": "Please provide both audio1 and audio2 files"
            }), 400

        audio1_file = request.files['audio1']
        audio2_file = request.files['audio2']

        # Validate file types
        allowed_extensions = {'wav', 'mp3', 'webm', 'ogg', 'm4a'}
        if not allowed_file(audio1_file.filename, allowed_extensions) or \
           not allowed_file(audio2_file.filename, allowed_extensions):
            logger.warning("Invalid audio file type")
            return jsonify({
                "error": "Invalid audio file type",
                "details": f"Allowed extensions: {allowed_extensions}"
            }), 400

        # Validate file sizes
        if not validate_file_size(audio1_file) or not validate_file_size(audio2_file):
            logger.warning("File size exceeds limit")
            return jsonify({
                "error": "File size exceeds limit",
                "details": f"Maximum file size: {config['MAX_FILE_SIZE']} bytes"
            }), 413

        # Secure filenames
        audio1_filename = secure_filename(audio1_file.filename)
        audio2_filename = secure_filename(audio2_file.filename)

        logger.info(f"Processing audio comparison: {audio1_filename}, {audio2_filename}")

        # Convert files to WAV format
        try:
            wav_path1 = convert_to_wav(audio1_file, audio1_filename)
            wav_path2 = convert_to_wav(audio2_file, audio2_filename)
        except Exception as e:
            logger.error(f"Error converting audio files: {str(e)}")
            return jsonify({
                "error": "Error converting audio files",
                "details": str(e)
            }), 400

        try:
            # Load audio files
            y1, sr1 = librosa.load(wav_path1)
            y2, sr2 = librosa.load(wav_path2)

            # Extract speaker-specific features
            # Pitch features
            pitches1, magnitudes1 = librosa.piptrack(y=y1, sr=sr1)
            pitches2, magnitudes2 = librosa.piptrack(y=y2, sr=sr2)
            
            pitch_mean1 = np.mean(pitches1[magnitudes1 > np.median(magnitudes1)])
            pitch_std1 = np.std(pitches1[magnitudes1 > np.median(magnitudes1)])
            pitch_range1 = np.ptp(pitches1[magnitudes1 > np.median(magnitudes1)])
            
            pitch_mean2 = np.mean(pitches2[magnitudes2 > np.median(magnitudes2)])
            pitch_std2 = np.std(pitches2[magnitudes2 > np.median(magnitudes2)])
            pitch_range2 = np.ptp(pitches2[magnitudes2 > np.median(magnitudes2)])

            # Amplitude features
            amp_mean1 = np.mean(np.abs(y1))
            amp_std1 = np.std(np.abs(y1))
            amp_range1 = np.ptp(np.abs(y1))
            
            amp_mean2 = np.mean(np.abs(y2))
            amp_std2 = np.std(np.abs(y2))
            amp_range2 = np.ptp(np.abs(y2))

            # Spectral features
            spectral_centroids1 = librosa.feature.spectral_centroid(y=y1, sr=sr1)[0]
            spectral_rolloff1 = librosa.feature.spectral_rolloff(y=y1, sr=sr1)[0]
            spectral_bandwidth1 = librosa.feature.spectral_bandwidth(y=y1, sr=sr1)[0]
            spectral_flatness1 = librosa.feature.spectral_flatness(y=y1)[0]
            
            spectral_centroids2 = librosa.feature.spectral_centroid(y=y2, sr=sr2)[0]
            spectral_rolloff2 = librosa.feature.spectral_rolloff(y=y2, sr=sr2)[0]
            spectral_bandwidth2 = librosa.feature.spectral_bandwidth(y=y2, sr=sr2)[0]
            spectral_flatness2 = librosa.feature.spectral_flatness(y=y2)[0]

            # Frequency features
            freqs1 = librosa.fft_frequencies(sr=sr1)
            freqs2 = librosa.fft_frequencies(sr=sr2)
            spectrum1 = np.abs(librosa.stft(y1))
            spectrum2 = np.abs(librosa.stft(y2))
            
            peak_freqs1, _ = find_peaks(np.mean(spectrum1, axis=1), height=np.mean(np.mean(spectrum1, axis=1)))
            peak_freqs2, _ = find_peaks(np.mean(spectrum2, axis=1), height=np.mean(np.mean(spectrum2, axis=1)))
            
            dominant_freq1 = freqs1[peak_freqs1[np.argmax(np.mean(spectrum1, axis=1)[peak_freqs1])]]
            dominant_freq2 = freqs2[peak_freqs2[np.argmax(np.mean(spectrum2, axis=1)[peak_freqs2])]]

            # MFCCs
            mfcc1 = librosa.feature.mfcc(y=y1, sr=sr1, n_mfcc=20)
            mfcc2 = librosa.feature.mfcc(y=y2, sr=sr2, n_mfcc=20)

            # Calculate feature differences
            differences = {}
            thresholds = {
                'pitch': 0.8,
                'amplitude': 0.7,
                'spectral': 0.6,
                'frequency': 0.4,
                'mfcc': 0.5
            }

            # Pitch differences
            pitch_diff = abs(pitch_mean1 - pitch_mean2) / max(pitch_mean1, pitch_mean2)
            pitch_std_diff = abs(pitch_std1 - pitch_std2) / max(pitch_std1, pitch_std2)
            pitch_range_diff = abs(pitch_range1 - pitch_range2) / max(pitch_range1, pitch_range2)
            differences['pitch'] = (pitch_diff + pitch_std_diff + pitch_range_diff) / 3

            # Amplitude differences
            amp_diff = abs(amp_mean1 - amp_mean2) / max(amp_mean1, amp_mean2)
            amp_std_diff = abs(amp_std1 - amp_std2) / max(amp_std1, amp_std2)
            amp_range_diff = abs(amp_range1 - amp_range2) / max(amp_range1, amp_range2)
            differences['amplitude'] = (amp_diff + amp_std_diff + amp_range_diff) / 3

            # Spectral differences
            spectral_diffs = []
            spectral_features = {
                'spectral_centroid': (spectral_centroids1, spectral_centroids2),
                'spectral_rolloff': (spectral_rolloff1, spectral_rolloff2),
                'spectral_bandwidth': (spectral_bandwidth1, spectral_bandwidth2),
                'spectral_flatness': (spectral_flatness1, spectral_flatness2)
            }
            
            for feature_name, (feature1, feature2) in spectral_features.items():
                mean_diff = abs(np.mean(feature1) - np.mean(feature2)) / max(np.mean(feature1), np.mean(feature2))
                std_diff = abs(np.std(feature1) - np.std(feature2)) / max(np.std(feature1), np.std(feature2))
                spectral_diffs.append((mean_diff + std_diff) / 2)
            differences['spectral'] = np.mean(spectral_diffs)

            # Frequency differences
            freq_diff = abs(dominant_freq1 - dominant_freq2) / max(dominant_freq1, dominant_freq2)
            differences['frequency'] = freq_diff

            # MFCC differences
            mfcc_mean_diff = cosine(np.mean(mfcc1, axis=1), np.mean(mfcc2, axis=1))
            mfcc_std_diff = cosine(np.std(mfcc1, axis=1), np.std(mfcc2, axis=1))
            differences['mfcc'] = (mfcc_mean_diff + mfcc_std_diff) / 2

            # Calculate similarities
            similarities = {k: 100 * (1 - v) for k, v in differences.items()}
            
            # Calculate overall similarity with weighted average
            weights = {
                'pitch': 0.4,
                'amplitude': 0.2,
                'spectral': 0.3,
                'frequency': 0.3,
                'mfcc': 0.4
            }
            overall_similarity = sum(similarities[k] * weights[k] for k in similarities.keys())

            # Create spectrum visualization
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 1, 1)
            librosa.display.specshow(librosa.amplitude_to_db(np.abs(spectrum1), ref=np.max), 
                                   sr=sr1, x_axis='time', y_axis='log')
            plt.colorbar(format='%+2.0f dB')
            plt.title(f'Spectrum of {audio1_filename}')
            
            plt.subplot(2, 1, 2)
            librosa.display.specshow(librosa.amplitude_to_db(np.abs(spectrum2), ref=np.max), 
                                   sr=sr2, x_axis='time', y_axis='log')
            plt.colorbar(format='%+2.0f dB')
            plt.title(f'Spectrum of {audio2_filename}')
            
            plt.tight_layout()

            # Save plot to a bytes buffer
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()

            # Determine if same speaker
            is_same_speaker = bool(
                differences['pitch'] < thresholds['pitch'] and
                differences['amplitude'] < thresholds['amplitude'] and
                differences['spectral'] < thresholds['spectral'] and
                differences['frequency'] < thresholds['frequency'] and
                differences['mfcc'] < thresholds['mfcc'] and
                overall_similarity > 50
            )

            logger.info(f"Audio comparison completed successfully. Similarity: {overall_similarity:.2f}%")
            
            return jsonify({
                "overall_similarity": round(overall_similarity, 2),
                "is_same_speaker": is_same_speaker,
                "feature_similarities": {
                    "pitch": round(similarities['pitch'], 2),
                    "amplitude": round(similarities['amplitude'], 2),
                    "spectral": round(similarities['spectral'], 2),
                    "frequency": round(similarities['frequency'], 2),
                    "mfcc": round(similarities['mfcc'], 2)
                },
                "feature_differences": {
                    "pitch": round(differences['pitch'], 4),
                    "amplitude": round(differences['amplitude'], 4),
                    "spectral": round(differences['spectral'], 4),
                    "frequency": round(differences['frequency'], 4),
                    "mfcc": round(differences['mfcc'], 4)
                },
                "feature_thresholds": thresholds,
                "spectrum_plot": plot_base64,
                "message": "Audio comparison completed successfully"
            }), 200

        except Exception as e:
            logger.error(f"Error processing audio comparison: {str(e)}")
            return jsonify({
                "error": "Error processing audio comparison",
                "details": str(e)
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in compare_audio endpoint: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

    finally:
        # Clean up temporary files
        for path in [wav_path1, wav_path2]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception as e:
                    logger.error(f"Error cleaning up temporary file {path}: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Flask application")
    app.run(
        debug=config['DEBUG'],
        host=config['HOST'],
        port=config['PORT']
    )


