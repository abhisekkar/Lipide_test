from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from transformers import pipeline

app = Flask(__name__)
CORS(app)

# Set up the file upload folder 
UPLOAD_FOLDER = 'C:/Users/abhis/flask_app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/summarize', methods=['POST'])
def summarize_document():
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    with open(filepath, 'r') as file:
        content = file.read()
    
    try:
        summary = summarizer(content, max_length=150, min_length=50, do_sample=False)
        return jsonify({'summary': summary[0]['summary_text']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
