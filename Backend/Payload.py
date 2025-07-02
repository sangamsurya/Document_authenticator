import wave
import contextlib

def calculate_audio_payload_bits(file_path):
    with contextlib.closing(wave.open(file_path, 'rb')) as audio:
        channels = audio.getnchannels()
        sample_width = audio.getsampwidth()  # in bytes
        frame_rate = audio.getframerate()
        num_frames = audio.getnframes()

        duration = num_frames / frame_rate
        bit_depth = sample_width * 8  # convert bytes to bits

        payload_bits = frame_rate * bit_depth * channels * duration
        return int(payload_bits), duration

# Example usage
audio_path = 'shreya.wav'
payload_bits, duration = calculate_audio_payload_bits(audio_path)
print(f"Payload: {payload_bits} bits")
print(f"Duration: {duration:.2f} seconds")
