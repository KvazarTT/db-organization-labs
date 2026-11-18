from typing import Optional, List
from my_project.auth.dao.general_dao import GeneralDAO
from my_project.auth.domain.client import Client
from my_project.auth.domain.irrigation_system import IrrigationSystem


class ClientDAO(GeneralDAO):
    _model = Client

    def find_by_email(self, email: str) -> Optional[Client]:
        return self._session.query(Client).filter_by(email=email).first()

    def get_irrigation_systems_by_client_id(self, client_id: int) -> Optional[List[IrrigationSystem]]:
        client = self.find_by_id(client_id)
        if not client:
            return None
        return client.irrigation_systems
