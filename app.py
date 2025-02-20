from flask import Flask, jsonify, redirect, url_for
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv
from extensions import db, jwt, cors, mail
from models.user import User
from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.company_routes import company_bp
from routes.item_routes import item_bp
from routes.purchase_routes import purchase_bp
from routes.sale_routes import sale_bp
from routes.analytics_routes import analytics_bp
from utils.commands import list_users, shell_command
import time
import psycopg2

load_dotenv()

def wait_for_db(max_retries=5, delay_seconds=2):
    current_try = 1
    while current_try <= max_retries:
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            conn.close()
            print("Database connection successful!")
            return True
        except psycopg2.OperationalError as e:
            print(f"Attempt {current_try}/{max_retries}: Database not ready yet... {str(e)}")
            time.sleep(delay_seconds)
            current_try += 1
    return False

def create_app():
    app = Flask(__name__)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"], 
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 1025))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    migrate = Migrate(app, db)

    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Order Manager API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(company_bp, url_prefix='/api')
    app.register_blueprint(item_bp, url_prefix='/api')
    app.register_blueprint(purchase_bp, url_prefix='/api')
    app.register_blueprint(sale_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')

    app.cli.add_command(list_users)
    app.cli.add_command(shell_command)

    @app.route('/')
    def index():
        return redirect(url_for('swagger_ui.show'))

    @app.route('/api')
    def api_index():
        return jsonify({
            "name": "Order Manager API",
            "version": "1.0.0",
            "documentation": "/api/docs",
            "health_check": "/health",
            "endpoints": {
                "auth": {
                    "register": "/api/auth/register",
                    "login": "/api/auth/login",
                    "profile": "/api/auth/me"
                },
                "users": {
                    "list": "/api/users",
                    "create": "/api/users",
                    "get": "/api/users/<id>",
                    "update": "/api/users/<id>",
                    "delete": "/api/users/<id>"
                },
                "companies": {
                    "list": "/api/companies",
                    "create": "/api/companies",
                    "get": "/api/companies/<id>",
                    "update": "/api/companies/<id>",
                    "delete": "/api/companies/<id>"
                },
                "items": {
                    "list": "/api/items",
                    "create": "/api/items",
                    "get": "/api/items/<id>",
                    "update": "/api/items/<id>",
                    "delete": "/api/items/<id>"
                }
            }
        })

    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }), 200

    return app

app = create_app()

if __name__ == '__main__':
    print("Waiting for database to be ready...")
    if not wait_for_db():
        print("Could not connect to database. Exiting.")
        exit(1)
        
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    app.run(host='0.0.0.0', debug=True) 