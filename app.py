import os
import base64
from io import BytesIO
from flask import Flask, request, jsonify
import fitz  # PyMuPDF

app = Flask(__name__)

@app.route("/")
def index():
    return "PDF Signer API is running!"

@app.route("/add-signature", methods=["POST"])
def add_signature():
    try:
        data = request.get_json()

        if not data or 'pdf_base64' not in data or 'signature_base64' not in data:
            return jsonify({'error': 'Missing pdf_base64 or signature_base64'}), 400

        # Decode the base64 PDF
        pdf_bytes = base64.b64decode(data['pdf_base64'])
        signature_bytes = base64.b64decode(data['signature_base64'])

        # Open PDF and signature
        pdf_stream = BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")

        # Load image from bytes
        signature_img_stream = BytesIO(signature_bytes)
        img = fitz.Pixmap(signature_img_stream)

        # Insert image on last page, lower-right corner
        page = doc[-1]
        padding = 40

        image_width = 150  # Adjust size as needed
        image_height = 50

        page_width = page.rect.width
        page_height = page.rect.height

        x0 = page_width - image_width - padding
        y0 = page_height - image_height - padding
        rect = fitz.Rect(x0, y0, x0 + image_width, y0 + image_height)

        page.insert_image(rect, pixmap=img)

        # Export to base64
        output_stream = BytesIO()
        doc.save(output_stream)
        doc.close()
        output_stream.seek(0)
        signed_pdf_base64 = base64.b64encode(output_stream.read()).decode('utf-8')

        return jsonify({"signed_pdf_base64": signed_pdf_base64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
