import os
import sys
from pathlib import Path
from datetime import date
from flask import Flask, jsonify
from sqlalchemy import text, create_engine

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from my_project import db
from my_project.utils.config_loader import load_config
from my_project.auth.route import register_routes
from my_project.auth.domain import Client, IrrigationSystem

def get_working_database_uri(cfg: dict) -> str:
    """Verifies MySQL connection, falling back to SQLite if credentials or server are not ready."""
    db_uri = cfg.get('SQLALCHEMY_DATABASE_URI', '')
    if 'sqlite' in db_uri.lower():
        return db_uri
    try:
        engine = create_engine(db_uri, connect_args={'connect_timeout': 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[Database] Successfully connected to MySQL.")
        return db_uri
    except Exception as e:
        sqlite_file = BASE_DIR / "soilsense_mvp.db"
        sqlite_uri = f"sqlite:///{sqlite_file.as_posix()}"
        print(f"[Notice] MySQL not reached with config/app.yml ({e}).")
        print(f"[MVP Auto-Fallback] Using local SQLite database: {sqlite_uri}")
        return sqlite_uri

def seed_initial_data():
    """Populates initial seed data if database is empty."""
    try:
        if db.session.query(Client).first() is None:
            c1 = Client(first_name='Олег', last_name='Петренко', email='oleg.p@example.com', phone='+380501234567', registration_date=date(2025, 5, 10))
            c2 = Client(first_name='Марія', last_name='Коваль', email='maria.k@example.com', phone='+380671234567', registration_date=date(2025, 6, 15))
            c3 = Client(first_name='Іван', last_name='Бойко', email='ivan.b@example.com', phone='+380631234567', registration_date=date(2025, 7, 20))
            c4 = Client(first_name='Анна', last_name='Шевченко', email='anna.sh@example.com', phone='+380991234567', registration_date=date(2025, 8, 5))
            c5 = Client(first_name='Сергій', last_name='Мельник', email='serg.m@example.com', phone='+380981234567', registration_date=date(2025, 9, 1))
            db.session.add_all([c1, c2, c3, c4, c5])
            db.session.commit()

            s1 = IrrigationSystem(client_id=c1.id, system_name='Полив Теплиця 1', status='active')
            s2 = IrrigationSystem(client_id=c1.id, system_name='Полив Відкритий Ґрунт', status='active')
            s3 = IrrigationSystem(client_id=c2.id, system_name='Смарт-сад', status='maintenance')
            s4 = IrrigationSystem(client_id=c3.id, system_name='Поле Пшениця', status='active')
            s5 = IrrigationSystem(client_id=c4.id, system_name='Газон Біля Дому', status='active')
            db.session.add_all([s1, s2, s3, s4, s5])
            db.session.commit()
            print("[Database] Seeded initial data for clients and irrigation_systems.")
    except Exception as e:
        db.session.rollback()
        print(f"[Database] Seed warning: {e}")

def create_app(config_override: dict = None) -> Flask:
    app = Flask(__name__)
    cfg = load_config()

    if config_override and 'SQLALCHEMY_DATABASE_URI' in config_override:
        db_uri = config_override['SQLALCHEMY_DATABASE_URI']
    else:
        db_uri = get_working_database_uri(cfg)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = cfg['SQLALCHEMY_TRACK_MODIFICATIONS']
    
    if config_override:
        app.config.update(config_override)

    db.init_app(app)
    register_routes(app)

    with app.app_context():
        try:
            db.create_all()
            # If not in testing mode, seed sample data
            if not app.config.get('TESTING'):
                seed_initial_data()
        except Exception as e:
            print(f"[Notice] Table creation / seed warning: {e}")

    @app.route('/')
    def index():
        return jsonify({
            'status': 'online',
            'project': 'SoilSense Back-End REST API (MVP)',
            'lab': 'Laboratory Work #4 (Flask + MySQL / SQLite Fallback)',
            'tables': ['clients', 'irrigation_systems'],
            'author': 'Matvii Ivkov (Group IR-22)',
            'endpoints': {
                'clients': '/api/clients',
                'client_by_id': '/api/clients/<id>',
                'client_irrigation_systems': '/api/clients/<id>/irrigation-systems',
                'irrigation_systems': '/api/irrigation-systems',
                'irrigation_system_by_id': '/api/irrigation-systems/<id>',
                'irrigation_system_client': '/api/irrigation-systems/<id>/client'
            }
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    cfg = load_config()
    host = cfg.get('SERVER_HOST', '127.0.0.1')
    port = cfg.get('SERVER_PORT', 5000)
    debug = cfg.get('SERVER_DEBUG', False)
    print(f"Starting SoilSense MVP server at http://{host}:{port}/")
    app.run(host=host, port=port, debug=debug)
