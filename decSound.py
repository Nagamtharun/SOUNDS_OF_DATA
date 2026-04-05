import numpy as np
from pydub import AudioSegment
from PIL import Image
import csv
import math

def decode_audio_to_data(filepath, duration_ms=10, min_freq=200, max_freq=2000):
    """
    Decodes an audio file back into an integer intensity matrix and grayscale image.
    """
    audio = AudioSegment.from_file(filepath, format="wav")
    
    # We need to process it in chunks of duration_ms
    chunk_length_ms = duration_ms
    chunks = len(audio) // chunk_length_ms
    
    intensities = []
    
    for i in range(chunks):
        chunk = audio[i * chunk_length_ms : (i + 1) * chunk_length_ms]
        
        # Convert chunk to raw data
        samples = np.array(chunk.get_array_of_samples())
        sample_rate = chunk.frame_rate
        
        # Perform FFT
        if len(samples) == 0:
            continue
            
        fft_out = np.fft.rfft(samples)
        freqs = np.fft.rfftfreq(len(samples), d=1.0/sample_rate)
        
        # Find dominant frequency
        idx_max = np.argmax(np.abs(fft_out))
        dominant_freq = freqs[idx_max]
        
        # Map frequency to intensity (0-255)
        # Handle bounds
        if dominant_freq < min_freq:
            dominant_freq = min_freq
        if dominant_freq > max_freq:
            dominant_freq = max_freq
            
        # Reverse mapping: freq = min_freq + (max_freq - min_freq) * (intensity / 255)
        intensity_normalized = (dominant_freq - min_freq) / (max_freq - min_freq) if max_freq > min_freq else 0
        intensity = int(round(intensity_normalized * 255))
        
        # Ensure it stays within bounds
        intensity = max(0, min(255, intensity))
        intensities.append(intensity)
        
    # Reconstruct matrix
    num_elements = len(intensities)
    if num_elements == 0:
        return None, None
        
    N = int(math.sqrt(num_elements))
    
    # Trim to perfect square if necessary
    intensities = intensities[:N*N]
    
    # Generate colored matrix and reconstructed values (1-100 approx)
    import values as val_module
    color_matrix = []
    reconstructed_values = []
    
    for intensity in intensities:
        # Revert 0-255 scale back to 1-100 typical scale
        mapped_val = int(round((intensity / 255.0) * 100))
        
        # Clip to ensure valid mappings
        mapped_val = max(1, min(100, mapped_val))
        reconstructed_values.append(mapped_val)
        
        rgb = val_module.value_to_rgb(mapped_val)
        color_matrix.append(rgb)
        
    color_array = np.array(color_matrix, dtype=np.uint8).reshape((N, N, 3))
    image = Image.fromarray(color_array, mode="RGB")
    
    # Collect metadata
    metadata = {
        'sample_rate': audio.frame_rate,
        'bit_depth': audio.sample_width * 8,
        'total_samples': int(audio.frame_count()),
        'duration_sec': round(len(audio) / 1000.0, 2),
        'encoding': f"PCM-{audio.sample_width * 8}LE" # Approximation for standard wav
    }
    
    return image, reconstructed_values, metadata

