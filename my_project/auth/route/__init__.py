from flask import Flask
from .client_route import client_bp
from .irrigation_system_route import irrigation_system_bp
from .maintenance_log_route import maintenance_log_bp
from .stored_program_route import stored_program_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(client_bp)
    app.register_blueprint(irrigation_system_bp)
    app.register_blueprint(maintenance_log_bp)
    app.register_blueprint(stored_program_bp)


__all__ = [
    'client_bp',
    'irrigation_system_bp',
    'maintenance_log_bp',
    'stored_program_bp',
    'register_routes'
]
