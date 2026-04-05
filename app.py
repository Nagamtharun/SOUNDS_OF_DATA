from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
import os
import numpy as np
from PIL import Image
import csv
import io
import uuid
import numToRgb
import genSound
import vizSound
import decSound
import traceback
import base64
import json
import io

# Configuration
IS_VERCEL = os.environ.get('VERCEL') == '1'

if IS_VERCEL:
    UPLOAD_FOLDER = '/tmp/uploads'
    GENERATED_FOLDER = '/tmp/generated'
else:
    # Use explicit absolute path based on __file__ to avoid issues
    import sys
    base_path = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(base_path, 'uploads')
    GENERATED_FOLDER = os.path.join(base_path, 'static', 'generated')

ALLOWED_EXTENSIONS = {'csv'}
ALLOWED_AUDIO_EXTENSIONS = {'wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'dev-secret-key-sound-of-data'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

@app.route('/files/<filename>')
def serve_generated_file(filename):
    return send_file(os.path.join(GENERATED_FOLDER, filename))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def get_numbers_from_csv(filepath):
    numbers_array = []
    with open(filepath, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            for num in row:
                try:
                    if num.strip():
                        val = float(num)
                        # Ensure value is integer if needed, or keeping as float?
                        # numToRgb expects values that map to colors. value_to_rgb takes int.
                        numbers_array.append(int(val))
                except ValueError:
                    continue
    return numbers_array

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload_page')
def upload_page():
    # Fetch recent uploads
    history = []
    try:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                if f.endswith('.csv'):
                    filepath = os.path.join(UPLOAD_FOLDER, f)
                    # Get display name (remove UUID prefix if present)
                    display_name = f.split('_', 1)[1] if '_' in f else f
                    history.append({
                        'filename': f,
                        'display_name': display_name,
                        'timestamp': os.path.getctime(filepath)
                    })
            # Sort by newest first
            history.sort(key=lambda x: x['timestamp'], reverse=True)
    except Exception as e:
        print(f"Error fetching history: {e}")

    return render_template('upload.html', history=history)

@app.route('/upload_action', methods=['POST'])
def upload_file_action():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('upload_page'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('upload_page'))
    
    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            numbers_array = get_numbers_from_csv(filepath)
            if not numbers_array:
                 flash('No valid numbers found in CSV.', 'error')
                 return redirect(url_for('upload_page'))

            rgb_image, _ = numToRgb.generate_image_data(numbers_array)
            img_byte_arr = io.BytesIO()
            rgb_image.save(img_byte_arr, format='PNG')
            img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            image_url = f"data:image/png;base64,{img_b64}"
            
            numbers_json = json.dumps(numbers_array)
            
            return render_template('visualize.html', filename=file.filename, image_url=image_url, numbers_json=numbers_json)
        except Exception as e:
            traceback.print_exc()
            flash(f"Error generating image: {str(e)}", 'error')
            return redirect(url_for('upload_page'))
    
    flash('Invalid file type. Please upload a CSV.', 'error')
    return redirect(url_for('upload_page'))

@app.route('/visualize_page')
def visualize_page():
    filename = request.args.get('filename')
    if not filename:
        return redirect(url_for('upload_page'))
    
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        flash('File not found.', 'error')
        return redirect(url_for('upload_page'))
        
    output_filename = f"img_{filename}.png"
    output_path = os.path.join(GENERATED_FOLDER, output_filename)
    
    # Generate image if not exists
    if not os.path.exists(output_path):
        try:
            numbers_array = get_numbers_from_csv(filepath)
            if not numbers_array:
                 flash('No valid numbers found in CSV.', 'error')
                 return redirect(url_for('upload_page'))

            # Generate
            rgb_image, _ = numToRgb.generate_image_data(numbers_array)
            rgb_image.save(output_path)
        except Exception as e:
            traceback.print_exc()
            flash(f"Error generating image: {str(e)}", 'error')
            return redirect(url_for('upload_page'))
    
    image_url = url_for('serve_generated_file', filename=output_filename)
    return render_template('visualize.html', filename=filename, image_url=image_url)

@app.route('/generate_audio_action', methods=['POST'])
def generate_audio_action():
    filename = request.form.get('filename')
    duration = int(request.form.get('duration', 10))
    min_freq = int(request.form.get('min_freq', 200))
    max_freq = int(request.form.get('max_freq', 2000))
    numbers_json = request.form.get('numbers_json')
    
    if not numbers_json:
        flash("Data lost between requests. Please start over.", "error")
        return redirect(url_for('upload_page'))
        
    try:
        numbers_array = json.loads(numbers_json)
        _, grayscale_data = numToRgb.generate_image_data(numbers_array)
        
        final_sound = genSound.generate_sound_from_data(grayscale_data, duration=duration, min_freq=min_freq, max_freq=max_freq)
        
        sound_byte_arr = io.BytesIO()
        final_sound.export(sound_byte_arr, format="wav")
        sound_b64 = base64.b64encode(sound_byte_arr.getvalue()).decode('utf-8')
        audio_url = f"data:audio/wav;base64,{sound_b64}"
        
        return render_template('sonify.html', audio_url=audio_url, filename=filename)
        
    except Exception as e:
        traceback.print_exc()
        flash(f"Error generating audio: {str(e)}", 'error')
        return redirect(url_for('upload_page'))

@app.route('/sonify_page')
def sonify_page():
    filename = request.args.get('filename') # Just for context if needed
    audio_file = request.args.get('audio_file')
    
    if not audio_file:
         return redirect(url_for('upload_page'))
         
    audio_url = url_for('serve_generated_file', filename=audio_file)
    return render_template('sonify.html', audio_url=audio_url, filename=filename)

@app.route('/reverse_upload_page')
def reverse_upload_page():
    return render_template('reverse_upload.html')

@app.route('/reverse_action', methods=['POST'])
def reverse_action():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('reverse_upload_page'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('reverse_upload_page'))
    
    if file and allowed_audio_file(file.filename):
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        duration = int(request.form.get('duration', 10))
        min_freq = int(request.form.get('min_freq', 200))
        max_freq = int(request.form.get('max_freq', 2000))
        
        try:
            image, intensities, metadata = decSound.decode_audio_to_data(filepath, duration_ms=duration, min_freq=min_freq, max_freq=max_freq)
            if image is None:
                flash('Could not decode audio.', 'error')
                return redirect(url_for('reverse_upload_page'))
                
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            image_url = f"data:image/png;base64,{base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')}"
            
            num_elements = len(intensities)
            N = int(num_elements**0.5)
            csv_data = [list(intensities[i*N:(i+1)*N]) for i in range(N)]
            
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            for row in csv_data: writer.writerow(row)
            csv_b64 = base64.b64encode(csv_buffer.getvalue().encode('utf-8')).decode('utf-8')
            csv_url = f"data:text/csv;base64,{csv_b64}"
            
            return render_template('decoded.html', image_url=image_url, csv_url=csv_url, metadata=metadata, csv_data=csv_data)
            
        except Exception as e:
            traceback.print_exc()
            flash(f"Error decoding: {str(e)}", 'error')
            return redirect(url_for('reverse_upload_page'))
            
    flash('Invalid file type. Please upload a WAV.', 'error')
    return redirect(url_for('reverse_upload_page'))

@app.route('/decoded_page')
def decoded_page():
    image_file = request.args.get('image_file')
    csv_file = request.args.get('csv_file')
    
    if not image_file or not csv_file:
         return redirect(url_for('reverse_upload_page'))
         
    image_url = url_for('serve_generated_file', filename=image_file)
    csv_url = url_for('serve_generated_file', filename=csv_file)
    
    metadata = {
        'sample_rate': request.args.get('sample_rate'),
        'bit_depth': request.args.get('bit_depth'),
        'total_samples': request.args.get('total_samples'),
        'duration_sec': request.args.get('duration_sec'),
        'encoding': request.args.get('encoding')
    }
    
    # We also need the table data to display in the UI like in the picture
    csv_data = []
    csv_path = os.path.join(GENERATED_FOLDER, csv_file)
    if os.path.exists(csv_path):
        with open(csv_path, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                csv_data.append(row)
    
    return render_template('decoded.html', image_url=image_url, csv_url=csv_url, metadata=metadata, csv_data=csv_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
