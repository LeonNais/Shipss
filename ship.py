import psycopg2

# Подключаемся к базе данных
conn = psycopg2.connect(dbname="shipping", user="postgres", password="6")


# Функция для добавления или обновления судна
def add_or_update_ship(ship_id, ship_name, construction_year, flag, ship_type):
    cur = conn.cursor()
    if len(str(ship_id)) != 9:
        print("Некорректный идентификатор судна")
        return
    # Проверяем, существует ли судно в базе данных
    cur.execute("SELECT COUNT(*) FROM ship WHERE ship_id = %s", (ship_id,))
    count = cur.fetchone()[0]

    if count == 0:
        # Если судно не существует, добавляем новое
        cur.execute(
            "INSERT INTO ship (ship_id, ship_name, construction_year, flag, ship_type) VALUES (%s, %s, %s, %s, %s)",
            (ship_id, ship_name, construction_year, flag, ship_type))
        conn.commit()
        print("Судно успешно добавлено")
    else:
        # Если судно существует и один из параметров совпадает с имеющимся, выдаем ошибку и не добавляем/не обновляем
        cur.execute("SELECT ship_name, construction_year, flag, ship_type FROM ship WHERE ship_id = %s", (ship_id,))
        existing_ship = cur.fetchone()
        if existing_ship[0] == ship_name or existing_ship[1] == construction_year or existing_ship[2] == flag or \
                existing_ship[3] == ship_type:
            print("Такое судно уже существует в базе данных")
        else:
            # Если судно существует и никакой параметр не совпадает, обновляем данные
            cur.execute(
                "UPDATE ship SET ship_name = %s, construction_year = %s, flag = %s, ship_type = %s WHERE ship_id = %s",
                (ship_name, construction_year, flag, ship_type, ship_id))


# Функция для удаления судна, если оно не пришвартовано
# noinspection SqlResolve
def delete_ship(ship_id):
    cur = conn.cursor()
    # Проверяем, пришвартовано ли судно на каком-либо причале
    cur.execute("SELECT COUNT(*) FROM dock_ship WHERE ship_id = %s", (ship_id,))
    count = cur.fetchone()[0]
    if count == 0:
        # Если судно не пришвартовано, удаляем его из базы данных
        cur.execute("DELETE FROM ship WHERE ship_id = %s", (ship_id,))
        conn.commit()
        print("Судно успешно удалено")
    else:
        # Если судно пришвартовано, выводим ошибку
        print("Невозможно удалить пришвартованное судно")


# Функция для добавления причала
# noinspection SqlResolve
def add_dock(dock_id, dock_name, latitude, longitude, max_ships):
    cur = conn.cursor()
    # Проверка на наличие записи с данным dock_id*
    cur.execute("SELECT * FROM dock WHERE dock_id = %s", (dock_id,))
    if cur.fetchone():
        print(f"Причал с id {dock_id} уже существует")
        cur.close()
        return  # прерывание выполнения функции, если запись существует
    else:
        cur.execute("INSERT INTO dock (dock_id, dock_name, latitude, longitude, max_ships) VALUES (%s, %s, %s, %s, %s)",
                    (dock_id, dock_name, latitude, longitude, max_ships))
        conn.commit()
        print("Причал успешно добавлен")
    cur.close()


# Функция для удаления причала
# noinspection SqlResolve
def delete_dock(dock_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM dock WHERE dock_id = %s", (dock_id,))
    conn.commit()
    print("Причал успешно удален")


# Функция для пришвартовки судна на причал
# noinspection SqlResolve
def dock_ship(ship_id, dock_id):
    cur = conn.cursor()
    # Проверяем, есть ли место на причале
    cur.execute("SELECT COUNT(*) FROM dock_ship WHERE dock_id = %s", (dock_id,))
    count = cur.fetchone()[0]
    cur.execute("SELECT max_ships FROM dock WHERE dock_id = %s", (dock_id,))
    max_ships = cur.fetchone()[0]
    if count < max_ships:
        # Если место есть, пришвартовываем судно на причале
        cur.execute("INSERT INTO dock_ship (dock_id, ship_id) VALUES (%s, %s)", (dock_id, ship_id))
        conn.commit()
        print("Судно успешно пришвартовано на причале")
    else:
        # Если места нет, выводим ошибку
        print("Невозможно пришвартовать судно. Нет свободных мест на причале")


# Функция для отшвартовки судна с причала
# noinspection SqlResolve
def undock_ship(ship_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM dock_ship WHERE ship_id = %s", (ship_id,))
    conn.commit()
    print("Судно успешно отшвартовано")


# Функция для вывода списка свободных причалов
# noinspection SqlResolve
def get_free_docks():
    cur = conn.cursor()
    cur.execute(
        "SELECT dock_id FROM dock WHERE max_ships > (SELECT COUNT(*) FROM dock_ship WHERE dock_id = dock.dock_id)")
    docks = cur.fetchall()
    print("Список свободных причалов:")
    for dock in docks:
        print(dock[0])


# Основной цикл программы
while True:
    # Выводим меню для выбора действия
    print("Выберите действие:")
    print("1. Добавить или обновить судно")
    print("2. Удалить судно")
    print("3. Добавить причал")
    print("4. Удалить причал")
    print("5. Пришвартовать судно")
    print("6. Отшвартовать судно")
    print("7. Вывести список свободных причалов")
    print("8. Выйти из программы")

    choice = input("Введите номер действия: ")

    if choice == '1':
        # Добавляем или обновляем судно
        ship_id = input("Введите идентификатор судна: ")
        ship_name = input("Введите название судна: ")
        construction_year = input("Введите год постройки судна: ")
        flag = input("Введите флаг судна: ")
        ship_type = input("Введите тип судна: ")
        add_or_update_ship(ship_id, ship_name, construction_year, flag, ship_type)
    elif choice == '2':
        # Удаляем судно
        ship_id = input("Введите идентификатор судна: ")
        delete_ship(ship_id)
    elif choice == '3':
        # Добавляем причал
        dock_id = input("Введите идентификатор причала: ")
        dock_name = input("Введите название причала: ")
        latitude = input("Введите широту причала: ")
        longitude = input("Введите долготу причала: ")
        max_ships = input("Введите максимальное количество судов, которое может причаливать на причале: ")
        add_dock(dock_id, dock_name, latitude, longitude, max_ships)
    elif choice == '4':
        # Удаляем причал
        dock_id = input("Введите идентификатор причала: ")
        delete_dock(dock_id)
    elif choice == '5':
        # Пришвартовываем судно на причал
        ship_id = input("Введите идентификатор судна: ")
        dock_id = input("Введите идентификатор причала: ")
        dock_ship(ship_id, dock_id)
    elif choice == '6':
        # Отшвартовываем судно с причала
        ship_id = input("Введите идентификатор судна: ")
        undock_ship(ship_id)
    elif choice == '7':
        # Выводим список свободных причалов
        get_free_docks()
    elif choice == '8':
        # Выходим из программы
        break
    else:
        print("Неверный выбор. Пожалуйста, попробуйте еще раз.")
