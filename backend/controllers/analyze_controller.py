from flask_restx import Resource
from werkzeug.datastructures import FileStorage
from flask import request
from services.file_service import FileService
from services.analysis_service import AnalysisService
from utils.file_utils import allowed_file

class AnalyzeResource(Resource):
    def __init__(self, api=None, app=None):
        super().__init__()
        self.api = api
        self.app = app
        self.file_service = FileService(app)
        self.analysis_service = AnalysisService()
        
        if api:
            # Define request parser for file upload
            self.file_upload = api.parser()
            self.file_upload.add_argument('file', 
                                        type=FileStorage, 
                                        location='files', 
                                        required=True, 
                                        help='File to analyze')

    def post(self):
        """Handle file upload and analysis"""
        if self.api:
            self.api.expect(self.file_upload)
            
        try:
            if 'file' not in request.files:
                return {'error': 'No file provided'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No selected file'}, 400
                
            if not allowed_file(file.filename):
                return {'error': 'File type not allowed'}, 400

            # Save and process file
            saved_file = self.file_service.save_file(file)
            
            # Analyze file
            analysis_result = self.analysis_service.analyze_file(saved_file)
            
            return analysis_result

        except Exception as e:
            return {'error': str(e)}, 500
