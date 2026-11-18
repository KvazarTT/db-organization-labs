from typing import List
from my_project.auth.dao.general_dao import GeneralDAO
from my_project.auth.domain.irrigation_system import IrrigationSystem

class IrrigationSystemDAO(GeneralDAO):
    _model = IrrigationSystem

    def find_by_client_id(self, client_id: int) -> List[IrrigationSystem]:
        return self._session.query(IrrigationSystem).filter_by(client_id=client_id).all()

    def find_by_status(self, status: str) -> List[IrrigationSystem]:
        return self._session.query(IrrigationSystem).filter_by(status=status).all()
