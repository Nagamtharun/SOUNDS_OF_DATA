import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

def intensity_to_freq(intensity, min_intensity, max_intensity, min_freq=200, max_freq=2000):
   if max_intensity == min_intensity: return min_freq
   return min_freq + (max_freq - min_freq) * (intensity - min_intensity) / (max_intensity - min_intensity)

def generate_col_sound_from_data(image_data, duration=1000, min_freq=200, max_freq=2000):
   """
   Generates audio from grayscale image data using column averages.
   """
   min_intensity = np.min(image_data)
   max_intensity = np.max(image_data)

   # Matrix to store sound frequencies for each pixel
   pixel_frequencies_matrix = []

   for row in image_data:
       row_frequencies = []
       for pixel_intensity in row:
           freq = intensity_to_freq(pixel_intensity, min_intensity, max_intensity, min_freq, max_freq)
           row_frequencies.append(freq)
       pixel_frequencies_matrix.append(row_frequencies)

   pixel_frequencies_matrix = np.array(pixel_frequencies_matrix)

   # Calculate the average frequency for each column
   column_avg_frequencies = np.mean(pixel_frequencies_matrix, axis=0)

   final_sound = AudioSegment.silent(duration=0)

   for avg_freq in column_avg_frequencies:
       sine_wave = Sine(avg_freq).to_audio_segment(duration=duration)
       final_sound += sine_wave

   return final_sound
