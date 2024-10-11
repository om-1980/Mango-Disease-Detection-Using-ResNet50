from flask import Flask, render_template, request, jsonify
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)

# Load the trained model
model = load_model('disease_detector.h5')

# Path to save uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the file
        img_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(img_path)
        
        # Preprocess the image
        img = image.load_img(img_path, target_size=(224, 224))  # Resize to model's expected input size
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Expand dimensions to match batch size
        
        # Normalize the image (if model was trained on normalized data)
        img_array = img_array / 255.0  # Ensure the values are between 0 and 1
        
        # Predict the disease
        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction, axis=1)
        confidence = np.max(prediction)
        
        # Disease class labels
        disease_labels = [
            "Anthracnose", 
            "Bacterial Canker", 
            "Cutting Weevil", 
            "Die Back", 
            "Gall Midge", 
            "Healthy", 
            "Powdery Mildew", 
            "Sooty Mould"
        ]

        disease_info = {
          "Anthracnose": {
              "description": "Anthracnose is a fungal disease that causes dark, sunken lesions on leaves, stems, and fruit. It is more common in humid and warm climates.",
              "symptoms": "Dark, water-soaked spots that develop into sunken, dark lesions.",
              "causes": "Caused by the fungus *Colletotrichum gloeosporioides*.",
              "impact": "Can significantly reduce fruit yield and quality.",
              "control": "Use fungicides and ensure good air circulation around trees by proper pruning."
          },
          "Bacterial Canker": {
              "description": "Bacterial Canker is a serious bacterial disease that leads to cankers, wilting, and dieback of branches.",
              "symptoms": "Cankers on branches, oozing of sap, wilting of leaves.",
              "causes": "Caused by the bacterium *Xanthomonas campestris*.",
              "impact": "If left untreated, the disease can kill young trees and reduce fruit production.",
              "control": "Copper-based sprays, removal of infected branches, and ensuring proper drainage."
          },
          "Gall Midge": {
              "description": "Gall midge is a pest infestation where small flies lay eggs on mango leaves, resulting in galls or swelling.",
              "symptoms": "Swellings or galls on leaves.",
              "causes": "Caused by gall midges laying eggs on the leaf tissues.",
              "impact": "Weakens the tree and reduces fruit yield.",
              "control": "Use of insecticides and regular monitoring of trees."
          },
          "Die Back": {
              "description": "Die back is a fungal disease where parts of the tree's branches start dying back from the tips.",
              "symptoms": "Wilting of leaves, dieback of branches.",
              "causes": "Caused by fungi such as *Botryosphaeria* or *Lasiodiplodia*.",
              "impact": "Can kill branches and reduce yield.",
              "control": "Prune affected areas and apply fungicides."
          },
          "Powdery Mildew": {
              "description": "Powdery mildew is a fungal disease that appears as white powdery patches on leaves and fruit.",
              "symptoms": "White powdery patches on leaves, flowers, and young fruit.",
              "causes": "Caused by the fungus *Oidium mangiferae*.",
              "impact": "Can cause early fruit drop and reduced quality of fruit.",
              "control": "Use sulfur-based fungicides and improve air circulation around the tree."
          },
          "Healthy": {
              "description": "The mango leaf appears to be healthy with no visible disease symptoms.",
              "impact": "The plant is in good health and does not require any treatment."
          },
          "Sooty Mould": {
              "description": "Sooty mold is a fungal disease that appears as black soot-like coating on leaves, fruit, and stems.",
              "symptoms": "Black soot-like coating on leaves and fruit.",
              "causes": "Caused by a fungus growing on honeydew excreted by sucking insects like aphids and scale.",
              "impact": "Blocks photosynthesis, reducing plant growth and fruit production.",
              "control": "Control the insects that produce honeydew and wash off the mold with water."
          }
        }


        # Prepare response data
        result = {
            'prediction': disease_labels[predicted_class[0]],
            'details': disease_info[disease_labels[predicted_class[0]]],
            'confidence_levels': prediction[0].tolist(),  # Include confidence levels for chart
            'labels': disease_labels
        }

        return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)
