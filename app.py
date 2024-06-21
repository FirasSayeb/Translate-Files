from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from flask import Flask, render_template, request, send_file
from deep_translator import GoogleTranslator
from PyPDF2 import PdfReader
import arabic_reshaper
from bidi.algorithm import get_display

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        file = request.files['file']
        select = request.form.get('language')
        exten = request.form.get('extension')

        if file.filename.endswith('.pdf'):
            reader = PdfReader(file)
            page = reader.pages[0]
            text = page.extract_text()
            translated = GoogleTranslator(source='auto', target=select).translate(text)
        else:
            content = file.read().decode('utf-8')
            translated = GoogleTranslator(source='auto', target=select).translate(content)

        if exten == 'pdf':
            output = BytesIO()
            pdf = canvas.Canvas(output, pagesize=letter)
            
            # Register the Arabic font
            pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
            pdf.setFont('Amiri', 12)
            
            # Reshape and reverse the Arabic text for proper rendering
            reshaped_text = arabic_reshaper.reshape(translated)
            bidi_text = get_display(reshaped_text)
            
            # Split the reshaped text into lines
            lines = bidi_text.split('\n')
            y = 750  # Start height for drawing text
            
            for line in lines:
                pdf.drawString(100, y, line)
                y -= 14  # Move to the next line

            pdf.save()
            output.seek(0)
            return send_file(output, as_attachment=True, download_name='translated.pdf', mimetype='application/pdf')
        else:
            output = BytesIO()
            output.write(translated.encode('utf-8'))
            output.seek(0)
            return send_file(output, as_attachment=True, download_name='translated.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
