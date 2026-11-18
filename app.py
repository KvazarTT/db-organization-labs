import sys
from pathlib import Path
from flask import Flask, jsonify
import pymysql

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from my_project import db
from my_project.utils import load_config, execute_sql_file
from my_project.auth.route import register_routes


def ensure_lab5_database_ready(cfg: dict, force_reset: bool = False) -> None:
    """Ensures soilsense_db has all Lab 5 tables, triggers, functions, and procedures loaded."""
    if force_reset:
        execute_sql_file(cfg)
        return

    conn = pymysql.connect(
        host=cfg['DB_HOST'],
        port=cfg['DB_PORT'],
        user=cfg['DB_USER'],
        password=cfg['DB_PASSWORD'],
        charset='utf8mb4'
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.routines "
                "WHERE routine_schema = %s AND routine_name = 'sp_split_clients_with_cursor'",
                (cfg['DB_NAME'],)
            )
            exists = cur.fetchone()[0] > 0
        if not exists:
            execute_sql_file(cfg)
    finally:
        conn.close()


def create_app(config_override: dict = None) -> Flask:
    app = Flask(__name__)
    cfg = load_config()

    db_uri = (
        config_override['SQLALCHEMY_DATABASE_URI']
        if config_override and 'SQLALCHEMY_DATABASE_URI' in config_override
        else cfg['SQLALCHEMY_DATABASE_URI']
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = cfg['SQLALCHEMY_TRACK_MODIFICATIONS']

    if config_override:
        app.config.update(config_override)

    if not app.config.get('TESTING'):
        ensure_lab5_database_ready(cfg, force_reset=bool(app.config.get('RESET_DB', False)))

    db.init_app(app)
    register_routes(app)

    @app.route('/')
    def index():
        return jsonify({
            'status': 'online',
            'project': 'SoilSense Back-End REST API',
            'lab': 'Laboratory Work #5 (MySQL Stored Programs: Triggers, Procedures, Functions, Cursors)',
            'tables': [
                'clients',
                'irrigation_systems',
                'maintenance_logs',
                'client_system_access',
                'deletion_audit_log'
            ],
            'author': 'Matvii Ivkov (Group IR-22)',
            'endpoints': {
                'clients': '/api/clients',
                'irrigation_systems': '/api/irrigation-systems',
                'maintenance_logs': '/api/maintenance-logs',
                'system_maintenance_logs': '/api/irrigation-systems/<id>/maintenance-logs',
                'sp_insert_maintenance_log': '/api/stored-programs/maintenance-logs',
                'sp_link_client_system': '/api/stored-programs/client-system-access',
                'sp_noname_systems': '/api/stored-programs/noname-systems',
                'sp_maintenance_cost_stats': '/api/stored-programs/maintenance-cost-stats?op=AVG',
                'sp_split_clients_cursor': '/api/stored-programs/split-clients-cursor',
                'deletion_audit_logs': '/api/stored-programs/deletion-audit-logs'
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
    print(f"Starting SoilSense Lab 5 server at http://{host}:{port}/")
    app.run(host=host, port=port, debug=debug)
