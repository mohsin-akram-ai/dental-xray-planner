# Dental X-Ray Planner

An AI-assisted dental screening tool. The user uploads a dental X-ray or an intra-oral photo. The app detects dental conditions, draws boxes on the image, and suggests a treatment plan with an urgency level.

This tool is for decision support only. The final diagnosis must be made by a licensed dentist.

## Features

- Two input types: X-ray and intra-oral photo
- Object detection with YOLO, with detection boxes drawn on the image
- Warning when the model is not confident (below 50 percent) or finds nothing
- Rule-based treatment suggestions with urgency levels
- Dark X-ray style web interface built with Streamlit
- Automatic tests for the treatment rules and name cleaning

## Current status

The app currently uses the general YOLOv8n model as a placeholder, so it detects everyday objects only. The dental models (X-ray model and photo model) will be added by placing the model files in the models folder:

- models/xray_best.pt (Model A, X-ray)
- models/photo_best.pt (Model B, photo)

Class names from the dental models are cleaned automatically (for example "Periapical_Lesion" becomes "periapical lesion") and matched with the rules in rules.py.

## How to run

1. Create a virtual environment:

        python -m venv .venv

2. Activate it (Windows PowerShell):

        .venv\Scripts\activate

3. Install the libraries:

        pip install -r requirements.txt

4. Start the app:

        streamlit run app.py

## How to run the tests

        pip install pytest
        python -m pytest test_logic.py

## Project files

- app.py: connects everything and shows the web page
- detector.py: loads the YOLO model, detects conditions, and draws the boxes
- rules.py: treatment suggestions and urgency for each condition
- styles.py: page design (CSS) and header
- test_logic.py: automatic tests
- requirements.txt: the list of libraries the project needs