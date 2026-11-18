from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from my_project import db
from my_project.auth.domain.deletion_audit_log import DeletionAuditLog


class StoredProgramDAO:
    """DAO for executing MySQL stored procedures, functions, and reading audit/junction tables."""

    def __init__(self, session=None):
        self._session = session or db.session

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return value

    @classmethod
    def _serialize_rows(cls, rows: Any) -> List[Dict[str, Any]]:
        return [
            {k: cls._serialize_value(v) for k, v in dict(row).items()}
            for row in rows
        ]

    def _call_procedure(self, sql_stmt: str, params: Optional[dict] = None, commit: bool = True) -> List[Dict[str, Any]]:
        try:
            result = self._session.execute(text(sql_stmt), params or {})
            rows = self._serialize_rows(result.mappings().all()) if result.returns_rows else []
            if commit:
                self._session.commit()
            return rows
        except Exception:
            self._session.rollback()
            raise

    def insert_maintenance_log(
        self,
        system_id: int,
        technician_name: str,
        description: str,
        service_cost: float,
        maintenance_date: Optional[str] = None
    ) -> Dict[str, Any]:
        rows = self._call_procedure(
            "CALL sp_insert_maintenance_log(:system_id, :technician_name, :description, :service_cost, :maintenance_date)",
            {
                'system_id': system_id,
                'technician_name': technician_name,
                'description': description,
                'service_cost': service_cost,
                'maintenance_date': maintenance_date
            },
            commit=True
        )
        return rows[0] if rows else {}

    def link_client_irrigation_system(
        self,
        first_name: str,
        last_name: str,
        system_name: str,
        access_role: str = 'operator'
    ) -> Dict[str, Any]:
        rows = self._call_procedure(
            "CALL sp_link_client_irrigation_system(:first_name, :last_name, :system_name, :access_role)",
            {
                'first_name': first_name,
                'last_name': last_name,
                'system_name': system_name,
                'access_role': access_role
            },
            commit=True
        )
        return rows[0] if rows else {}

    def get_client_system_access_list(self) -> List[Dict[str, Any]]:
        result = self._session.execute(
            text(
                "SELECT csa.id, csa.client_id, c.first_name, c.last_name, "
                "csa.system_id, s.system_name, csa.access_role, csa.assigned_at "
                "FROM client_system_access csa "
                "JOIN clients c ON c.id = csa.client_id "
                "JOIN irrigation_systems s ON s.id = csa.system_id "
                "ORDER BY csa.id ASC"
            )
        )
        return self._serialize_rows(result.mappings().all())

    def insert_noname_systems(self, start_num: int = 5) -> List[Dict[str, Any]]:
        return self._call_procedure(
            "CALL sp_insert_noname_systems(:start_num)",
            {'start_num': start_num},
            commit=True
        )

    def get_maintenance_cost_stats(self, stat_type: str = 'AVG') -> Dict[str, Any]:
        rows = self._call_procedure(
            "CALL sp_get_maintenance_cost_stats(:stat_type)",
            {'stat_type': stat_type},
            commit=False
        )
        return rows[0] if rows else {}

    def split_clients_with_cursor(self) -> Dict[str, Any]:
        rows = self._call_procedure("CALL sp_split_clients_with_cursor()", commit=True)
        return rows[0] if rows else {}

    def get_deletion_audit_logs(self) -> List[Dict[str, Any]]:
        logs = self._session.query(DeletionAuditLog).order_by(DeletionAuditLog.id.asc()).all()
        return [log.put_into_dto() for log in logs]
