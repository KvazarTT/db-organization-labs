from typing import List
from my_project.auth.dao.general_dao import GeneralDAO
from my_project.auth.domain.maintenance_log import MaintenanceLog


class MaintenanceLogDAO(GeneralDAO):
    _model = MaintenanceLog

    def find_by_system_id(self, system_id: int) -> List[MaintenanceLog]:
        return self._session.query(MaintenanceLog).filter_by(system_id=system_id).all()
