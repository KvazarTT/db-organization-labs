from datetime import datetime
from my_project import db


class ClientSystemAccess(db.Model):
    __tablename__ = 'client_system_access'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey('irrigation_systems.id', ondelete='CASCADE'), nullable=False)
    access_role = db.Column(db.String(30), nullable=False, default='operator')
    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def put_into_dto(self) -> dict:
        return {
            'id': self.id,
            'client_id': self.client_id,
            'system_id': self.system_id,
            'access_role': self.access_role,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None
        }
