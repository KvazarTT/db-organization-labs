from datetime import date, datetime
from decimal import Decimal
from my_project import db


class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Physical FOREIGN KEY is omitted intentionally; 1:M integrity is enforced by MySQL triggers
    system_id = db.Column(db.Integer, nullable=False)
    technician_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    service_cost = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    maintenance_date = db.Column(db.Date, nullable=False, default=date.today)

    def put_into_dto(self) -> dict:
        return {
            'id': self.id,
            'system_id': self.system_id,
            'technician_name': self.technician_name,
            'description': self.description,
            'service_cost': float(self.service_cost) if self.service_cost is not None else 0.0,
            'maintenance_date': self.maintenance_date.isoformat() if self.maintenance_date else None
        }

    @classmethod
    def create_from_dto(cls, dto: dict) -> 'MaintenanceLog':
        raw_date = dto.get('maintenance_date')
        if isinstance(raw_date, str):
            try:
                m_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
            except ValueError:
                m_date = date.today()
        elif isinstance(raw_date, (date, datetime)):
            m_date = raw_date if isinstance(raw_date, date) else raw_date.date()
        else:
            m_date = date.today()

        cost = dto.get('service_cost', 0.00)
        return cls(
            system_id=dto.get('system_id'),
            technician_name=dto.get('technician_name'),
            description=dto.get('description'),
            service_cost=Decimal(str(cost)) if cost is not None else Decimal('0.00'),
            maintenance_date=m_date
        )
