from flask import Flask
from .client_route import client_bp
from .irrigation_system_route import irrigation_system_bp

def register_routes(app: Flask) -> None:
    app.register_blueprint(client_bp)
    app.register_blueprint(irrigation_system_bp)

__all__ = ['client_bp', 'irrigation_system_bp', 'register_routes']
