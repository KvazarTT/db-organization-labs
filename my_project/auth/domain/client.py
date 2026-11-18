from datetime import date, datetime
from my_project import db


class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    registration_date = db.Column(db.Date, nullable=False, default=date.today)

    irrigation_systems = db.relationship(
        'IrrigationSystem',
        backref='client',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def put_into_dto(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None
        }

    @classmethod
    def create_from_dto(cls, dto: dict) -> 'Client':
        raw_date = dto.get('registration_date')
        if isinstance(raw_date, str):
            try:
                reg_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
            except ValueError:
                reg_date = date.today()
        elif isinstance(raw_date, (date, datetime)):
            reg_date = raw_date if isinstance(raw_date, date) else raw_date.date()
        else:
            reg_date = date.today()

        return cls(
            first_name=dto.get('first_name'),
            last_name=dto.get('last_name'),
            email=dto.get('email'),
            phone=dto.get('phone'),
            registration_date=reg_date
        )
