from typing import List, Optional, Any
from my_project import db


class GeneralDAO:
    _model = None

    def __init__(self, session=None):
        self._session = session or db.session

    def find_all(self) -> List[Any]:
        return self._session.query(self._model).all()

    def find_by_id(self, key: int) -> Optional[Any]:
        return self._session.get(self._model, key)

    def create(self, obj: Any) -> Any:
        try:
            self._session.add(obj)
            self._session.commit()
            return obj
        except Exception:
            self._session.rollback()
            raise

    def update(self, key: int, update_data: dict) -> Optional[Any]:
        obj = self.find_by_id(key)
        if not obj:
            return None
        try:
            for field, value in update_data.items():
                if hasattr(obj, field) and field != 'id':
                    setattr(obj, field, value)
            self._session.commit()
            return obj
        except Exception:
            self._session.rollback()
            raise

    def delete(self, key: int) -> bool:
        obj = self.find_by_id(key)
        if not obj:
            return False
        try:
            self._session.delete(obj)
            self._session.commit()
            return True
        except Exception:
            self._session.rollback()
            raise
