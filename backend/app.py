from flask import Flask, jsonify
from flask_restx import Api, Resource, Namespace, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='File Upload API',
    description='A simple API with file upload capability',
    doc='/docs',  # Swagger UI at /docs
)

UPLOAD_FOLDER = 'tmp_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- Root namespace ----------
root_ns = Namespace('', description='Root operations', path='/')

@root_ns.route('/')
class Hello(Resource):
    def get(self):
        return {
            'message': 'Hello, this is the root endpoint.',
            'available_endpoints': {
                'GET /': 'This welcome message',
                'GET /docs': 'Swagger documentation',
                'POST /upload': 'File upload endpoint',
                'GET /health': 'Health check endpoint'
            }
        }

@root_ns.route('/health')
class HealthCheck(Resource):
    def get(self):
        return {'status': 'healthy', 'message': 'API is running'}

# ---------- Upload namespace ----------
upload_ns = Namespace('upload', description='File upload operations', path='/upload')

upload_parser = reqparse.RequestParser()
upload_parser.add_argument(
    'file',
    location='files',
    type=FileStorage,
    required=True,
    help='File to upload'
)

@upload_ns.route('/')
class Upload(Resource):
    @upload_ns.expect(upload_parser)
    @upload_ns.doc(responses={200: 'Success', 400: 'Validation Error', 415: 'Unsupported Type', 500: 'Internal Error'})
    def post(self):
        """Upload a file"""
        try:
            args = upload_parser.parse_args()
            uploaded_file = args['file']

            if not uploaded_file or uploaded_file.filename == '':
                return {'error': 'No file selected'}, 400

            filename = secure_filename(uploaded_file.filename)

            if not allowed_file(filename):
                return {'error': f'File type not allowed. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}'}, 415

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(filepath)

            return {
                'message': 'File uploaded successfully',
                'filename': filename,
                'type': uploaded_file.content_type,
                'size': os.path.getsize(filepath),
                'path': filepath
            }, 200

        except Exception as e:
            return {'error': str(e)}, 500

# ---------- Error handlers ----------
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'message': 'The requested URL was not found on the server.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ---------- Register namespaces ----------
api.add_namespace(root_ns)
api.add_namespace(upload_ns)

if __name__ == '__main__':
    print("\n=== Flask API Server Starting ===")
    print("  Root:   http://localhost:8000/")
    print("  Docs:   http://localhost:8000/docs")
    print("  Health: http://localhost:8000/health")
    print("  Upload: http://localhost:8000/upload  (POST)")
    print("=================================\n")
    app.run(debug=True, host='0.0.0.0', port=8000)
