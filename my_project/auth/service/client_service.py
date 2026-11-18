from typing import Optional, List
from my_project.auth.service.general_service import GeneralService
from my_project.auth.dao.client_dao import ClientDAO
from my_project.auth.domain.client import Client
from my_project.auth.domain.irrigation_system import IrrigationSystem


class ClientService(GeneralService):
    def __init__(self):
        self._dao = ClientDAO()

    def find_by_email(self, email: str) -> Optional[Client]:
        return self._dao.find_by_email(email)

    def get_irrigation_systems_by_client_id(self, client_id: int) -> Optional[List[IrrigationSystem]]:
        return self._dao.get_irrigation_systems_by_client_id(client_id)
