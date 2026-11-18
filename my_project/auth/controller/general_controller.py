from typing import Tuple, Any, Dict

class GeneralController:
    _service = None

    def find_all(self) -> Tuple[Any, int]:
        entities = self._service.find_all()
        return [entity.put_into_dto() for entity in entities], 200

    def find_by_id(self, key: int) -> Tuple[Dict[str, Any], int]:
        entity = self._service.find_by_id(key)
        if not entity:
            return {'message': f'Record with id {key} not found'}, 404
        return entity.put_into_dto(), 200

    def create(self, entity: Any) -> Tuple[Dict[str, Any], int]:
        created_entity = self._service.create(entity)
        return created_entity.put_into_dto(), 201

    def update(self, key: int, update_data: dict) -> Tuple[Dict[str, Any], int]:
        updated_entity = self._service.update(key, update_data)
        if not updated_entity:
            return {'message': f'Record with id {key} not found'}, 404
        return updated_entity.put_into_dto(), 200

    def delete(self, key: int) -> Tuple[Dict[str, Any], int]:
        success = self._service.delete(key)
        if not success:
            return {'message': f'Record with id {key} not found'}, 404
        return {'message': f'Record with id {key} successfully deleted'}, 200
