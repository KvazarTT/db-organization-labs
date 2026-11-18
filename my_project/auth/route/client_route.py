from flask import Blueprint, request, jsonify, make_response
from my_project.auth.controller.general_controller import GeneralController
from my_project.auth.controller.client_controller import ClientController
from my_project.auth.domain.client import Client

client_bp = Blueprint('client_bp', __name__, url_prefix='/api/clients')
client_controller = ClientController()


@client_bp.route('', methods=['GET'])
def get_all_clients():
    result, status_code = client_controller.find_all()
    return make_response(jsonify(result), status_code)


@client_bp.route('/<int:client_id>', methods=['GET'])
def get_client_by_id(client_id: int):
    result, status_code = client_controller.find_by_id(client_id)
    return make_response(jsonify(result), status_code)


@client_bp.route('', methods=['POST'])
def create_client():
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)
    if not data.get('first_name') or not data.get('last_name') or not data.get('email'):
        return make_response(jsonify({'error': 'first_name, last_name, and email are required fields'}), 400)

    try:
        client = Client.create_from_dto(data)
        result, status_code = client_controller.create(client)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': GeneralController.format_db_error(e)}), 400)


@client_bp.route('/<int:client_id>', methods=['PUT'])
def update_client(client_id: int):
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)

    try:
        result, status_code = client_controller.update(client_id, data)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': GeneralController.format_db_error(e)}), 400)


@client_bp.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id: int):
    try:
        result, status_code = client_controller.delete(client_id)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': GeneralController.format_db_error(e)}), 400)


@client_bp.route('/<int:client_id>/irrigation-systems', methods=['GET'])
def get_client_irrigation_systems(client_id: int):
    result, status_code = client_controller.get_irrigation_systems(client_id)
    return make_response(jsonify(result), status_code)
