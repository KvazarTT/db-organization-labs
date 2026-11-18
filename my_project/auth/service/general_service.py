from typing import List, Optional, Any


class GeneralService:
    _dao = None

    def find_all(self) -> List[Any]:
        return self._dao.find_all()

    def find_by_id(self, key: int) -> Optional[Any]:
        return self._dao.find_by_id(key)

    def create(self, entity: Any) -> Any:
        return self._dao.create(entity)

    def update(self, key: int, update_data: dict) -> Optional[Any]:
        return self._dao.update(key, update_data)

    def delete(self, key: int) -> bool:
        return self._dao.delete(key)
