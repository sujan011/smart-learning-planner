from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config
from models import db

from routes.auth import auth_bp
from routes.planner import planner_bp
from routes.ai import ai_bp
from routes.main import main


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app)

    # Blueprints
    app.register_blueprint(auth_bp,    url_prefix="/auth")
    app.register_blueprint(planner_bp, url_prefix="/planner")
    app.register_blueprint(ai_bp,      url_prefix="/ai")
    app.register_blueprint(main)

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)