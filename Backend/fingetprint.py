import librosa
from scipy.spatial.distance import cosine
import numpy as np

def generate_fingerprint(audio_file):
    # Load audio and extract MFCC features
    y, sr = librosa.load(audio_file, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

    # Normalize the MFCCs to avoid large value differences
    mfcc = librosa.util.normalize(mfcc, axis=1)

    # Flatten MFCC to create a fingerprint
    fingerprint = mfcc.flatten()

    # Ensure the fingerprint is a numpy array
    return np.array(fingerprint)


import numpy as np
from scipy.spatial.distance import cosine

def match_audio(extracted_fp, stored_fp):
    # Ensure both fingerprints are NumPy arrays
    extracted_fp = np.array(extracted_fp)

    # Check if stored_fp is empty
    if stored_fp.size == 0:
        print("Error: stored_fp is empty!")
        return 0.0  # Return 0% match if stored_fp is empty

    # Ensure stored_fp is a proper 1D array (reshape if necessary)
    stored_fp = np.array(stored_fp).flatten()

    # Check the shapes after reshaping
    print(f"extracted_fp shape: {extracted_fp.shape}")
    print(f"stored_fp shape: {stored_fp.shape}")

    # Ensure both fingerprints have the same length
    min_len = min(len(extracted_fp), len(stored_fp))
    extracted_fp = extracted_fp[:min_len]
    stored_fp = stored_fp[:min_len]

    # Calculate Cosine Similarity
    similarity = 1 - cosine(extracted_fp, stored_fp)
    match_percentage = similarity * 100

    return round(match_percentage, 2)



# extracted = 'extracted_audio.wav'
# original = 'audio4.wav'

# original_fp = generate_fingerprint(original)
# extracted_fp = generate_fingerprint(extracted)

# print(match_audio(extracted_fp,original_fp))


