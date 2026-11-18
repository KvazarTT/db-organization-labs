from typing import Tuple, Any
from my_project.auth.controller.general_controller import GeneralController
from my_project.auth.service.stored_program_service import StoredProgramService


class StoredProgramController:
    def __init__(self):
        self._service = StoredProgramService()

    def insert_maintenance_log(self, data: dict) -> Tuple[Any, int]:
        try:
            created = self._service.insert_maintenance_log(
                system_id=int(data['system_id']),
                technician_name=data['technician_name'],
                description=data['description'],
                service_cost=float(data.get('service_cost', 0.0)),
                maintenance_date=data.get('maintenance_date')
            )
            return created, 201
        except Exception as exc:
            return {'error': GeneralController.format_db_error(exc)}, 400

    def link_client_irrigation_system(self, data: dict) -> Tuple[Any, int]:
        try:
            linked = self._service.link_client_irrigation_system(
                first_name=data['first_name'],
                last_name=data['last_name'],
                system_name=data['system_name'],
                access_role=data.get('access_role', 'operator')
            )
            return linked, 201
        except Exception as exc:
            return {'error': GeneralController.format_db_error(exc)}, 400

    def get_client_system_access_list(self) -> Tuple[Any, int]:
        return self._service.get_client_system_access_list(), 200

    def insert_noname_systems(self, start_num: int = 5) -> Tuple[Any, int]:
        try:
            created_list = self._service.insert_noname_systems(start_num=start_num)
            return {
                'inserted_count': len(created_list),
                'records': created_list
            }, 201
        except Exception as exc:
            return {'error': GeneralController.format_db_error(exc)}, 400

    def get_maintenance_cost_stats(self, stat_type: str = 'AVG') -> Tuple[Any, int]:
        try:
            stats = self._service.get_maintenance_cost_stats(stat_type=stat_type)
            return stats, 200
        except Exception as exc:
            return {'error': GeneralController.format_db_error(exc)}, 400

    def split_clients_with_cursor(self) -> Tuple[Any, int]:
        try:
            summary = self._service.split_clients_with_cursor()
            return summary, 201
        except Exception as exc:
            return {'error': GeneralController.format_db_error(exc)}, 400

    def get_deletion_audit_logs(self) -> Tuple[Any, int]:
        return self._service.get_deletion_audit_logs(), 200
