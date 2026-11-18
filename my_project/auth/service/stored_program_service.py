from typing import Any, Dict, List, Optional
from my_project.auth.dao.stored_program_dao import StoredProgramDAO


class StoredProgramService:
    def __init__(self):
        self._dao = StoredProgramDAO()

    def insert_maintenance_log(
        self,
        system_id: int,
        technician_name: str,
        description: str,
        service_cost: float = 0.0,
        maintenance_date: Optional[str] = None
    ) -> Dict[str, Any]:
        return self._dao.insert_maintenance_log(
            system_id=system_id,
            technician_name=technician_name,
            description=description,
            service_cost=service_cost,
            maintenance_date=maintenance_date
        )

    def link_client_irrigation_system(
        self,
        first_name: str,
        last_name: str,
        system_name: str,
        access_role: str = 'operator'
    ) -> Dict[str, Any]:
        return self._dao.link_client_irrigation_system(
            first_name=first_name,
            last_name=last_name,
            system_name=system_name,
            access_role=access_role
        )

    def get_client_system_access_list(self) -> List[Dict[str, Any]]:
        return self._dao.get_client_system_access_list()

    def insert_noname_systems(self, start_num: int = 5) -> List[Dict[str, Any]]:
        return self._dao.insert_noname_systems(start_num=start_num)

    def get_maintenance_cost_stats(self, stat_type: str = 'AVG') -> Dict[str, Any]:
        return self._dao.get_maintenance_cost_stats(stat_type=stat_type)

    def split_clients_with_cursor(self) -> Dict[str, Any]:
        return self._dao.split_clients_with_cursor()

    def get_deletion_audit_logs(self) -> List[Dict[str, Any]]:
        return self._dao.get_deletion_audit_logs()
