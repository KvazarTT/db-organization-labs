from typing import Tuple, Any
from my_project.auth.controller.general_controller import GeneralController
from my_project.auth.service.client_service import ClientService

class ClientController(GeneralController):
    def __init__(self):
        self._service = ClientService()

    def get_irrigation_systems(self, client_id: int) -> Tuple[Any, int]:
        client = self._service.find_by_id(client_id)
        if not client:
            return {'message': f'Client with id {client_id} not found'}, 404
        systems = self._service.get_irrigation_systems_by_client_id(client_id)
        return [system.put_into_dto() for system in systems], 200
