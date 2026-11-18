from pathlib import Path
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="CCCCCC"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="E5E5E5"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def create_report():
    doc = docx.Document()

    for sec in doc.sections:
        sec.top_margin = Cm(2.0)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(2.0)
        sec.right_margin = Cm(2.0)

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
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.0
        pPr = p._p.get_or_add_pPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="F7F7F7"/>')
        pPr.append(shd)
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.0)
        run.font.color.rgb = RGBColor(25, 25, 25)

    def add_styled_table(headers, rows, widths, center_cols=()):
        table = doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_borders(table)

        hdr_cells = table.rows[0].cells
        for i, name in enumerate(headers):
            hdr_cells[i].text = name
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            r = p.runs[0]
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="E0E0E0"/>')
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading)
            set_cell_margins(hdr_cells[i])

        for row_data in rows:
            row = table.add_row()
            for idx, text_val in enumerate(row_data):
                cell = row.cells[idx]
                cell.text = text_val
                p = cell.paragraphs[0]
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                if idx in center_cols:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(10.5)
                set_cell_margins(cell)

        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = width
        return table

    # 1. Title Page
    add_p('МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=2)
    add_p('НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ "ЛЬВІВСЬКА ПОЛІТЕХНІКА"', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=2)
    add_p('Інститут комп’ютерних технологій, автоматики та метрології', WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=2)
    add_p('Кафедра "Комп\'ютеризовані системи автоматики"', WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=18)

    logo_path = Path(r'C:\Users\matvi\.gemini\antigravity\brain\8344d4bf-29db-4ccb-934a-91ed63aac9bb\scratch\lpnu_logo.png')
    if logo_path.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(18)
        p_logo.add_run().add_picture(str(logo_path), width=Cm(4.2))

    add_p('ЗВІТ', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, space_after=6)
    add_p('про виконання лабораторної роботи № 5', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=4)
    add_p(
        '«Збережені програми в MySQL (тригери, процедури, функції, курсори) та інтеграція з Flask Back-End»',
        WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_after=4
    )
    add_p('з навчальної дисципліни: «Організація баз даних та знань»', WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=12, space_after=40)

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_info.paragraph_format.space_after = Pt(48)
    p_info.paragraph_format.line_spacing = 1.15
    r = p_info.add_run('Виконав:\nстудент групи ІР-22\nІвков Матвій\n\nПрийняв:\nАсистент кафедри КСА\nВолос І.В.')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    add_p('Львів — 2026', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=12)
    doc.add_page_break()

    # 2. Assignment Section
    add_p('Завдання до лабораторної роботи', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=10)
    tasks = [
        'На базі попередньої роботи (back-end with Flask, база даних soilsense_db) реалізувати в MySQL програмні конструкції (тригери, процедури, функції, курсори) та забезпечити виклик збережених процедур через контролери бекенду:',
        '1. Додати до БД 1 додаткову таблицю (maintenance_logs) і зв’язати її з існуючою таблицею (irrigation_systems) зв’язком 1:M, використавши тригери для забезпечення цілісності замість фізичного зовнішнього ключа.',
        '2. Збережені процедури та функції:\n'
        '   a. Параметризована вставка нових значень у таблицю maintenance_logs (sp_insert_maintenance_log).\n'
        '   b. Реалізація зв’язку M:M між таблицями clients та irrigation_systems у стикувальну таблицю client_system_access за реально-існуючими значеннями first_name, last_name та system_name (sp_link_client_irrigation_system).\n'
        '   c. Пакетна вставка 10 рядків у форматі <Noname+№> (Noname5, Noname6, ..., Noname14) у таблицю irrigation_systems (sp_insert_noname_systems).\n'
        '   d. Користувацька функція для обчислення MAX, MIN, SUM або AVG стовпця service_cost таблиці maintenance_logs (fn_get_maintenance_cost_stat) та процедура її виклику у SELECT (sp_get_maintenance_cost_stats).\n'
        '   e (варіант i). Процедура з курсором (sp_split_clients_with_cursor), яка динамічно створює 2 таблиці зі штампом часу за структурою clients і випадковим чином пострічково копіює туди дані з таблиці clients.',
        '3. Написати 3 довільні тригери для таблиць поточної БД:\n'
        '   a. Значення стовпця phone у таблиці clients не може закінчуватися двома нулями.\n'
        '   d. Мінімальна кардинальність 6 стрічок для таблиці clients.\n'
        '   f. Таблиця-журнал deletion_audit_log для фіксації логів зі штампом часу при видаленні рядків з irrigation_systems.'
    ]
    for t in tasks:
        add_p(t, WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=5)

    add_p('', space_after=6)

    # 3. Implementation
    add_p('Хід виконання роботи', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=10)

    add_p('1. Розширення бази даних soilsense_db та структура проєкту lab5', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)
    add_p(
        'На основі проєкту lab4 створено нову робочу директорію lab5/. Базу даних soilsense_db розширено трьома таблицями, '
        'опис яких наведено у таблиці 1.',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    add_p('Таблиця 1. Нові таблиці бази даних soilsense_db (Лабораторна робота № 5)', WD_ALIGN_PARAGRAPH.CENTER, bold=True, space_after=4)
    add_styled_table(
        ['Назва таблиці', 'Ключові стовпці', 'Призначення та зв’язки'],
        [
            ('maintenance_logs', 'id, system_id, technician_name, description, service_cost, maintenance_date',
             'Журнал техобслуговування. Зв’язок 1:M з irrigation_systems реалізовано тригерами без фізичного FOREIGN KEY.'),
            ('client_system_access', 'id, client_id, system_id, access_role, assigned_at',
             'Стикувальна таблиця M:M між clients та irrigation_systems із унікальним ключем (client_id, system_id).'),
            ('deletion_audit_log', 'id, table_name, record_id, deleted_details, deleted_at',
             'Таблиця-журнал аудиту видалень із фіксацією штампа часу тригером AFTER DELETE.')
        ],
        [Cm(3.8), Cm(5.5), Cm(7.7)]
    )

    add_p('', space_after=4)
    add_p('Структура створеного проєкту lab5:', WD_ALIGN_PARAGRAPH.LEFT, bold=True, space_after=4)
    struct_text = (
        "lab5/\n"
        "├── config/\n"
        "│   └── app.yml                             # Налаштування підключення до MySQL (soilsense_db)\n"
        "├── my_project/\n"
        "│   ├── auth/\n"
        "│   │   ├── controller/\n"
        "│   │   │   ├── general_controller.py       # Базовий контролер + форматування помилок БД/тригерів\n"
        "│   │   │   ├── client_controller.py\n"
        "│   │   │   ├── irrigation_system_controller.py\n"
        "│   │   │   ├── maintenance_log_controller.py\n"
        "│   │   │   └── stored_program_controller.py # Контролер виклику збережених програм MySQL\n"
        "│   │   ├── dao/\n"
        "│   │   │   ├── general_dao.py              # Загальний CRUD із безпечним rollback при помилках тригерів\n"
        "│   │   │   ├── client_dao.py\n"
        "│   │   │   ├── irrigation_system_dao.py\n"
        "│   │   │   ├── maintenance_log_dao.py\n"
        "│   │   │   └── stored_program_dao.py       # Виконання CALL sp_* через SQLAlchemy text()\n"
        "│   │   ├── domain/\n"
        "│   │   │   ├── client.py\n"
        "│   │   │   ├── irrigation_system.py\n"
        "│   │   │   ├── maintenance_log.py          # ORM-модель без фізичного ForeignKey\n"
        "│   │   │   ├── client_system_access.py     # ORM-модель стикувальної таблиці M:M\n"
        "│   │   │   └── deletion_audit_log.py       # ORM-модель журналу видалень\n"
        "│   │   ├── route/\n"
        "│   │   │   ├── client_route.py\n"
        "│   │   │   ├── irrigation_system_route.py\n"
        "│   │   │   ├── maintenance_log_route.py    # Маршрути /api/maintenance-logs\n"
        "│   │   │   └── stored_program_route.py     # Маршрути /api/stored-programs/*\n"
        "│   │   └── service/\n"
        "│   │       ├── general_service.py\n"
        "│   │       ├── client_service.py\n"
        "│   │       ├── irrigation_system_service.py\n"
        "│   │       ├── maintenance_log_service.py\n"
        "│   │       └── stored_program_service.py\n"
        "│   ├── utils/\n"
        "│   │   ├── config_loader.py\n"
        "│   │   └── db_initializer.py               # Парсер DELIMITER та розгортання data.sql\n"
        "│   └── __init__.py\n"
        "├── tests/\n"
        "│   └── test_api.py                         # 8 інтеграційних тестів PyTest для MySQL\n"
        "├── app.py                                  # Точка входу Flask та перевірка готовності БД\n"
        "├── data.sql                                # DDL, початкові дані, тригери, процедури, функція, курсор\n"
        "├── generate_report.py                      # Скрипт генерації цього звіту\n"
        "├── postman_collection.json                 # Оновлена колекція запитів Postman\n"
        "├── README.md\n"
        "├── requirements.txt\n"
        "└── setup.py"
    )
    add_code_block(struct_text)

    # 4. REST API table
    add_p('2. Реалізовані маршрути REST API (доповнення до Lab 4)', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)
    add_p(
        'Окрім базових маршрутів /api/clients та /api/irrigation-systems із лабораторної роботи № 4, '
        'додано 13 нових кінцевих точок для роботи з maintenance_logs та виклику збережених програм MySQL (таблиця 2).',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    add_p('Таблиця 2. Специфікація нових REST API маршрутів (Лабораторна робота № 5)', WD_ALIGN_PARAGRAPH.CENTER, bold=True, space_after=4)
    add_styled_table(
        ['HTTP Метод', 'Шлях (URL)', 'Призначення / Об’єкт MySQL', 'Код статусу'],
        [
            ('GET', '/api/maintenance-logs', 'Отримання всіх записів техобслуговування', '200 OK'),
            ('GET', '/api/maintenance-logs/<id>', 'Отримання запису обслуговування за ID', '200 OK / 404'),
            ('POST', '/api/maintenance-logs', 'Створення запису (тригерна перевірка system_id)', '201 / 400'),
            ('PUT', '/api/maintenance-logs/<id>', 'Оновлення запису (тригерна перевірка system_id)', '200 / 400 / 404'),
            ('DELETE', '/api/maintenance-logs/<id>', 'Видалення запису техобслуговування', '200 / 404'),
            ('GET', '/api/irrigation-systems/<id>/maintenance-logs', 'Вибірка 1:M усіх логів обслуговування системи', '200 / 404'),
            ('POST', '/api/stored-programs/maintenance-logs', 'П. 2.a: виклик sp_insert_maintenance_log', '201 / 400'),
            ('POST', '/api/stored-programs/client-system-access', 'П. 2.b: виклик sp_link_client_irrigation_system (M:M)', '201 / 400'),
            ('GET', '/api/stored-programs/client-system-access', 'Перегляд стикувальної таблиці client_system_access', '200 OK'),
            ('POST', '/api/stored-programs/noname-systems', 'П. 2.c: виклик sp_insert_noname_systems (10 рядків)', '201 / 400'),
            ('GET', '/api/stored-programs/maintenance-cost-stats?op=...', 'П. 2.d: виклик sp_get_maintenance_cost_stats та UDF', '200 / 400'),
            ('POST', '/api/stored-programs/split-clients-cursor', 'П. 2.e.i: виклик sp_split_clients_with_cursor', '201 / 400'),
            ('GET', '/api/stored-programs/deletion-audit-logs', 'П. 3.f: перегляд журналу видалень deletion_audit_log', '200 OK')
        ],
        [Cm(2.2), Cm(6.7), Cm(5.6), Cm(2.5)],
        center_cols=(0, 3)
    )

    add_p('', space_after=6)

    # 5. SQL and Backend Implementation
    add_p('3. Програмна реалізація тригерів, процедур, функції та курсора', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)

    add_p('3.1. Забезпечення цілісності зв’язку 1:M за допомогою тригерів (Пункт 1)', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_p(
        'Таблиця maintenance_logs не містить фізичного FOREIGN KEY. Цілісність посилань на irrigation_systems(id) '
        'забезпечують чотири тригери: BEFORE INSERT та BEFORE UPDATE на maintenance_logs і BEFORE DELETE / BEFORE UPDATE на irrigation_systems.',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )
    add_code_block(
        "CREATE TRIGGER trg_maintenance_logs_before_insert_fk\n"
        "BEFORE INSERT ON maintenance_logs\n"
        "FOR EACH ROW\n"
        "BEGIN\n"
        "    IF NOT EXISTS (SELECT 1 FROM irrigation_systems WHERE id = NEW.system_id) THEN\n"
        "        SIGNAL SQLSTATE '45000'\n"
        "        SET MESSAGE_TEXT = 'FK Trigger Error: irrigation_systems record with specified system_id does not exist';\n"
        "    END IF;\n"
        "END //\n\n"
        "CREATE TRIGGER trg_irrigation_systems_before_delete_fk\n"
        "BEFORE DELETE ON irrigation_systems\n"
        "FOR EACH ROW\n"
        "BEGIN\n"
        "    IF EXISTS (SELECT 1 FROM maintenance_logs WHERE system_id = OLD.id) THEN\n"
        "        SIGNAL SQLSTATE '45000'\n"
        "        SET MESSAGE_TEXT = 'FK Trigger Error: Cannot delete irrigation_system with existing maintenance_logs';\n"
        "    END IF;\n"
        "END //"
    )

    add_p('3.2. Збережені процедури вставки, зв’язку M:M та пакетного наповнення (Пункти 2.a, 2.b, 2.c)', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "-- 2.b: Реалізація зв'язку M:M у стикувальну таблицю за іменами клієнта та системи\n"
        "CREATE PROCEDURE sp_link_client_irrigation_system(\n"
        "    IN p_first_name VARCHAR(50), IN p_last_name VARCHAR(50),\n"
        "    IN p_system_name VARCHAR(100), IN p_access_role VARCHAR(30)\n"
        ")\n"
        "BEGIN\n"
        "    DECLARE v_client_id INT DEFAULT NULL;\n"
        "    DECLARE v_system_id INT DEFAULT NULL;\n"
        "    SELECT id INTO v_client_id FROM clients WHERE first_name = p_first_name AND last_name = p_last_name LIMIT 1;\n"
        "    IF v_client_id IS NULL THEN\n"
        "        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Client with specified first_name and last_name not found';\n"
        "    END IF;\n"
        "    SELECT id INTO v_system_id FROM irrigation_systems WHERE system_name = p_system_name LIMIT 1;\n"
        "    IF v_system_id IS NULL THEN\n"
        "        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Irrigation system with specified system_name not found';\n"
        "    END IF;\n"
        "    INSERT INTO client_system_access (client_id, system_id, access_role)\n"
        "    VALUES (v_client_id, v_system_id, COALESCE(NULLIF(TRIM(p_access_role), ''), 'operator'))\n"
        "    ON DUPLICATE KEY UPDATE access_role = VALUES(access_role), assigned_at = CURRENT_TIMESTAMP;\n"
        "    SELECT csa.id, csa.client_id, c.first_name, c.last_name, csa.system_id, s.system_name, csa.access_role, csa.assigned_at\n"
        "    FROM client_system_access csa\n"
        "    JOIN clients c ON c.id = csa.client_id JOIN irrigation_systems s ON s.id = csa.system_id\n"
        "    WHERE csa.client_id = v_client_id AND csa.system_id = v_system_id;\n"
        "END //\n\n"
        "-- 2.c: Пакет вставки 10 рядків у форматі <Noname+№>\n"
        "CREATE PROCEDURE sp_insert_noname_systems(IN p_start_num INT)\n"
        "BEGIN\n"
        "    DECLARE v_num INT DEFAULT IF(p_start_num IS NULL OR p_start_num <= 0, 5, p_start_num);\n"
        "    DECLARE v_counter INT DEFAULT 0;\n"
        "    DECLARE v_client_id INT;\n"
        "    DECLARE v_first_id INT DEFAULT 0;\n"
        "    DECLARE v_last_id INT DEFAULT 0;\n"
        "    SELECT MIN(id) INTO v_client_id FROM clients;\n"
        "    WHILE v_counter < 10 DO\n"
        "        INSERT INTO irrigation_systems (client_id, system_name, status)\n"
        "        VALUES (v_client_id, CONCAT('Noname', v_num + v_counter), 'active');\n"
        "        IF v_counter = 0 THEN SET v_first_id = LAST_INSERT_ID(); END IF;\n"
        "        SET v_last_id = LAST_INSERT_ID();\n"
        "        SET v_counter = v_counter + 1;\n"
        "    END WHILE;\n"
        "    SELECT id, client_id, system_name, status FROM irrigation_systems WHERE id BETWEEN v_first_id AND v_last_id;\n"
        "END //"
    )

    add_p('3.3. Користувацька функція агрегації та процедура її виклику у SELECT (Пункт 2.d)', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "CREATE FUNCTION fn_get_maintenance_cost_stat(p_stat_type VARCHAR(10))\n"
        "RETURNS DECIMAL(12,2) DETERMINISTIC READS SQL DATA\n"
        "BEGIN\n"
        "    DECLARE v_result DECIMAL(12,2);\n"
        "    DECLARE v_op VARCHAR(10) DEFAULT UPPER(TRIM(COALESCE(p_stat_type, 'AVG')));\n"
        "    IF v_op = 'MAX' THEN SELECT MAX(service_cost) INTO v_result FROM maintenance_logs;\n"
        "    ELSEIF v_op = 'MIN' THEN SELECT MIN(service_cost) INTO v_result FROM maintenance_logs;\n"
        "    ELSEIF v_op = 'SUM' THEN SELECT SUM(service_cost) INTO v_result FROM maintenance_logs;\n"
        "    ELSEIF v_op = 'AVG' THEN SELECT AVG(service_cost) INTO v_result FROM maintenance_logs;\n"
        "    ELSE SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid stat type. Allowed values: MAX, MIN, SUM, AVG';\n"
        "    END IF;\n"
        "    RETURN COALESCE(v_result, 0.00);\n"
        "END //\n\n"
        "CREATE PROCEDURE sp_get_maintenance_cost_stats(IN p_stat_type VARCHAR(10))\n"
        "BEGIN\n"
        "    SELECT UPPER(TRIM(COALESCE(p_stat_type, 'AVG'))) AS requested_operation,\n"
        "           fn_get_maintenance_cost_stat(p_stat_type) AS requested_value,\n"
        "           fn_get_maintenance_cost_stat('MIN') AS min_cost, fn_get_maintenance_cost_stat('MAX') AS max_cost,\n"
        "           fn_get_maintenance_cost_stat('SUM') AS sum_cost, fn_get_maintenance_cost_stat('AVG') AS avg_cost;\n"
        "END //"
    )

    add_p('3.4. Процедура з курсором для динамічного створення 2-х таблиць зі штампом часу (Пункт 2.e.i)', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "CREATE PROCEDURE sp_split_clients_with_cursor()\n"
        "BEGIN\n"
        "    DECLARE v_done INT DEFAULT 0;\n"
        "    DECLARE v_id INT; DECLARE v_first_name VARCHAR(50); DECLARE v_last_name VARCHAR(50);\n"
        "    DECLARE v_email VARCHAR(100); DECLARE v_phone VARCHAR(20); DECLARE v_reg_date DATE;\n"
        "    DECLARE v_ts VARCHAR(32); DECLARE v_tbl1 VARCHAR(64); DECLARE v_tbl2 VARCHAR(64);\n"
        "    DECLARE v_count1 INT DEFAULT 0; DECLARE v_count2 INT DEFAULT 0;\n"
        "    DECLARE cur_clients CURSOR FOR SELECT id, first_name, last_name, email, phone, registration_date FROM clients ORDER BY id;\n"
        "    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;\n\n"
        "    SET v_ts = CONCAT(DATE_FORMAT(NOW(6), '%Y%m%d_%H%i%s_%f'), '_', LPAD(FLOOR(RAND() * 1000), 3, '0'));\n"
        "    SET v_tbl1 = CONCAT('clients_copy_1_', v_ts); SET v_tbl2 = CONCAT('clients_copy_2_', v_ts);\n"
        "    SET @sql_create1 = CONCAT('CREATE TABLE `', v_tbl1, '` LIKE clients');\n"
        "    PREPARE stmt_c1 FROM @sql_create1; EXECUTE stmt_c1; DEALLOCATE PREPARE stmt_c1;\n"
        "    SET @sql_create2 = CONCAT('CREATE TABLE `', v_tbl2, '` LIKE clients');\n"
        "    PREPARE stmt_c2 FROM @sql_create2; EXECUTE stmt_c2; DEALLOCATE PREPARE stmt_c2;\n"
        "    ...\n"
        "    OPEN cur_clients;\n"
        "    read_loop: LOOP\n"
        "        FETCH cur_clients INTO v_id, v_first_name, v_last_name, v_email, v_phone, v_reg_date;\n"
        "        IF v_done = 1 THEN LEAVE read_loop; END IF;\n"
        "        SET @p_id = v_id; SET @p_first_name = v_first_name; SET @p_last_name = v_last_name;\n"
        "        SET @p_email = v_email; SET @p_phone = v_phone; SET @p_reg_date = v_reg_date;\n"
        "        IF RAND() < 0.5 THEN\n"
        "            EXECUTE stmt_ins1 USING @p_id, @p_first_name, @p_last_name, @p_email, @p_phone, @p_reg_date;\n"
        "            SET v_count1 = v_count1 + 1;\n"
        "        ELSE\n"
        "            EXECUTE stmt_ins2 USING @p_id, @p_first_name, @p_last_name, @p_email, @p_phone, @p_reg_date;\n"
        "            SET v_count2 = v_count2 + 1;\n"
        "        END IF;\n"
        "    END LOOP;\n"
        "    CLOSE cur_clients;\n"
        "    SELECT v_tbl1 AS table_1, v_count1 AS table_1_rows, v_tbl2 AS table_2, v_count2 AS table_2_rows, (v_count1 + v_count2) AS total_copied;\n"
        "END //"
    )

    add_p('3.5. Додаткові тригери цілісності формату, кардинальності та журналювання (Пункт 3)', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "-- 3.a: Заборона закінчення phone двома нулями (BEFORE INSERT та BEFORE UPDATE)\n"
        "IF NEW.phone IS NOT NULL AND RIGHT(TRIM(NEW.phone), 2) = '00' THEN\n"
        "    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Trigger Error (3.a): Client phone number cannot end with 00';\n"
        "END IF;\n\n"
        "-- 3.d: Мінімальна кардинальність 6 стрічок у clients (BEFORE DELETE)\n"
        "SELECT COUNT(*) INTO v_count FROM clients;\n"
        "IF v_count <= 6 THEN\n"
        "    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Trigger Error (3.d): Minimum cardinality of 6 clients must be maintained';\n"
        "END IF;\n\n"
        "-- 3.f: Логування видалень із irrigation_systems зі штампом часу (AFTER DELETE)\n"
        "INSERT INTO deletion_audit_log (table_name, record_id, deleted_details, deleted_at)\n"
        "VALUES ('irrigation_systems', OLD.id, CONCAT('client_id=', OLD.client_id, ', system_name=', OLD.system_name, ', status=', OLD.status), NOW());"
    )

    add_p('3.6. Інтеграція збережених процедур у Flask DAO (my_project/auth/dao/stored_program_dao.py)', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "class StoredProgramDAO:\n"
        "    def _call_procedure(self, sql_stmt: str, params: Optional[dict] = None, commit: bool = True):\n"
        "        try:\n"
        "            result = self._session.execute(text(sql_stmt), params or {})\n"
        "            rows = self._serialize_rows(result.mappings().all()) if result.returns_rows else []\n"
        "            if commit:\n"
        "                self._session.commit()\n"
        "            return rows\n"
        "        except Exception:\n"
        "            self._session.rollback()\n"
        "            raise"
    )

    # 6. Testing & Results
    add_p('4. Результати тестування через PyTest та REST API', WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=13, space_after=6)
    add_p(
        'Усі тригери, збережені процедури, користувацьку функцію та курсор протестовано безпосередньо на живій СКБД MySQL 8.0.46 '
        '(база даних soilsense_db) за допомогою автоматизованого набору тестів PyTest та HTTP-запитів.',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    add_p('4.1. Результат виконання набору тестів pytest:', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "============================= test session starts =============================\n"
        "platform win32 -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0 -- C:\\git\\LLM2.0\\lab4\\.venv\\Scripts\\python.exe\n"
        "cachedir: .pytest_cache\n"
        "rootdir: C:\\git\\LLM2.0\\lab5\n"
        "collecting ... collected 8 items\n\n"
        "tests/test_api.py::test_index_endpoint PASSED                            [ 12%]\n"
        "tests/test_api.py::test_task1_1m_trigger_integrity PASSED                [ 25%]\n"
        "tests/test_api.py::test_task2a_sp_parameterized_insert PASSED            [ 37%]\n"
        "tests/test_api.py::test_task2b_sp_mm_relationship PASSED                 [ 50%]\n"
        "tests/test_api.py::test_task2c_sp_noname_batch PASSED                    [ 62%]\n"
        "tests/test_api.py::test_task2d_udf_and_sp_stats PASSED                   [ 75%]\n"
        "tests/test_api.py::test_task2e_sp_cursor_split_tables PASSED             [ 87%]\n"
        "tests/test_api.py::test_task3_custom_triggers PASSED                     [100%]\n\n"
        "============================= 8 passed in 14.31s =============================="
    )

    add_p('4.2. Приклади реальних HTTP-запитів та відповідей JSON:', WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    add_code_block(
        "1. Запит (2.a — параметризована вставка через sp_insert_maintenance_log):\n"
        "POST /api/stored-programs/maintenance-logs\n"
        "Статус: 201 Created\n"
        "Відповідь: {\"description\": \"Очищення форсунок через процедуру\", \"id\": 7, \"maintenance_date\": \"2026-06-05\", \"service_cost\": 525.0, \"system_id\": 3, \"technician_name\": \"Олена Козак\"}\n\n"
        "2. Запит (2.b — зв'язок M:M за реально-існуючими іменами):\n"
        "POST /api/stored-programs/client-system-access\n"
        "Статус: 201 Created\n"
        "Відповідь: {\"access_role\": \"admin\", \"assigned_at\": \"2026-11-17T19:11:16\", \"client_id\": 4, \"first_name\": \"Анна\", \"id\": 5, \"last_name\": \"Шевченко\", \"system_id\": 1, \"system_name\": \"Полив Теплиця 1\"}\n\n"
        "3. Запит (2.d — виклик користувацької функції fn_get_maintenance_cost_stat через процедуру):\n"
        "GET /api/stored-programs/maintenance-cost-stats?op=MAX\n"
        "Статус: 200 OK\n"
        "Відповідь: {\"avg_cost\": 589.29, \"max_cost\": 1200.0, \"min_cost\": 250.0, \"requested_operation\": \"MAX\", \"requested_value\": 1200.0, \"sum_cost\": 4125.0}\n\n"
        "4. Запит (2.e.i — курсор та динамічні 2 таблиці зі штампом часу):\n"
        "POST /api/stored-programs/split-clients-cursor\n"
        "Статус: 201 Created\n"
        "Відповідь: {\"table_1\": \"clients_copy_1_20261117_191116_654467_229\", \"table_1_rows\": 5, \"table_2\": \"clients_copy_2_20261117_191116_654467_229\", \"table_2_rows\": 5, \"total_copied\": 10}\n\n"
        "5. Перевірка тригерів (П. 1, 3.a, 3.f):\n"
        "POST /api/clients (phone=\"+380671234500\") -> 400: {\"error\": \"Trigger Error (3.a): Client phone number cannot end with 00\"}\n"
        "DELETE /api/irrigation-systems/1 (є логи)  -> 400: {\"error\": \"FK Trigger Error: Cannot delete irrigation_system with existing maintenance_logs\"}\n"
        "DELETE /api/irrigation-systems/11 (без логів) -> 200 + запис у deletion_audit_log із deleted_at"
    )

    # 7. Conclusion
    add_p('Висновок', WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=10)
    add_p(
        'Під час виконання лабораторної роботи № 5 на базі проєкту лабораторної роботи № 4 (Flask + MySQL, база даних soilsense_db) '
        'реалізовано повний комплекс збережених програм у СКБД MySQL 8.0 та їх виклик через контролери бекенду. '
        'Створено таблицю maintenance_logs і забезпечено цілісність зв’язку 1:M із таблицею irrigation_systems виключно тригерами '
        'без використання фізичного зовнішнього ключа. Розроблено збережені процедури для параметризованої вставки '
        '(sp_insert_maintenance_log), зв’язування сутностей M:M за існуючими значеннями (sp_link_client_irrigation_system), '
        'пакетної генерації 10 рядків формату Noname5..Noname14 (sp_insert_noname_systems), агрегуючу функцію '
        'fn_get_maintenance_cost_stat (MAX, MIN, SUM, AVG) із процедурою виклику в SELECT, а також процедуру з курсором '
        'sp_split_clients_with_cursor для динамічного створення двох таблиць зі штампом часу та випадкового копіювання рядків. '
        'Реалізовано 3 додаткові тригери: заборона номерів телефону на «00», мінімальна кардинальність 6 рядків для таблиці clients '
        'та аудит видалень із irrigation_systems у таблицю deletion_audit_log. Працездатність усіх ендпоінтів і конструкцій БД '
        'підтверджено інтеграційним набором тестів PyTest (8 з 8 тестів пройдено успішно) та підготовлено колекцію postman_collection.json.',
        WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    lab5_report = Path(__file__).resolve().parent / 'звіт_лаб5_бд_Івков.docx'
    root_report = Path(__file__).resolve().parent.parent / 'звіт_лаб5_бд_Івков.docx'
    doc.save(str(lab5_report))
    doc.save(str(root_report))
    print(f"Reports saved to:\n - {lab5_report}\n - {root_report}")


if __name__ == '__main__':
    create_report()
