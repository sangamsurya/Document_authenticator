import numpy as np
# from scipy.fftpack import dct, idct
from PIL import Image
import wave
import time
from fingetprint import generate_fingerprint,match_audio
from unique_id import unique_id_generator
from pymongo import MongoClient
import uuid
from typing import Union, Optional, Tuple, BinaryIO
import logging
from io import BytesIO
import struct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define HEADER_BIT_LENGTH for overall payload length
HEADER_BIT_LENGTH = 32 # 4 bytes for storing the total length of data to embed

# Audio configuration constants
SUPPORTED_SAMPLE_WIDTHS = {1: np.uint8, 2: np.int16, 4: np.int32}
MIN_FRAME_RATE = 8000  # Minimum supported frame rate
MAX_FRAME_RATE = 48000  # Maximum supported frame rate
MAX_AUDIO_DURATION = 300  # Maximum audio duration in seconds

# client = MongoClient("mongodb://localhost:27017/")
# db = client["steganography_db"]
# collection = db["audio_fingerprints"]


def audio_to_binary(audio_file: Union[str, BinaryIO]) -> Tuple[str, int]:
    """
    Convert audio file to binary string and extract frame rate.
    
    Args:
        audio_file: Path to audio file or file-like object
        
    Returns:
        Tuple containing:
        - binary_data: Binary string representation of audio
        - frame_rate: Audio frame rate
        
    Raises:
        ValueError: If audio file is invalid or unsupported
        IOError: If there are issues reading the audio file
    """
    try:
        # Ensure the file pointer is at the beginning if it's a file-like object
        if hasattr(audio_file, 'seek'):
            audio_file.seek(0)
            
        with wave.open(audio_file, 'rb') as wav:
            # Extract audio parameters
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frame_rate = wav.getframerate()
            n_frames = wav.getnframes()
            duration = n_frames / frame_rate

            # Validate audio parameters
            if n_channels not in (1, 2):
                raise ValueError(f"Unsupported number of channels: {n_channels}. Only mono and stereo are supported.")
            
            if sample_width not in SUPPORTED_SAMPLE_WIDTHS:
                raise ValueError(f"Unsupported sample width: {sample_width} bytes")
            
            if not MIN_FRAME_RATE <= frame_rate <= MAX_FRAME_RATE:
                raise ValueError(f"Frame rate {frame_rate} Hz is not supported. Must be between {MIN_FRAME_RATE} and {MAX_FRAME_RATE} Hz")
            
            if duration > MAX_AUDIO_DURATION:
                raise ValueError(f"Audio duration {duration:.1f} seconds exceeds maximum allowed duration of {MAX_AUDIO_DURATION} seconds")

            # Log audio details
            logger.info(f"Processing audio file:")
            logger.info(f"  Channels: {n_channels}")
            logger.info(f"  Sample Width: {sample_width} bytes")
            logger.info(f"  Frame Rate: {frame_rate} Hz")
            logger.info(f"  Total Frames: {n_frames}")
            logger.info(f"  Duration: {duration:.2f} seconds")

            # Read audio frames
            audio_frames = wav.readframes(n_frames)
            if not audio_frames:
                raise ValueError("No audio data found in file")

            # Convert to numpy array
            dtype = SUPPORTED_SAMPLE_WIDTHS[sample_width]
            audio_array = np.frombuffer(audio_frames, dtype=dtype)

            # Handle stereo audio by averaging channels
            if n_channels == 2:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(dtype)

            # Normalize audio data to 0-1 range
            audio_array = audio_array.astype(np.float32)
            audio_array = (audio_array - audio_array.min()) / (audio_array.max() - audio_array.min())
            
            # Convert to binary string with proper scaling
            binary_data = ''
            for sample in audio_array:
                # Scale to 16-bit range and convert to binary
                scaled_value = int(sample * 65535)
                binary_data += format(scaled_value, '016b')
            
            return binary_data, frame_rate

    except wave.Error as e:
        error_msg = f"Wave file error: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Error processing audio file: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)


def binary_to_audio(binary_data: str, frame_rate: int, output_file: str) -> None:
    """
    Convert binary string to audio file.
    
    Args:
        binary_data: Binary string representation of audio
        frame_rate: Audio frame rate
        output_file: Path to save the output WAV file
        
    Raises:
        ValueError: If input parameters are invalid
        IOError: If there are issues writing the audio file
    """
    try:
        # Validate input parameters
        if not isinstance(binary_data, str) or not all(c in '01' for c in binary_data):
            raise ValueError("Binary data must be a string of 0s and 1s")
        
        if not isinstance(frame_rate, int) or not MIN_FRAME_RATE <= frame_rate <= MAX_FRAME_RATE:
            raise ValueError(f"Frame rate must be between {MIN_FRAME_RATE} and {MAX_FRAME_RATE} Hz")

        # Ensure binary data length is a multiple of 16 (for 16-bit audio)
        if len(binary_data) % 16 != 0:
            binary_data = binary_data.ljust(len(binary_data) + (16 - len(binary_data) % 16), '0')

        # Convert binary to numpy array
        audio_array = np.zeros(len(binary_data) // 16, dtype=np.float32)
        for i in range(0, len(binary_data), 16):
            # Convert 16 bits to float in 0-1 range
            value = int(binary_data[i:i+16], 2)
            audio_array[i//16] = value / 65535.0

        # Convert to 16-bit audio data
        audio_array = (audio_array * 32767).astype(np.int16)

        n_frames = len(audio_array)

        # Write to WAV file with proper parameters
        with wave.open(output_file, 'wb') as wav:
            wav.setnchannels(1)  # Mono audio
            wav.setsampwidth(2)  # 16-bit audio
            wav.setframerate(frame_rate)
            wav.setnframes(n_frames)
            wav.writeframes(audio_array.tobytes())

        logger.info(f"Audio file saved successfully: {output_file}")
        logger.info(f"  Frame Rate: {frame_rate} Hz")
        logger.info(f"  Total Frames: {n_frames}")
        logger.info(f"  Duration: {n_frames/frame_rate:.2f} seconds")

    except Exception as e:
        logger.error(f"Error converting binary to audio: {str(e)}")
        raise IOError(f"Error converting binary to audio: {str(e)}")



def embed_data_rgb(image_path: Union[str, BytesIO], frame_rate: int, unique_id: str, binary_data: str, output_image_path: Optional[str] = None) -> Image.Image:
    """
    Embeds binary data (audio_binary_data) along with unique_id, its length, and frame_rate 
    into an RGB image using cyclic LSB steganography (R-1st LSB, G-2nd LSB, B-3rd LSB).
    
    Args:
        image_path: Path to the input image or BytesIO object
        frame_rate: Audio frame rate
        unique_id: Unique identifier for the embedded data (expected as 32-bit binary string)
        binary_data: Audio binary data to embed (string of 0s and 1s)
        output_image_path: Optional path to save the stego image
        
    Returns:
        PIL.Image.Image: The stego image with embedded data
        
    Raises:
        ValueError: If the image doesn't have enough capacity for the data or input is invalid
        IOError: If there are issues reading/writing the image
    """
    try:
        image = Image.open(image_path).convert('RGB')
        image_array = np.array(image)

        # Validate input parameters
        if not isinstance(frame_rate, int) or frame_rate <= 0:
            raise ValueError("Frame rate must be a positive integer")
        if not isinstance(unique_id, str) or len(unique_id) != 32 or not all(c in '01' for c in unique_id):
            raise ValueError("Unique ID must be a 32-bit binary string")
        if not isinstance(binary_data, str) or not all(c in '01' for c in binary_data):
            raise ValueError("Binary data must be a string of 0s and 1s")

        # Prepare the full payload: Unique ID + Audio Length + Frame Rate + Audio Binary Data
        audio_data_length_binary = format(len(binary_data), '032b') # Length of audio binary data itself
        frame_rate_binary = format(frame_rate, '016b')

        # This is the full payload *without* the initial overall length header
        payload_without_overall_length_header = unique_id + audio_data_length_binary + frame_rate_binary + binary_data
        
        # Calculate the total length of this payload in bits
        total_payload_length_bits = len(payload_without_overall_length_header)

        # Create the overall length header itself
        if total_payload_length_bits >= (1 << HEADER_BIT_LENGTH): 
            raise ValueError(f"Payload too large to store its length in {HEADER_BIT_LENGTH} bits.")
        overall_length_header = format(total_payload_length_bits, f'0{HEADER_BIT_LENGTH}b')

        # The final binary string to embed (overall_length_header + actual payload)
        final_binary_to_embed = overall_length_header + payload_without_overall_length_header
        total_bits_to_embed = len(final_binary_to_embed)

        # Check capacity
        rows, cols, _ = image_array.shape
        max_capacity_bits = rows * cols * 3 # Max bits can be hidden
        if total_bits_to_embed > max_capacity_bits:
            raise ValueError(f"Insufficient space in the image. Required: {total_bits_to_embed}, Available: {max_capacity_bits}")

        flat_pixels = image_array.flatten()

        # Embed using cyclic LSB pattern (R-1st, G-2nd, B-3rd)
        for i_bit in range(total_bits_to_embed):
            if i_bit >= len(flat_pixels): # Safety break if bits exceed pixel capacity (should be caught by check above)
                break

            # Calculate which pixel component (R, G, B) and its corresponding index in flat_pixels
            pixel_component_index = i_bit // 3 * 3 + (i_bit % 3)
            
            current_pixel_value = flat_pixels[pixel_component_index]
            bit_to_embed = int(final_binary_to_embed[i_bit])

            if i_bit % 3 == 0: # 1st bit of the 3-bit group (R channel's 1st LSB)
                flat_pixels[pixel_component_index] = (current_pixel_value & ~1) | bit_to_embed
            elif i_bit % 3 == 1: # 2nd bit of the 3-bit group (G channel's 2nd LSB)
                flat_pixels[pixel_component_index] = (current_pixel_value & ~2) | (bit_to_embed << 1) 
            else: # 3rd bit of the 3-bit group (B channel's 3rd LSB)
                flat_pixels[pixel_component_index] = (current_pixel_value & ~4) | (bit_to_embed << 2) 
        
        stego_image = Image.fromarray(flat_pixels.reshape(image_array.shape).astype(np.uint8))

        if output_image_path:
            stego_image.save(output_image_path)

        return stego_image

    except Exception as e:
        logger.error(f"Error processing image during embedding: {str(e)}")
        raise IOError(f"Error processing image during embedding: {str(e)}")

def extract_bits_from_image(image_path: Union[str, BytesIO], expected_bits_to_read: Optional[int] = None) -> str:
    """
    Extracts bits from an RGB image using the cyclic pattern (R-1st LSB, G-2nd LSB, B-3rd LSB).
    
    Args:
        image_path: Path to the input image or BytesIO object.
        expected_bits_to_read: Optional. The total number of bits expected to be extracted.
                               If None, extracts all possible bits.
    Returns:
        str: A binary string of extracted bits.
    """
    img = Image.open(image_path).convert('RGB')
    data = np.array(img)
    flat_pixels = data.flatten()

    bit_stream = []
    # Iterate through R, G, B components, extracting 3 bits per pixel
    for i in range(0, len(flat_pixels), 3):
        if i + 2 >= len(flat_pixels): # Ensure we have R, G, and B components
            break

        r_val = flat_pixels[i]
        g_val = flat_pixels[i+1]
        b_val = flat_pixels[i+2]

        # Extract 1st LSB from R
        bit_stream.append(str(r_val & 1))
        # Extract 2nd LSB from G
        bit_stream.append(str((g_val >> 1) & 1))
        # Extract 3rd LSB from B
        bit_stream.append(str((b_val >> 2) & 1))
        
        if expected_bits_to_read and len(bit_stream) >= expected_bits_to_read:
            break

    return ''.join(bit_stream)[:expected_bits_to_read] if expected_bits_to_read else ''.join(bit_stream)

def binary_string_to_bytes(binary_data_string: str) -> bytes:
    """
    Converts a binary string to a bytes object.
    """
    byte_data = bytearray()
    for i in range(0, len(binary_data_string), 8):
        byte_str = binary_data_string[i:i+8]
        if len(byte_str) < 8: # Handle incomplete last byte if any
            break
        byte_data.append(int(byte_str, 2))
    return bytes(byte_data)

def extract_data_from_image(image_path: Union[str, BytesIO]) -> Tuple[str, int, int]:
    """
    Extracts unique ID, audio binary data, and frame rate from a stego image.
    Uses the cyclic LSB extraction pattern (R-1st LSB, G-2nd LSB, B-3rd LSB).
    
    Args:
        image_path: Path to the stego image or BytesIO object
        
    Returns:
        Tuple containing:
        - extracted_audio_binary: Binary string representation of extracted audio
        - frame_rate: Extracted audio frame rate
        - unique_id: Extracted unique ID (as integer)
        
    Raises:
        ValueError: If data cannot be extracted or is corrupted
        IOError: If there are issues reading the image
    """
    try:
        # First, extract enough bits to read the overall length header
        # We need at least HEADER_BIT_LENGTH bits from the start
        initial_bit_stream = extract_bits_from_image(image_path, expected_bits_to_read=HEADER_BIT_LENGTH)

        if len(initial_bit_stream) < HEADER_BIT_LENGTH:
            raise ValueError("Not enough bits to extract overall length header. Image might be too small or corrupted.")
        
        overall_length_header_binary = initial_bit_stream
        total_payload_length_bits = int(overall_length_header_binary, 2)

        # Now extract the full payload based on the total length
        full_bit_stream = extract_bits_from_image(image_path, expected_bits_to_read=HEADER_BIT_LENGTH + total_payload_length_bits)

        if len(full_bit_stream) < HEADER_BIT_LENGTH + total_payload_length_bits:
            raise ValueError("Extracted bit stream is shorter than expected payload length. Image might be corrupted.")

        # Separate the overall length header from the actual payload
        actual_payload_bits = full_bit_stream[HEADER_BIT_LENGTH : HEADER_BIT_LENGTH + total_payload_length_bits]

        # Parse the components from the actual payload
        # Unique ID (32 bits) + Audio Length (32 bits) + Frame Rate (16 bits) + Audio Data
        if len(actual_payload_bits) < (32 + 32 + 16): # Minimum header size
            raise ValueError("Actual payload too short to contain header information.")

        unique_id_binary_str = actual_payload_bits[:32]
        audio_length_binary_str = actual_payload_bits[32:64]
        frame_rate_binary_str = actual_payload_bits[64:80]
        extracted_audio_binary = actual_payload_bits[80:]

        # Convert to appropriate types
        extracted_unique_id = int(unique_id_binary_str, 2)
        extracted_audio_length = int(audio_length_binary_str, 2)
        extracted_frame_rate = int(frame_rate_binary_str, 2)

        # Validate extracted audio length (optional, but good for sanity check)
        if len(extracted_audio_binary) != extracted_audio_length:
            logger.warning(f"Extracted audio binary length ({len(extracted_audio_binary)}) does not match embedded length ({extracted_audio_length}). Data might be truncated.")
        
        return extracted_audio_binary, extracted_frame_rate, extracted_unique_id

    except Exception as e:
        logger.error(f"Error processing image during extraction: {str(e)}")
        raise IOError(f"Error processing image during extraction: {str(e)}")







def main():
    # Input files
    image_path = 'image2.jpg'
    audio_file = 'audio4.wav'
    stego_image_path = 'stego_image_rev.png'
    extracted_audio_file = 'extracted_audio.wav'

    generated_fp = generate_fingerprint(audio_file)

    unique_id = unique_id_generator()

    fingerprint_list = generated_fp.tolist()
    
    # collection.insert_one({"unique_id": unique_id, "fingerprint": fingerprint_list})
    
    unique_id = format(unique_id, '032b')

    
    binary_data , frame_rate = audio_to_binary(audio_file)


    print("Binary length:",len(binary_data))


    image_final_stego = embed_data_rgb(image_path,frame_rate,unique_id, binary_data, stego_image_path)

    print("Embedding Completed Stego Image Saved....")

    print("Extracting Process Started...")

    extracted_binary,frame_rate,unique_id = extract_data_from_image(stego_image_path)
    
    print("Data extracted from RGB image.")
   
    binary_to_audio(extracted_binary, frame_rate, extracted_audio_file)

    print("Audio extracted and saved to", extracted_audio_file)

    # stored_fp_data = collection.find_one({"unique_id": unique_id})

    # stored_fp = np.array(stored_fp_data["fingerprint"])

    extracted_fp = generate_fingerprint(extracted_audio_file)


    cal = match_audio(extracted_fp,stored_fp)
    print(cal)


if __name__ == "__main__":
    main()

