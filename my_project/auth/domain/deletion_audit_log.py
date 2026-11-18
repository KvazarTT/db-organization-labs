from datetime import datetime
from my_project import db


class DeletionAuditLog(db.Model):
    __tablename__ = 'deletion_audit_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_name = db.Column(db.String(64), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    deleted_details = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def put_into_dto(self) -> dict:
        return {
            'id': self.id,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'deleted_details': self.deleted_details,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }
