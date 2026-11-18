from typing import Tuple, Any
from my_project.auth.controller.general_controller import GeneralController
from my_project.auth.service.maintenance_log_service import MaintenanceLogService
from my_project.auth.service.irrigation_system_service import IrrigationSystemService


class MaintenanceLogController(GeneralController):
    def __init__(self):
        self._service = MaintenanceLogService()
        self._system_service = IrrigationSystemService()

    def get_by_system_id(self, system_id: int) -> Tuple[Any, int]:
        system = self._system_service.find_by_id(system_id)
        if not system:
            return {'message': f'Irrigation system with id {system_id} not found'}, 404
        logs = self._service.find_by_system_id(system_id)
        return [log.put_into_dto() for log in logs], 200
