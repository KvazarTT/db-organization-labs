from datetime import datetime
from decimal import Decimal
from flask import Blueprint, request, jsonify, make_response
from my_project.auth.controller.general_controller import GeneralController
from my_project.auth.controller.maintenance_log_controller import MaintenanceLogController
from my_project.auth.domain.maintenance_log import MaintenanceLog

maintenance_log_bp = Blueprint('maintenance_log_bp', __name__, url_prefix='/api/maintenance-logs')
maintenance_log_controller = MaintenanceLogController()


@maintenance_log_bp.route('', methods=['GET'])
def get_all_maintenance_logs():
    result, status_code = maintenance_log_controller.find_all()
    return make_response(jsonify(result), status_code)


@maintenance_log_bp.route('/<int:log_id>', methods=['GET'])
def get_maintenance_log_by_id(log_id: int):
    result, status_code = maintenance_log_controller.find_by_id(log_id)
    return make_response(jsonify(result), status_code)


@maintenance_log_bp.route('', methods=['POST'])
def create_maintenance_log():
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)
    if data.get('system_id') is None or not data.get('technician_name') or not data.get('description'):
        return make_response(jsonify({'error': 'system_id, technician_name, and description are required fields'}), 400)

    try:
        log_entry = MaintenanceLog.create_from_dto(data)
        result, status_code = maintenance_log_controller.create(log_entry)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': GeneralController.format_db_error(e)}), 400)


@maintenance_log_bp.route('/<int:log_id>', methods=['PUT'])
def update_maintenance_log(log_id: int):
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)

    update_payload = dict(data)
    if isinstance(update_payload.get('maintenance_date'), str):
        try:
            update_payload['maintenance_date'] = datetime.strptime(
                update_payload['maintenance_date'], '%Y-%m-%d'
            ).date()
        except ValueError:
            return make_response(jsonify({'error': 'maintenance_date must be YYYY-MM-DD'}), 400)
    if 'service_cost' in update_payload and update_payload['service_cost'] is not None:
        update_payload['service_cost'] = Decimal(str(update_payload['service_cost']))

    try:
        result, status_code = maintenance_log_controller.update(log_id, update_payload)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': GeneralController.format_db_error(e)}), 400)


@maintenance_log_bp.route('/<int:log_id>', methods=['DELETE'])
def delete_maintenance_log(log_id: int):
    try:
        result, status_code = maintenance_log_controller.delete(log_id)
        return make_response(jsonify(result), status_code)
    except Exception as e:
        return make_response(jsonify({'error': GeneralController.format_db_error(e)}), 400)
