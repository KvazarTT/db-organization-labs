from flask import Blueprint, request, jsonify, make_response
from my_project.auth.controller.irrigation_system_controller import IrrigationSystemController
from my_project.auth.domain.irrigation_system import IrrigationSystem

irrigation_system_bp = Blueprint('irrigation_system_bp', __name__, url_prefix='/api/irrigation-systems')
irrigation_system_controller = IrrigationSystemController()

@irrigation_system_bp.route('', methods=['GET'])
def get_all_irrigation_systems():
    result, status_code = irrigation_system_controller.find_all()
    return make_response(jsonify(result), status_code)

@irrigation_system_bp.route('/<int:system_id>', methods=['GET'])
def get_irrigation_system_by_id(system_id: int):
    result, status_code = irrigation_system_controller.find_by_id(system_id)
    return make_response(jsonify(result), status_code)

@irrigation_system_bp.route('', methods=['POST'])
def create_irrigation_system():
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)
    if not data.get('client_id') or not data.get('system_name'):
        return make_response(jsonify({'error': 'client_id and system_name are required fields'}), 400)
    
    try:
        system = IrrigationSystem.create_from_dto(data)
        result, status_code = irrigation_system_controller.create(system)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@irrigation_system_bp.route('/<int:system_id>', methods=['PUT'])
def update_irrigation_system(system_id: int):
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)
    
    try:
        result, status_code = irrigation_system_controller.update(system_id, data)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@irrigation_system_bp.route('/<int:system_id>', methods=['DELETE'])
def delete_irrigation_system(system_id: int):
    try:
        result, status_code = irrigation_system_controller.delete(system_id)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@irrigation_system_bp.route('/<int:system_id>/client', methods=['GET'])
def get_system_client(system_id: int):
    result, status_code = irrigation_system_controller.get_client_by_system_id(system_id)
    return make_response(jsonify(result), status_code)
