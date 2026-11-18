import os
import yaml
from pathlib import Path


def load_config(config_path: str = None) -> dict:
    """Loads configuration from app.yml with fallback defaults and environment overrides."""
    if not config_path:
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_path = base_dir / 'config' / 'app.yml'
    else:
        config_path = Path(config_path)

    config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

    db_cfg = config.get('database', {})
    driver = os.getenv('DB_DRIVER', db_cfg.get('driver', 'mysql+pymysql'))
    user = os.getenv('DB_USER', db_cfg.get('user', 'root'))
    password = os.getenv('DB_PASSWORD', db_cfg.get('password', 'password'))
    host = os.getenv('DB_HOST', db_cfg.get('host', 'localhost'))
    port = os.getenv('DB_PORT', db_cfg.get('port', 3306))
    name = os.getenv('DB_NAME', db_cfg.get('name', 'soilsense_db'))

    db_uri = os.getenv('DATABASE_URL')
    if not db_uri:
        db_uri = f"{driver}://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"

    server_cfg = config.get('server', {})
    server_host = os.getenv('SERVER_HOST', server_cfg.get('host', '127.0.0.1'))
    server_port = int(os.getenv('SERVER_PORT', server_cfg.get('port', 5000)))
    server_debug = os.getenv('SERVER_DEBUG', str(server_cfg.get('debug', True))).lower() in ('true', '1')

    return {
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'DB_HOST': host,
        'DB_PORT': int(port),
        'DB_USER': user,
        'DB_PASSWORD': password,
        'DB_NAME': name,
        'SERVER_HOST': server_host,
        'SERVER_PORT': server_port,
        'SERVER_DEBUG': server_debug,
        'RAW_CONFIG': config
    }
