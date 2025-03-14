import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from app.apis.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/apis')
    
    # Serve static files
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')
    
    # Initialize scheduler for cleanup tasks
    scheduler = BackgroundScheduler()
    
    from app.utils.storage import cleanup_inactive_networks
    # Run cleanup every 5 minutes
    scheduler.add_job(
        func=cleanup_inactive_networks,
        trigger='interval',
        minutes=5,
        args=[int(os.getenv('NETWORK_TIMEOUT_MINUTES', 30))]
    )
    
    scheduler.start()
    
    return app 