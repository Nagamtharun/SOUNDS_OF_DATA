import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

# Function to map pixel intensity to frequency
def intensity_to_freq(intensity, min_intensity, max_intensity, min_freq=200, max_freq=2000):
    # Cast to float to avoid numpy uint8 overflow issues (e.g. 1800 out of bounds)
    intensity = float(intensity)
    min_intensity = float(min_intensity)
    max_intensity = float(max_intensity)
    
    if max_intensity == min_intensity:
        return min_freq
    return min_freq + (max_freq - min_freq) * (intensity - min_intensity) / (max_intensity - min_intensity)

def generate_sound_from_data(image_data, duration=10, min_freq=200, max_freq=2000):
    """
    Generates audio from grayscale image data.
    """
    # Normalize pixel intensity values
    min_intensity = np.min(image_data)
    max_intensity = np.max(image_data)

    # Matrix to store sound for each pixel
    pixel_sounds_matrix = []
    
    # We can perform the loop as per user script. 
    # User script: `final_sound += j` inside nested loop.
    
    # Optimizing the concatenation:
    # Concatenating AudioSegments is expensive.
    # It takes ~100ms per append if not careful, N=1600 -> 160s?
    # Actually pydub's sum() is slightly better but still linear-ish.
    # User's script does:
    # for i in pixel_sounds_matrix:
    #    for j in i:
    #        final_sound += j
    
    # Let's collect all segments in a flat list first.
    all_segments = []

    for row in image_data:
        for pixel_intensity in row:
            # Map the pixel intensity to frequency
            freq = intensity_to_freq(pixel_intensity, min_intensity, max_intensity, min_freq, max_freq)
       
            # Generate a sine wave of the corresponding frequency
            sine_wave = Sine(freq).to_audio_segment(duration=duration)
            all_segments.append(sine_wave)
    
    # Create a silent audio segment for final sound
    if not all_segments:
        return AudioSegment.silent(duration=0)
        
    # Efficient concatenation
    # final_sound = sum(all_segments) # this works for AudioSegments if start=0 (but default start is int 0, causes error)
    # Correct usage: sum(all_segments, AudioSegment.silent(duration=0))
    final_sound = sum(all_segments, AudioSegment.silent(duration=0))
    
    return final_sound
