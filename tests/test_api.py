import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app
from my_project import db

@pytest.fixture
def client():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        with app.test_client() as test_client:
            yield test_client
        db.session.remove()
        db.drop_all()

def test_index_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'online'
    assert 'clients' in data['endpoints']

def test_client_crud(client):
    # 1. Create client (POST)
    new_client = {
        'first_name': 'Олег',
        'last_name': 'Петренко',
        'email': 'oleg.p@example.com',
        'phone': '+380501234567',
        'registration_date': '2026-03-01'
    }
    post_res = client.post('/api/clients', json=new_client)
    assert post_res.status_code == 201
    created = post_res.get_json()
    client_id = created['id']
    assert created['email'] == 'oleg.p@example.com'

    # 2. Get all clients (GET)
    get_all_res = client.get('/api/clients')
    assert get_all_res.status_code == 200
    clients_list = get_all_res.get_json()
    assert len(clients_list) >= 1

    # 3. Get client by id (GET)
    get_res = client.get(f'/api/clients/{client_id}')
    assert get_res.status_code == 200
    assert get_res.get_json()['first_name'] == 'Олег'

    # 4. Update client (PUT)
    update_data = {'first_name': 'Олег-Оновлений', 'phone': '+380509999999'}
    put_res = client.put(f'/api/clients/{client_id}', json=update_data)
    assert put_res.status_code == 200
    assert put_res.get_json()['first_name'] == 'Олег-Оновлений'
    assert put_res.get_json()['phone'] == '+380509999999'

    # 5. Delete client (DELETE)
    del_res = client.delete(f'/api/clients/{client_id}')
    assert del_res.status_code == 200

    # Verify deleted
    get_deleted = client.get(f'/api/clients/{client_id}')
    assert get_deleted.status_code == 404

def test_irrigation_system_crud(client):
    # Setup client first
    cl_res = client.post('/api/clients', json={
        'first_name': 'Іван',
        'last_name': 'Бойко',
        'email': 'ivan.b@example.com',
        'phone': '+380631234567'
    })
    client_id = cl_res.get_json()['id']

    # 1. Create system (POST)
    new_system = {
        'client_id': client_id,
        'system_name': 'Полив Теплиця 1',
        'status': 'active'
    }
    post_res = client.post('/api/irrigation-systems', json=new_system)
    assert post_res.status_code == 201
    created_sys = post_res.get_json()
    sys_id = created_sys['id']
    assert created_sys['system_name'] == 'Полив Теплиця 1'

    # 2. Get all systems (GET)
    get_all_res = client.get('/api/irrigation-systems')
    assert get_all_res.status_code == 200
    systems_list = get_all_res.get_json()
    assert len(systems_list) >= 1

    # 3. Get system by id (GET)
    get_res = client.get(f'/api/irrigation-systems/{sys_id}')
    assert get_res.status_code == 200
    assert get_res.get_json()['system_name'] == 'Полив Теплиця 1'

    # 4. Update system (PUT)
    update_data = {'system_name': 'Полив Теплиця VIP', 'status': 'maintenance'}
    put_res = client.put(f'/api/irrigation-systems/{sys_id}', json=update_data)
    assert put_res.status_code == 200
    assert put_res.get_json()['system_name'] == 'Полив Теплиця VIP'
    assert put_res.get_json()['status'] == 'maintenance'

    # 5. Delete system (DELETE)
    del_res = client.delete(f'/api/irrigation-systems/{sys_id}')
    assert del_res.status_code == 200

    # Verify deleted
    get_del = client.get(f'/api/irrigation-systems/{sys_id}')
    assert get_del.status_code == 404

def test_m_to_1_relationship(client):
    # Create client
    cl_res = client.post('/api/clients', json={
        'first_name': 'Марія',
        'last_name': 'Коваль',
        'email': 'maria.k@example.com'
    })
    client_id = cl_res.get_json()['id']

    # Create two systems for this client
    sys1 = client.post('/api/irrigation-systems', json={
        'client_id': client_id,
        'system_name': 'Система Сад',
        'status': 'active'
    }).get_json()

    sys2 = client.post('/api/irrigation-systems', json={
        'client_id': client_id,
        'system_name': 'Система Газон',
        'status': 'inactive'
    }).get_json()

    # Query M:1 relationship from parent side: GET all systems of client
    rel_res = client.get(f'/api/clients/{client_id}/irrigation-systems')
    assert rel_res.status_code == 200
    systems = rel_res.get_json()
    assert len(systems) == 2
    system_names = [s['system_name'] for s in systems]
    assert 'Система Сад' in system_names
    assert 'Система Газон' in system_names

    # Query relationship from child side: GET client of system
    sys1_id = sys1['id']
    child_rel_res = client.get(f'/api/irrigation-systems/{sys1_id}/client')
    assert child_rel_res.status_code == 200
    parent_client = child_rel_res.get_json()
    assert parent_client['id'] == client_id
    assert parent_client['email'] == 'maria.k@example.com'

def test_validation_and_errors(client):
    # Missing required fields
    bad_res = client.post('/api/clients', json={'first_name': 'No Email'})
    assert bad_res.status_code == 400

    bad_sys_res = client.post('/api/irrigation-systems', json={'system_name': 'No Client'})
    assert bad_sys_res.status_code == 400

    # Non-existent ID
    assert client.get('/api/clients/9999').status_code == 404
    assert client.get('/api/irrigation-systems/9999').status_code == 404
    assert client.delete('/api/clients/9999').status_code == 404
    assert client.delete('/api/irrigation-systems/9999').status_code == 404
