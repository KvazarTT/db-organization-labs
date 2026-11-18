from flask import Blueprint, request, jsonify, make_response
from my_project.auth.controller.stored_program_controller import StoredProgramController

stored_program_bp = Blueprint('stored_program_bp', __name__, url_prefix='/api/stored-programs')
stored_program_controller = StoredProgramController()


@stored_program_bp.route('/maintenance-logs', methods=['POST'])
def sp_insert_maintenance_log():
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)
    if data.get('system_id') is None or not data.get('technician_name') or not data.get('description'):
        return make_response(jsonify({'error': 'system_id, technician_name, and description are required fields'}), 400)

    result, status_code = stored_program_controller.insert_maintenance_log(data)
    return make_response(jsonify(result), status_code)


@stored_program_bp.route('/client-system-access', methods=['POST'])
def sp_link_client_irrigation_system():
    data = request.get_json(silent=True)
    if not data:
        return make_response(jsonify({'error': 'JSON payload is required'}), 400)
    if not data.get('first_name') or not data.get('last_name') or not data.get('system_name'):
        return make_response(jsonify({'error': 'first_name, last_name, and system_name are required fields'}), 400)

    result, status_code = stored_program_controller.link_client_irrigation_system(data)
    return make_response(jsonify(result), status_code)


@stored_program_bp.route('/client-system-access', methods=['GET'])
def get_client_system_access_list():
    result, status_code = stored_program_controller.get_client_system_access_list()
    return make_response(jsonify(result), status_code)


@stored_program_bp.route('/noname-systems', methods=['POST'])
def sp_insert_noname_systems():
    data = request.get_json(silent=True) or {}
    start_num = data.get('start_num', 5)
    try:
        start_num_int = int(start_num)
    except (TypeError, ValueError):
        return make_response(jsonify({'error': 'start_num must be an integer'}), 400)

    result, status_code = stored_program_controller.insert_noname_systems(start_num_int)
    return make_response(jsonify(result), status_code)


@stored_program_bp.route('/maintenance-cost-stats', methods=['GET'])
def sp_get_maintenance_cost_stats():
    stat_type = request.args.get('op', 'AVG')
    result, status_code = stored_program_controller.get_maintenance_cost_stats(stat_type)
    return make_response(jsonify(result), status_code)


@stored_program_bp.route('/split-clients-cursor', methods=['POST'])
def sp_split_clients_with_cursor():
    result, status_code = stored_program_controller.split_clients_with_cursor()
    return make_response(jsonify(result), status_code)


@stored_program_bp.route('/deletion-audit-logs', methods=['GET'])
def get_deletion_audit_logs():
    result, status_code = stored_program_controller.get_deletion_audit_logs()
    return make_response(jsonify(result), status_code)
