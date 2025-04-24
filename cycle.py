import os
from importlib.metadata import files
import datetime
from time import sleep
from config import DIR_PATH, API, LOG_FILE
from loguru import logger

from cloud import Connector
from database_connect import sql_req

logger.add(
    LOG_FILE,
    format="{level} {time} {file} {function} {line} {message} {exception}",
    serialize=True,
    level="INFO",
    rotation="500 MB",
)


def get_last_modified_time(file_path):
    """
    Возвращает время последнего изменения файла в формате 'YYYY-MM-DD HH:MM:SS'.

    Args:
        file_path (str): Полный путь к файлу.

    Returns:
        str: Время последнего изменения или None, если файл не найден или произошла ошибка.
    """
    try:
        timestamp = os.path.getmtime(file_path)
        datetime_object = datetime.datetime.fromtimestamp(timestamp)
        last_modified_time = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(
            f"Время последнего изменения файла {file_path}: {last_modified_time}"
        )
        return last_modified_time
    except FileNotFoundError:
        logger.warning(f"Файл не найден: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении времени изменения файла {file_path}: {e}")
        return None


def download_db(data):
    """
    Загружает данные в базу данных.

    Функция принимает словарь, где ключи - имена файлов, а значения - соответствующие им даты и время последнего обновления.
    Для каждой пары ключ-значение вызывает функцию `sql_req` для добавления или обновления записи в базе данных.
    В случае успеха логирует информацию об успешном сохранении данных.
    В случае ошибки логирует информацию об ошибке.

    Args:
        data (dict): Словарь с данными для записи в базу данных. Ключи - имена файлов, значения - дата и время обновления.
    """

    logger.info("Начало download_db")
    try:
        for key, value in data.items():
            sql_req(func="add", file=key, add_or_update_datetime=value)
        logger.debug("data успешно сохранен в database.db")
    except Exception as e:
        logger.error(f"Ошибка при записи в database.db: {e}")


def open_db():
    """
    Открывает и считывает данные из базы данных.

    Функция вызывает функцию `sql_req` для чтения данных из базы данных.
    В случае успеха возвращает считанные данные.
    В случае ошибки логирует информацию об ошибке и возвращает None.

    Returns:
        dict: Данные, считанные из базы данных, или None в случае ошибки.
    """

    logger.info("Начало open_db")
    try:
        data_db = sql_req(func="read")
        return data_db
    except Exception as e:
        logger.error(f"Ошибка при чтении db: {e}")
        return None


def clear_db(data_db, list_file):
    """
    Очищает базу данных, удаляя записи, которых нет в `list_file`.

    Функция принимает текущие данные из базы данных (`data_db`) и список файлов (`list_file`).
    Определяет ключи, которые присутствуют в `data_db`, но отсутствуют в `list_file`.
    Для каждого такого ключа вызывает функцию `sql_req` для удаления соответствующей записи из базы данных,
    а также удаляет ключ из локальной копии `data_db`.
    Возвращает обновленный словарь `data_db`.

    Args:
        data_db (dict): Текущие данные из базы данных.
        list_file (list): Список файлов, которые должны остаться в базе данных.

    Returns:
        dict: Обновленный словарь `data_db` после очистки.
    """

    logger.info("Начало clear_db")
    list_deleted = [k for k in data_db if k not in list_file]

    for i in list_deleted:
        sql_req(func="del", file=i)
        del data_db[i]
        logger.debug(f"Удален ключ {i} из data_db и database.db")

    logger.debug(f"Финальный data_db после очистки: {data_db}")
    return data_db


def path_generator(file):
    """
    Генерирует полный путь к файлу.

    Args:
        file (str): Имя файла.

    Returns:
        str: Полный путь к файлу.
    """
    path_file = os.path.join(DIR_PATH, file)
    logger.debug(f"Сгенерирован путь к файлу {file}: {path_file}")
    return path_file


def update_file_time(file, data_disk):
    """
    Обновляет время для файла в словаре data_disk.

    Args:
        file (str): Имя файла.
        data_disk (dict): Словарь для хранения данных о файлах.

    Returns:
        dict: Обновленный словарь data_disk.
    """
    now = datetime.datetime.now()
    data_disk[file] = now.strftime("%Y-%m-%d %H:%M:%S")
    logger.debug(f"Обновлено время для файла {file}: {data_disk[file]}")
    return data_disk


def infinite_loop():
    """
    Основной цикл программы, который отслеживает изменения в директории с файлами.
    """
    logger.info("Начало infinite_loop")
    data_disk = {}
    attribute = Connector()

    while True:
        logger.debug("Начало итерации цикла")
        list_file = os.listdir(DIR_PATH)
        files_on_disk = attribute.info()
        logger.debug(f"Файлы в директории: {list_file}")
        logger.debug(f"Файлы на диске (attribute.info()): {files_on_disk}")

        # Обнаружение новых файлов
        for file in list_file:
            if file not in files_on_disk:
                logger.info(f"Новый файл обнаружен: {file}")
                path_file = path_generator(file)
                attribute.load(f_path=file, path_file=path_file)
                data_disk = update_file_time(file, data_disk)

        # Обнаружение удаленных файлов
        for file in files_on_disk:
            if file not in list_file:
                logger.info(f"Файл удален: {file}")
                attribute.delete(f_path=file)

        # Загрузка JSON данных
        data_db = open_db()

        if data_db is None:
            data_db = {}

        logger.debug(f"Текущий data_db: {data_db}")

        # Проверка времени изменения файлов и обновление при необходимости
        for file in list_file:
            path_file = path_generator(file)
            last_modified_time = get_last_modified_time(path_file)

            if last_modified_time is not None:
                if file in data_db and last_modified_time > data_db.get(file, ""):
                    logger.info(f"Файл {file} нуждается в обновлении")
                    attribute.reload(path_file=path_file, f_path=file)
                    data_disk = update_file_time(
                        file, data_disk
                    )  # Обновляем время в data_disk
                else:
                    logger.debug(
                        f"Файл {file} не нуждается в обновлении или отсутствует в data_db"
                    )
            else:
                logger.warning(f"Не удалось получить время изменения для файла: {file}")

        # Обновляем data_db новыми данными из data_disk
        if data_disk:
            data_db.update(data_disk)

        # Очистка и сохранение database
        cleaned_data_db = clear_db(data_db, list_file)
        download_db(cleaned_data_db)

        # Очищаем data_disk после сохранения в db
        data_disk = {}

        logger.info("Конец итерации цикла")
        sleep(5)  # Используем time.sleep() для задержки


if __name__ == "__main__":
    infinite_loop()
