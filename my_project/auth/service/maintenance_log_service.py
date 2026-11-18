from typing import List
from my_project.auth.service.general_service import GeneralService
from my_project.auth.dao.maintenance_log_dao import MaintenanceLogDAO
from my_project.auth.domain.maintenance_log import MaintenanceLog


class MaintenanceLogService(GeneralService):
    def __init__(self):
        self._dao = MaintenanceLogDAO()

    def find_by_system_id(self, system_id: int) -> List[MaintenanceLog]:
        return self._dao.find_by_system_id(system_id)
