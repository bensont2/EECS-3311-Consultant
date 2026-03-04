from flask import Flask, redirect, url_for
from config import Config
from models import db
from database import seed_db
from routes.auth import auth_bp
from routes.client import client_bp
from routes.consultant import consultant_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(consultant_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        seed_db()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)