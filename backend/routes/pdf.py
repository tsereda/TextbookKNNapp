from flask import request, current_app
from flask_restx import Resource, fields
from werkzeug.utils import secure_filename
import os
import PyPDF2

def init_routes(api, ns_pdf, get_db_session):
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @ns_pdf.route('/upload')
    class PDFUpload(Resource):
        @ns_pdf.doc(params={'file': {'description': 'PDF file to upload', 'type': 'file', 'required': True}})
        def post(self):
            """Upload a PDF file"""
            if 'file' not in request.files:
                return {"error": "No file part"}, 400
            file = request.files['file']
            if file.filename == '':
                return {"error": "No selected file"}, 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # Process PDF and add to knowledge graph
                with open(filepath, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                
                with get_db_session() as session:
                    session.run(
                        "CREATE (p:PDF {name: $name, content: $content})",
                        name=filename, content=text
                    )
                
                return {"message": f"File {filename} uploaded and processed successfully"}, 200
            return {"error": "File type not allowed"}, 400

    @ns_pdf.route('/list')
    class PDFList(Resource):
        def get(self):
            """Get a list of uploaded PDFs"""
            with get_db_session() as session:
                result = session.run("MATCH (p:PDF) RETURN p.name AS name")
                files = [record["name"] for record in result]
            return {"files": files}, 200

    @ns_pdf.route('/<string:filename>')
    class PDFGet(Resource):
        def get(self, filename):
            """Get details of a specific PDF"""
            with get_db_session() as session:
                result = session.run(
                    "MATCH (p:PDF {name: $name}) RETURN p",
                    name=filename
                )
                pdf = result.single()
                if pdf:
                    return {"filename": pdf["p"]["name"], "content": pdf["p"]["content"][:200] + "..."}, 200
                return {"error": "File not found"}, 404

    return UPLOAD_FOLDER