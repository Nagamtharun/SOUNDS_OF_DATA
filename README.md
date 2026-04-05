# The Sound of Data

This project visualizes data by converting CSV files into images and then into sound.

## Features

- **Upload Data**: Upload your CSV datasets.
- **Visualize**: See your data as a generated RGB image based on value mappings.
- **Sonification**: Listen to your data converted into audio frequencies.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser at `http://localhost:5000`.

## Project Structure

- `app.py`: Main Flask application.
- `values.py`: Logic for mapping data values to colors.
- `gen_csv.py`: Utility to generate test data.
- `templates/`: HTML templates.
- `static/`: CSS and generated assets.
