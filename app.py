from flask import Flask, request, send_file, jsonify
import fitz  # PyMuPDF
import base64
from io import BytesIO

app = Flask(__name__)

@app.route("/add-signature", methods=["POST"])
def add_signature():
    try:
        data = request.get_json()

        if not data or "pdf_base64" not in data or "signature_base64" not in data:
            return jsonify({"error": "Missing pdf_base64 or signature_base64"}), 400

        # Decode base64 PDF and signature image
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        signature_bytes = base64.b64decode(data["signature_base64"])

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[-1]

        # Create a pixmap from the image bytes
        img = fitz.Pixmap(signature_bytes)
        page_width = page.rect.width
        page_height = page.rect.height

        # Resize and position signature
        image_width = 200
        image_height = 80
        padding = 40
        x0 = page_width - image_width - padding
        y0 = page_height - image_height - padding

        page.insert_image(fitz.Rect(x0, y0, x0 + image_width, y0 + image_height), pixmap=img)

        output = BytesIO()
        doc.save(output)
        doc.close()
        output.seek(0)

        # Return signed PDF as base64
        return jsonify({
            "signed_pdf_base64": base64.b64encode(output.read()).decode()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
