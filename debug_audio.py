import numToRgb
import genSound
import csv

numbers = []
try:
    with open('test_data.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            for n in row:
                if n.strip():
                    numbers.append(int(float(n)))
                    
    # Simulate flow
    rgb_image, grayscale_data = numToRgb.generate_image_data(numbers)
    print("Grayscale data shape:", grayscale_data.shape)
    print("Grayscale data dtype:", grayscale_data.dtype)
    print("Grayscale max:", grayscale_data.max())
    
    sound = genSound.generate_sound_from_data(grayscale_data)
    sound.export("debug_out.wav", format="wav")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
