import numpy as np
from PIL import Image
import values

def generate_image_data(numbers_array):
    """
    Converts numbers array to RGB image and then to grayscale numpy array.
    Returns (rgb_image, grayscale_numpy_array)
    """
    n = int(len(numbers_array)**(0.5))
    # Ensure square
    if n * n != len(numbers_array):
        # Truncate to nearest square if needed, or handle error
        # Based on user script: n = int(len(arr)**0.5), input_array=...reshape(n,n)
        # This implies truncation of extra elements.
        pass

    input_array = np.array(numbers_array[:n*n]).reshape(n,n)

    # Convert the array to an RGB matrix
    rgb_matrix = []

    for row in input_array:
        rgb_row = []
        for value in row:
            rgb_value = values.value_to_rgb(value)
            rgb_row.append(rgb_value)
        rgb_matrix.append(rgb_row)

    # Debug: Check for values out of range
    # Ensure all values are tuples of length 3 with values 0-255
    # If rgb_matrix has bad data, print it.
    
    # Python integer 1800 out of bounds for uint8 suggests we are passing 1800 to np.uint8.
    # This happens if 'rgb_matrix' contains integers instead of tuples?
    # Or if a tuple contains 1800? 
    
    # Let's clean/clip just in case
    cleaned_matrix = []
    for r in rgb_matrix:
        cleaned_row = []
        for c in r:
            # c should be (R, G, B)
            if not isinstance(c, (list, tuple)):
                 # Weird case
                 cleaned_row.append((0,0,0))
            else:
                 # Clamp values 0-255
                 cleaned_row.append(tuple(max(0, min(255, int(x))) for x in c))
        cleaned_matrix.append(cleaned_row)

    # Convert the RGB matrix to a numpy array
    try:
        rgb_array = np.array(cleaned_matrix, dtype=np.uint8)
    except Exception as e:
        print("Error creating numpy array:", e)
        # Fallback dump
        print("Sample data:", cleaned_matrix[:1])
        raise e
    
    # Create an image from the numpy array
    rgb_image = Image.fromarray(rgb_array, mode="RGB")
    
    # Convert to grayscale ("L" mode) as per user script
    grayscale_image = rgb_image.convert("L")
    image_data = np.array(grayscale_image)
    
    return rgb_image, image_data
