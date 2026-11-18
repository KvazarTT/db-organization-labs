from typing import Tuple, Any
from my_project.auth.controller.general_controller import GeneralController
from my_project.auth.service.irrigation_system_service import IrrigationSystemService

class IrrigationSystemController(GeneralController):
    def __init__(self):
        self._service = IrrigationSystemService()

    def get_client_by_system_id(self, system_id: int) -> Tuple[Any, int]:
        system = self._service.find_by_id(system_id)
        if not system:
            return {'message': f'Irrigation system with id {system_id} not found'}, 404
        if not system.client:
            return {'message': 'Client not associated with this system'}, 404
        return system.client.put_into_dto(), 200
