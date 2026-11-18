import os
from pathlib import Path
import docx
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_report():
    doc = docx.Document()
    
    # Page setup
    for sec in doc.sections:
        sec.top_margin = Cm(2.0)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(2.0)
        sec.right_margin = Cm(2.0)

    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    def add_p(text, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, italic=False, size=12, space_after=4):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        return p

    def add_code_block(code_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(30, 30, 30)

    # 1. Header / Title Page
    add_p('МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=2)
    add_p('НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ "ЛЬВІВСЬКА ПОЛІТЕХНІКА"', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=2)
    add_p('Інститут комп’ютерних технологій, автоматики та метрології', WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=2)
    add_p('Кафедра "Комп\'ютеризовані системи автоматики"', WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=24)

    add_p('ЗВІТ', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, space_after=6)
    add_p('про виконання лабораторної роботи № 4', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=4)
    add_p('«Реалізація Back-End проекту з використанням Flask+Python та підключенням до MySQL»', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_after=4)
    add_p('з навчальної дисципліни: «Організація баз даних та знань»', WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=12, space_after=40)

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_info.paragraph_format.space_after = Pt(50)
    p_info.paragraph_format.line_spacing = 1.15
    r = p_info.add_run('Виконав:\nстудент групи ІР-22\nІвков Матвій\n\nПрийняв:\nАсистент кафедри КСА\nВолос І.В.')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    add_p('Львів — 2026', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=18)
    doc.add_page_break()

    # 2. Assignment Section
    add_p('Завдання до лабораторної роботи', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=10)
    
    tasks = [
        '1. Для спроектованої в лабораторній роботі № 3 бази даних soilsense_db реалізувати Back-End проект із використанням мікрофреймворка Flask (Python) та підключенням до СКБД MySQL.',
        '2. Забезпечити чітку багатошарову архітектуру проекту (Layered Architecture): конфігурація (config/app.yml), контролери (controller), доступ до даних (dao), моделі/сутності (domain), маршрути (route), сервіси бізнес-логіки (service), модульні тести (tests), головний файл запуску (app.py), SQL-скрипт (data.sql) та перелік залежностей (requirements.txt).',
        '3. Web-контролери повинні опрацьовувати вхідні HTTP-запити для виконання повного циклу CRUD-операцій (Create, Read, Update, Delete) та повертати серіалізовані дані у форматі DTO-об’єктів (Data Transfer Object).',
        '4. Сервісний рівень (Service Layer) повинен містити основну бізнес-логіку взаємодії та делегування операцій до рівня доступу до даних.',
        '5. Рівень DAO (Data Access Object) повинен інкапсулювати методи виконання запитів до бази даних за допомогою ORM SQLAlchemy.',
        '6. Клієнтську роботу розробленого REST API протестувати за допомогою інструменту Postman:\n   • отримання вибірки даних із таблиць (GET);\n   • вставка нових записів (POST);\n   • оновлення наявних даних (PUT);\n   • видалення даних за ідентифікатором (DELETE);\n   • вибірка пов’язаних даних зі сторони зв’язку M:1 (для клієнта отримати всі призначені йому системи автополиву, а для системи — отримати дані її власника).',
        '7. Підготувати проект до розгортання та завантаження у репозиторій GitHub.'
    ]
    for t in tasks:
        add_p(t, WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=5)

    add_p('', space_after=10)

    # 3. Architecture & Entities
    add_p('Хід виконання роботи', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=10)

    add_p('1. Вибір сутностей бази даних та структура проекту', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)
    add_p(
        'Для реалізації бекенд-частини відповідно до узгодження з викладачем було обрано дві ключові пов’язані сутності бази даних soilsense_db: '
        'таблицю клієнтів (clients) та таблицю систем автополиву (irrigation_systems). '
        'Між даними сутностями реалізовано зв’язок 1:M (один клієнт може мати декілька систем поливу; '
        'зі сторони систем автополиву — це зв’язок M:1 із зовнішнім ключем client_id, який посилається на clients.id із каскадним видаленням ON DELETE CASCADE).',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    add_p('Структура створеного проекту lab4:', WD_ALIGN_PARAGRAPH.LEFT, bold=True, space_after=4)
    struct_text = (
        "lab4/\n"
        "├── config/\n"
        "│   └── app.yml                     # Параметри з'єднання з MySQL та налаштування хоста\n"
        "├── my_project/\n"
        "│   ├── auth/\n"
        "│   │   ├── controller/             # Web-контролери для DTO-обміну\n"
        "│   │   │   ├── general_controller.py\n"
        "│   │   │   ├── client_controller.py\n"
        "│   │   │   └── irrigation_system_controller.py\n"
        "│   │   ├── dao/                    # DAO для виконання запитів через SQLAlchemy ORM\n"
        "│   │   │   ├── general_dao.py\n"
        "│   │   │   ├── client_dao.py\n"
        "│   │   │   └── irrigation_system_dao.py\n"
        "│   │   ├── domain/                 # ORM-моделі та методи put_into_dto / create_from_dto\n"
        "│   │   │   ├── client.py\n"
        "│   │   │   └── irrigation_system.py\n"
        "│   │   ├── route/                  # Flask Blueprints маршрутів REST API\n"
        "│   │   │   ├── client_route.py\n"
        "│   │   │   └── irrigation_system_route.py\n"
        "│   │   └── service/                # Сервіси бізнес-логіки\n"
        "│   │       ├── general_service.py\n"
        "│   │       ├── client_service.py\n"
        "│   │       └── irrigation_system_service.py\n"
        "│   ├── ui/                         # Допоміжний пакет представлення\n"
        "│   ├── utils/                      # Модуль завантаження конфігурації (config_loader.py)\n"
        "│   └── __init__.py                 # Спільний екземпляр SQLAlchemy db\n"
        "├── tests/\n"
        "│   └── test_api.py                 # 5 комплексних тестів для PyTest (CRUD + M:1 зв'язок)\n"
        "├── app.py                          # Точка входу додатку, фабрика create_app()\n"
        "├── data.sql                        # Сценарій створення та наповнення БД soilsense_db\n"
        "├── postman_collection.json         # Колекція 12 запитів для тестування у Postman\n"
        "├── requirements.txt                # Залежності проекту\n"
        "└── setup.py                        # Метадані пакета\n"
    )
    add_code_block(struct_text)

    # 4. Endpoints Table
    add_p('2. Реалізовані маршрути REST API', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)
    add_p('Нижче у таблиці 1 наведено перелік усіх розроблених кінцевих точок (endpoints) із відповідними методами, адресами та їх функціональним призначенням.', WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_p('Таблиця 1. Специфікація REST API маршрутів', WD_ALIGN_PARAGRAPH.CENTER, bold=True, space_after=4)

    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    hdr_cells = table.rows[0].cells
    headers = ['HTTP Метод', 'Шлях (URL)', 'Опис операції', 'Код статусу']
    widths = [Cm(2.6), Cm(6.5), Cm(5.5), Cm(2.4)]
    for i, name in enumerate(headers):
        hdr_cells[i].text = name
        hdr_cells[i].paragraphs[0].runs[0].bold = True
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shading = parse_xml(r'<w:shd {} w:fill="E0E0E0"/>'.format(nsdecls('w')))
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)

    api_rows = [
        ('GET', '/api/clients', 'Отримання списку всіх клієнтів', '200 OK'),
        ('GET', '/api/clients/<id>', 'Отримання інформації про клієнта за ID', '200 OK / 404'),
        ('POST', '/api/clients', 'Створення нового запису клієнта', '201 Created / 400'),
        ('PUT', '/api/clients/<id>', 'Оновлення існуючого клієнта', '200 OK / 404'),
        ('DELETE', '/api/clients/<id>', 'Видалення клієнта (каскадне видалення систем)', '200 OK / 404'),
        ('GET', '/api/clients/<id>/irrigation-systems', 'Вибірка M:1: усі системи поливу вказаного клієнта', '200 OK / 404'),
        ('GET', '/api/irrigation-systems', 'Отримання всіх систем автополиву', '200 OK'),
        ('GET', '/api/irrigation-systems/<id>', 'Отримання системи поливу за ID', '200 OK / 404'),
        ('POST', '/api/irrigation-systems', 'Створення нової системи автополиву', '201 Created / 400'),
        ('PUT', '/api/irrigation-systems/<id>', 'Оновлення параметрів системи автополиву', '200 OK / 404'),
        ('DELETE', '/api/irrigation-systems/<id>', 'Видалення системи автополиву за ID', '200 OK / 404'),
        ('GET', '/api/irrigation-systems/<id>/client', 'Вибірка M:1: отримання даних клієнта-власника системи', '200 OK / 404')
    ]

    for row_data in api_rows:
        row = table.add_row()
        for idx, text in enumerate(row_data):
            cell = row.cells[idx]
            cell.text = text
            cell.paragraphs[0].paragraph_format.line_spacing = 1.0
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)
            cell.paragraphs[0].paragraph_format.space_before = Pt(2)
            if idx in (0, 3):
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width

    add_p('', space_after=10)

    # 5. Code & Implementation details
    add_p('3. Програмна реалізація ключових модулів', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)
    
    add_p('3.1. Доменна модель Client (my_project/auth/domain/client.py):', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "class Client(db.Model):\n"
        "    __tablename__ = 'clients'\n"
        "    id = db.Column(db.Integer, primary_key=True, autoincrement=True)\n"
        "    first_name = db.Column(db.String(50), nullable=False)\n"
        "    last_name = db.Column(db.String(50), nullable=False)\n"
        "    email = db.Column(db.String(100), unique=True, nullable=False)\n"
        "    phone = db.Column(db.String(20), nullable=True)\n"
        "    registration_date = db.Column(db.Date, nullable=False, default=date.today)\n"
        "    irrigation_systems = db.relationship('IrrigationSystem', backref='client', lazy=True, cascade='all, delete-orphan')\n"
        "\n"
        "    def put_into_dto(self) -> dict:\n"
        "        return {\n"
        "            'id': self.id, 'first_name': self.first_name, 'last_name': self.last_name,\n"
        "            'email': self.email, 'phone': self.phone,\n"
        "            'registration_date': self.registration_date.isoformat() if self.registration_date else None\n"
        "        }\n"
    )

    add_p('3.2. Рівень доступу до даних GeneralDAO (my_project/auth/dao/general_dao.py):', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "class GeneralDAO:\n"
        "    _model = None\n"
        "    def __init__(self, session=None):\n"
        "        self._session = session or db.session\n"
        "    def find_all(self):\n"
        "        return self._session.query(self._model).all()\n"
        "    def find_by_id(self, key: int):\n"
        "        return self._session.get(self._model, key)\n"
        "    def create(self, obj):\n"
        "        self._session.add(obj)\n"
        "        self._session.commit()\n"
        "        return obj\n"
        "    def update(self, key: int, update_data: dict):\n"
        "        obj = self.find_by_id(key)\n"
        "        if not obj: return None\n"
        "        for field, value in update_data.items():\n"
        "            if hasattr(obj, field) and field != 'id': setattr(obj, field, value)\n"
        "        self._session.commit()\n"
        "        return obj\n"
        "    def delete(self, key: int) -> bool:\n"
        "        obj = self.find_by_id(key)\n"
        "        if not obj: return False\n"
        "        self._session.delete(obj)\n"
        "        self._session.commit()\n"
        "        return True\n"
    )

    add_p('3.3. Реалізація вибірки за зв’язком M:1 (my_project/auth/controller/client_controller.py):', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "class ClientController(GeneralController):\n"
        "    def __init__(self):\n"
        "        self._service = ClientService()\n"
        "\n"
        "    def get_irrigation_systems(self, client_id: int):\n"
        "        client = self._service.find_by_id(client_id)\n"
        "        if not client:\n"
        "            return {'message': f'Client with id {client_id} not found'}, 404\n"
        "        systems = self._service.get_irrigation_systems_by_client_id(client_id)\n"
        "        return [system.put_into_dto() for system in systems], 200\n"
    )

    # 6. Testing & Results
    add_p('4. Результати тестування через Postman та PyTest', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)
    add_p(
        'Працездатність розробленого Back-End проекту перевірено за двома напрямками: автоматизованим набором юніт-тестів та інтерактивним тестуванням через Postman.',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    add_p('4.1. Результати запуску автоматизованого набору тестів (pytest):', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    test_run_output = (
        "============================= test session starts =============================\n"
        "platform win32 -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0\n"
        "rootdir: C:\\git\\LLM2.0\\lab4\n"
        "collected 5 items\n\n"
        "lab4/tests/test_api.py::test_index_endpoint PASSED                       [ 20%]\n"
        "lab4/tests/test_api.py::test_client_crud PASSED                          [ 40%]\n"
        "lab4/tests/test_api.py::test_irrigation_system_crud PASSED               [ 60%]\n"
        "lab4/tests/test_api.py::test_m_to_1_relationship PASSED                  [ 80%]\n"
        "lab4/tests/test_api.py::test_validation_and_errors PASSED                [100%]\n\n"
        "============================== 5 passed in 1.07s ==============================\n"
    )
    add_code_block(test_run_output)

    add_p('4.2. Приклади HTTP-запитів та відповідей у Postman:', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    postman_examples = (
        "1. Запит: GET http://127.0.0.1:5000/api/clients/1\n"
        "Статус: 200 OK\n"
        "Тіло відповіді (JSON DTO):\n"
        "{\n"
        '  "id": 1,\n'
        '  "first_name": "Олег",\n'
        '  "last_name": "Петренко",\n'
        '  "email": "oleg.p@example.com",\n'
        '  "phone": "+380501234567",\n'
        '  "registration_date": "2025-05-10"\n'
        "}\n\n"
        "2. Запит: GET http://127.0.0.1:5000/api/clients/1/irrigation-systems (M:1 зв'язок)\n"
        "Статус: 200 OK\n"
        "Тіло відповіді (JSON DTO):\n"
        "[\n"
        "  {\n"
        '    "id": 1,\n'
        '    "client_id": 1,\n'
        '    "system_name": "Полив Теплиця 1",\n'
        '    "status": "active"\n'
        "  },\n"
        "  {\n"
        '    "id": 2,\n'
        '    "client_id": 1,\n'
        '    "system_name": "Полив Відкритий Ґрунт",\n'
        '    "status": "active"\n'
        "  }\n"
        "]\n\n"
        "3. Запит: POST http://127.0.0.1:5000/api/clients\n"
        "Тіло запиту: {\"first_name\": \"Микола\", \"last_name\": \"Гриценко\", \"email\": \"mykola.g@example.com\", \"phone\": \"+380671112233\"}\n"
        "Статус: 201 Created\n"
        "Відповідь: {\"id\": 11, \"first_name\": \"Микола\", \"last_name\": \"Гриценко\", \"email\": \"mykola.g@example.com\", \"phone\": \"+380671112233\", \"registration_date\": \"2026-11-09\"}\n\n"
        "4. Запит: PUT http://127.0.0.1:5000/api/clients/11\n"
        "Тіло запиту: {\"phone\": \"+380679998877\"}\n"
        "Статус: 200 OK\n"
        "Відповідь: {\"id\": 11, \"phone\": \"+380679998877\", ...}\n\n"
        "5. Запит: DELETE http://127.0.0.1:5000/api/clients/11\n"
        "Статус: 200 OK\n"
        "Відповідь: {\"message\": \"Record with id 11 successfully deleted\"}\n"
    )
    add_code_block(postman_examples)

    # 7. Conclusion
    add_p('Висновок', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=10)
    add_p(
        'Під час виконання лабораторної роботи № 4 я успішно реалізував Back-End проект на мові програмування Python з використанням фреймворка Flask та інтеграцією із реляційною СКБД MySQL (база даних soilsense_db). '
        'Для взаємодії з базою даних розгорнуто архітектуру згідно зі світовими стандартами розробки програмного забезпечення на основі N-рівневої архітектури (Layered Architecture): '
        'рівень доменних сутностей (Domain Model) із DTO-серіалізацією (put_into_dto, create_from_dto), '
        'рівень доступу до даних (DAO) із базовим класом GeneralDAO для уникнення дублювання CRUD-коду, '
        'сервісний рівень (Service) для ізоляції бізнес-правил та контролери (Web Controller) із Flask Blueprints маршрутизацією. '
        'Для двох пов’язаних сутностей clients та irrigation_systems реалізовано повний набір операцій CRUD, '
        'а також спеціалізовані методи для отримання даних за зв’язком M:1 (вибірка систем поливу конкретного клієнта та вибірка клієнта для конкретної системи). '
        'Конфігурацію бази даних винесено у зовнішній файл config/app.yml із підтримкою динамічного перевизначення через змінні середовища. '
        'Працездатність розробленого REST API повністю перевірено та підтверджено автоматизованими тестами pytest (5 з 5 пройдено успішно) '
        'і тестовими сценаріями в Postman, експортованими у готову колекцію postman_collection.json.',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    output_path = Path(__file__).resolve().parent / 'звіт_лаб4_бд_Івков.docx'
    doc.save(str(output_path))
    print(f"Report saved to: {output_path}")

if __name__ == '__main__':
    create_report()
