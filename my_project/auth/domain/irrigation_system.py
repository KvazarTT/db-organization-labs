from my_project import db

class IrrigationSystem(db.Model):
    __tablename__ = 'irrigation_systems'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    system_name = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.Enum('active', 'inactive', 'maintenance', name='irrigation_system_status', native_enum=False),
        nullable=False,
        default='active'
    )

    def put_into_dto(self) -> dict:
        return {
            'id': self.id,
            'client_id': self.client_id,
            'system_name': self.system_name,
            'status': self.status
        }

    @classmethod
    def create_from_dto(cls, dto: dict) -> 'IrrigationSystem':
        return cls(
            client_id=dto.get('client_id'),
            system_name=dto.get('system_name'),
            status=dto.get('status', 'active')
        )
