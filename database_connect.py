import sqlite3
from sqlite3 import IntegrityError


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.cursor = None
        self.connection = None

    def __enter__(self):
        """
        Устанавливает соединение с базой данных при входе в контекстный менеджер.

        Returns:
            self: возвращает экземпляр DatabaseManager
        """

        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                filename TEXT PRIMARY KEY NOT NULL ,
                datetime TEXT NOT NULL
            )
        """
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Закрывает соединение с базой данных при выходе из контекстного менеджера.

        Returns:
            exc_type: Тип исключения, если оно возникло
            exc_val: Значение исключения, если оно возникло
            exc_tb: Трассировка исключения, если оно возникло

        """
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def data_add(self, file_name, add_or_update_time):
        """
        Добавляет запись о файле в базу данных или обновляет существующую запись.

        Args:
            file_name (str): Имя файла.
            add_or_update_time (str): Дата и время добавления или обновления файла в формате ISO.

        Returns:
            sqlite3.Cursor: Объект курсора, используемый для выполнения SQL-запросов.

        Raises:
            sqlite3.IntegrityError: Возникает, если при добавлении записи нарушается ограничение уникальности (например, если файл с таким именем уже существует).
                                     В этом случае, функция выполняет обновление времени для существующей записи.

        Описание:
            Функция пытается добавить новую запись в таблицу 'files' с указанным именем файла и датой/временем.
            Если запись с таким именем файла уже существует (возникает ошибка IntegrityError), функция обновляет
            дату/время для существующей записи.  Таким образом, функция либо добавляет новый файл, либо обновляет
            информацию о существующем.
        """

        try:
            return self.cursor.execute(
                "INSERT INTO files (filename, datetime) " "VALUES (?, ?)",
                (file_name, add_or_update_time),
            )
        except IntegrityError:
            return self.cursor.execute(
                "UPDATE files " "SET datetime = ? " "WHERE filename =?",
                (add_or_update_time, file_name),
            )

    def data_delete(self, file_name):
        """
        Удаляет запись о файле из базы данных.

        Args:
            file_name (str): Имя файла, запись о котором нужно удалить.

        Returns:
            sqlite3.Cursor: Объект курсора, используемый для выполнения SQL-запросов.

        Описание:
            Функция удаляет запись из таблицы 'files' для файла с указанным именем.
        """

        return self.cursor.execute(
            "DELETE " "FROM files " "WHERE filename = ?", (file_name,)
        )

    def data_read(self):
        self.cursor.execute("SELECT * " "FROM files")
        data = self.cursor.fetchall()
        files = {elem[0]: elem[1] for elem in data}
        return files


def sql_req(func, **kwargs):
    """
    Выполняет SQL-запросы к базе данных на основе переданных аргументов.

    Функция принимает название операции (`func`) и набор именованных аргументов (`**kwargs`),
    которые определяют параметры запроса. В зависимости от значения `func`, функция выполняет
    операции добавления, обновления или удаления данных в базе данных.

    Аргументы:
        func (str): Название операции, которую необходимо выполнить ("add", "update", "del").
        **kwargs: Именованные аргументы, содержащие параметры для SQL-запроса.
                   Обязательные параметры зависят от значения `func`.

    Поддерживаемые операции и ожидаемые аргументы:
        - "add" или "update":
            - file (str): Имя файла.
            - add_or_update_datetime (str): Дата и время добавления или обновления файла.
        - "del":
            - file (str): Имя файла, который необходимо удалить.

    Пример использования:
        # Добавление новой записи
        sql_req(func="add", file="example.txt", add_or_update_datetime="2024-10-27 10:00:00")

        # Удаление записи
        sql_req(func="del", file="example.txt")
    """

    data = {"func": func}
    for key, value in kwargs.items():
        data.update({f"{key}": f"{value}"})
    print(data)
    with DatabaseManager("database.db") as db:
        if func in ("add", "update"):
            return db.data_add(
                file_name=data["file"],
                add_or_update_time=data["add_or_update_datetime"],
            )
        elif func == "del":
            return db.data_delete(file_name=data["file"])
        elif func == "read":
            return db.data_read()
        return None
