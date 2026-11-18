import sys
from pathlib import Path
import pytest
import pymysql

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app
from my_project import db
from my_project.utils import load_config, execute_sql_file


@pytest.fixture(scope='session', autouse=True)
def restore_clean_db_after_suite():
    yield
    cfg = load_config()
    execute_sql_file(cfg)


@pytest.fixture
def client():
    cfg = load_config()
    execute_sql_file(cfg)

    app = create_app({'TESTING': True})
    with app.app_context():
        with app.test_client() as test_client:
            yield test_client
        db.session.remove()
        db.engine.dispose()


def test_index_endpoint(client):
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'online'
    assert 'maintenance_logs' in data['tables']
    assert 'sp_split_clients_cursor' in data['endpoints']


def test_task1_1m_trigger_integrity(client):
    # Verify maintenance_logs has NO physical FOREIGN KEY in information_schema
    cfg = load_config()
    conn = pymysql.connect(
        host=cfg['DB_HOST'], port=cfg['DB_PORT'],
        user=cfg['DB_USER'], password=cfg['DB_PASSWORD'], database=cfg['DB_NAME']
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'maintenance_logs' "
                "AND REFERENCED_TABLE_NAME IS NOT NULL",
                (cfg['DB_NAME'],)
            )
            assert cur.fetchone()[0] == 0
    finally:
        conn.close()

    # Valid GET by 1:M relationship (irrigation_system -> maintenance_logs)
    sys_logs_res = client.get('/api/irrigation-systems/1/maintenance-logs')
    assert sys_logs_res.status_code == 200
    assert len(sys_logs_res.get_json()) == 2

    # Valid POST into maintenance_logs
    create_res = client.post('/api/maintenance-logs', json={
        'system_id': 2,
        'technician_name': 'Петро Іваненко',
        'description': 'Перевірка датчика тиску',
        'service_cost': 190.50,
        'maintenance_date': '2026-06-01'
    })
    assert create_res.status_code == 201
    log_id = create_res.get_json()['id']

    # Invalid INSERT blocked by BEFORE INSERT trigger
    bad_insert = client.post('/api/maintenance-logs', json={
        'system_id': 9999,
        'technician_name': 'Тест',
        'description': 'Неіснуюча система',
        'service_cost': 100.00
    })
    assert bad_insert.status_code == 400
    assert 'FK Trigger Error' in bad_insert.get_json()['error']

    # Invalid UPDATE blocked by BEFORE UPDATE trigger
    bad_update = client.put(f'/api/maintenance-logs/{log_id}', json={'system_id': 9999})
    assert bad_update.status_code == 400
    assert 'FK Trigger Error' in bad_update.get_json()['error']

    # Deleting parent irrigation_system with child maintenance_logs blocked by BEFORE DELETE trigger
    bad_delete = client.delete('/api/irrigation-systems/1')
    assert bad_delete.status_code == 400
    assert 'FK Trigger Error' in bad_delete.get_json()['error']

    # Valid PUT and DELETE cleanup
    ok_update = client.put(f'/api/maintenance-logs/{log_id}', json={'service_cost': 210.00})
    assert ok_update.status_code == 200
    assert ok_update.get_json()['service_cost'] == 210.0
    assert client.delete(f'/api/maintenance-logs/{log_id}').status_code == 200


def test_task2a_sp_parameterized_insert(client):
    res = client.post('/api/stored-programs/maintenance-logs', json={
        'system_id': 3,
        'technician_name': 'Олена Козак',
        'description': 'Очищення форсунок через процедуру',
        'service_cost': 525.00,
        'maintenance_date': '2026-06-05'
    })
    assert res.status_code == 201
    created = res.get_json()
    assert created['system_id'] == 3
    assert created['service_cost'] == 525.0

    # Verify persisted
    get_res = client.get(f"/api/maintenance-logs/{created['id']}")
    assert get_res.status_code == 200
    assert get_res.get_json()['description'] == 'Очищення форсунок через процедуру'

    # Trigger still rejects invalid system_id via stored procedure
    bad_res = client.post('/api/stored-programs/maintenance-logs', json={
        'system_id': 9999,
        'technician_name': 'Тест',
        'description': 'Помилка FK тригера',
        'service_cost': 50.00
    })
    assert bad_res.status_code == 400
    assert 'FK Trigger Error' in bad_res.get_json()['error']


def test_task2b_sp_mm_relationship(client):
    res = client.post('/api/stored-programs/client-system-access', json={
        'first_name': 'Анна',
        'last_name': 'Шевченко',
        'system_name': 'Полив Теплиця 1',
        'access_role': 'admin'
    })
    assert res.status_code == 201
    linked = res.get_json()
    assert linked['first_name'] == 'Анна'
    assert linked['last_name'] == 'Шевченко'
    assert linked['system_name'] == 'Полив Теплиця 1'
    assert linked['access_role'] == 'admin'

    # Verify M:M list endpoint
    list_res = client.get('/api/stored-programs/client-system-access')
    assert list_res.status_code == 200
    assert any(
        row['client_id'] == linked['client_id'] and row['system_id'] == linked['system_id']
        for row in list_res.get_json()
    )

    # Non-existent client or system fails cleanly
    missing_res = client.post('/api/stored-programs/client-system-access', json={
        'first_name': 'Невідомий',
        'last_name': 'Клієнт',
        'system_name': 'Полив Теплиця 1'
    })
    assert missing_res.status_code == 400


def test_task2c_sp_noname_batch(client):
    res = client.post('/api/stored-programs/noname-systems', json={'start_num': 5})
    assert res.status_code == 201
    payload = res.get_json()
    assert payload['inserted_count'] == 10
    names = [r['system_name'] for r in payload['records']]
    assert names == [f'Noname{i}' for i in range(5, 15)]


def test_task2d_udf_and_sp_stats(client):
    for op, expected in [('MAX', 1200.0), ('MIN', 250.0), ('SUM', 3600.0), ('AVG', 600.0)]:
        res = client.get(f'/api/stored-programs/maintenance-cost-stats?op={op}')
        assert res.status_code == 200
        data = res.get_json()
        assert data['requested_operation'] == op
        assert data['requested_value'] == expected
        assert data['min_cost'] == 250.0
        assert data['max_cost'] == 1200.0
        assert data['sum_cost'] == 3600.0
        assert data['avg_cost'] == 600.0

    bad_res = client.get('/api/stored-programs/maintenance-cost-stats?op=MEDIAN')
    assert bad_res.status_code == 400


def test_task2e_sp_cursor_split_tables(client):
    res1 = client.post('/api/stored-programs/split-clients-cursor')
    assert res1.status_code == 201
    d1 = res1.get_json()
    assert d1['table_1'].startswith('clients_copy_1_')
    assert d1['table_2'].startswith('clients_copy_2_')
    assert d1['table_1_rows'] + d1['table_2_rows'] == 10
    assert d1['total_copied'] == 10

    res2 = client.post('/api/stored-programs/split-clients-cursor')
    assert res2.status_code == 201
    d2 = res2.get_json()
    assert d2['table_1'] != d1['table_1']
    assert d2['table_2'] != d1['table_2']
    assert d2['table_1_rows'] + d2['table_2_rows'] == 10

    cfg = load_config()
    conn = pymysql.connect(
        host=cfg['DB_HOST'], port=cfg['DB_PORT'],
        user=cfg['DB_USER'], password=cfg['DB_PASSWORD'],
        database=cfg['DB_NAME'], autocommit=True
    )
    try:
        with conn.cursor() as cur:
            for tbl, expected_cnt in [
                (d1['table_1'], d1['table_1_rows']),
                (d1['table_2'], d1['table_2_rows']),
                (d2['table_1'], d2['table_1_rows']),
                (d2['table_2'], d2['table_2_rows'])
            ]:
                cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
                assert cur.fetchone()[0] == expected_cnt
                cur.execute(f"DROP TABLE IF EXISTS `{tbl}`")
    finally:
        conn.close()


def test_task3_custom_triggers(client):
    # 3.a: phone cannot end with '00' on INSERT or UPDATE
    bad_phone_insert = client.post('/api/clients', json={
        'first_name': 'Тест',
        'last_name': 'Нулі',
        'email': 'zero.test@example.com',
        'phone': '+380671234500'
    })
    assert bad_phone_insert.status_code == 400
    assert '00' in bad_phone_insert.get_json()['error']

    ok_insert = client.post('/api/clients', json={
        'first_name': 'Тарас',
        'last_name': 'Сидоренко',
        'email': 'taras.s@example.com',
        'phone': '+380671234501'
    })
    assert ok_insert.status_code == 201
    new_client_id = ok_insert.get_json()['id']

    bad_phone_update = client.put(f'/api/clients/{new_client_id}', json={'phone': '+380671234500'})
    assert bad_phone_update.status_code == 400
    assert '00' in bad_phone_update.get_json()['error']

    # 3.f: AFTER DELETE on irrigation_systems writes timestamped record to deletion_audit_log
    del_sys_res = client.delete('/api/irrigation-systems/11')
    assert del_sys_res.status_code == 200

    audit_res = client.get('/api/stored-programs/deletion-audit-logs')
    assert audit_res.status_code == 200
    audit_logs = audit_res.get_json()
    assert len(audit_logs) == 1
    assert audit_logs[0]['table_name'] == 'irrigation_systems'
    assert audit_logs[0]['record_id'] == 11
    assert audit_logs[0]['deleted_at'] is not None

    # 3.d: minimum cardinality of 6 clients on DELETE (11 clients -> delete 5 -> 6 left -> 6th delete blocked)
    for cid in [new_client_id, 10, 9, 8, 7]:
        assert client.delete(f'/api/clients/{cid}').status_code == 200

    blocked_del = client.delete('/api/clients/6')
    assert blocked_del.status_code == 400
    assert 'Minimum cardinality of 6 clients' in blocked_del.get_json()['error']
