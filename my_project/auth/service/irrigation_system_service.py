from typing import List
from my_project.auth.service.general_service import GeneralService
from my_project.auth.dao.irrigation_system_dao import IrrigationSystemDAO
from my_project.auth.domain.irrigation_system import IrrigationSystem

class IrrigationSystemService(GeneralService):
    def __init__(self):
        self._dao = IrrigationSystemDAO()

    def find_by_client_id(self, client_id: int) -> List[IrrigationSystem]:
        return self._dao.find_by_client_id(client_id)

    def find_by_status(self, status: str) -> List[IrrigationSystem]:
        return self._dao.find_by_status(status)
