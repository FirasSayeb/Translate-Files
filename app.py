from io import BytesIO
from flask import Flask, render_template, request, send_file
from deep_translator import GoogleTranslator
from PyPDF2 import PdfReader

app = Flask(__name__)

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        file = request.files['file']
        select = request.form.get('language')
        if file.filename.endswith('.pdf') :
            reader = PdfReader(file)
            number_of_pages = len(reader.pages)
            page = reader.pages[0]
            text = page.extract_text()
            translated = GoogleTranslator(source='auto', target=select).translate(text)
        else:
            content = file.read().decode('utf-8') 
            translated = GoogleTranslator(source='auto', target=select).translate(content)
        
        output = BytesIO() 
        output.write(translated.encode('utf-8'))
        output.seek(0) 

        return send_file(output, as_attachment=True, download_name='translated.txt')

if __name__ == '__main__':
    app.run(debug=True)
