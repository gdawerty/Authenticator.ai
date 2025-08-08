from flask import Flask
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Register routes (Blueprints)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
