from loguru import logger
import json


def download_json(data, mode="w"):
    """
    Сохраняет данные в JSON файл.

    Args:
        data (dict): Данные для сохранения.
        mode (str): Режим открытия файла ('w' для записи, 'a' для добавления).
    """
    logger.info("Начало download_json")
    try:
        with open("data.json", mode, encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.debug("JSON успешно сохранен в data.json")
    except Exception as e:
        logger.error(f"Ошибка при записи в data.json: {e}")


def open_json():
    """
    Загружает данные из JSON файла.

    Returns:
        dict: Данные из JSON файла или None, если файл не найден или произошла ошибка.
    """
    logger.info("Начало open_json")
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data_json = json.load(f)
        logger.debug("JSON успешно загружен из data.json")
        return data_json
    except FileNotFoundError:
        logger.warning("Файл data.json не найден.")
        return None
    except json.JSONDecodeError:
        logger.error("Ошибка при разборе JSON из data.json. Возможно, файл поврежден.")
        return None
    except Exception as e:
        logger.error(f"Ошибка при чтении data.json: {e}")
        return None


def clear_json(data_json, list_file):
    """
    Удаляет устаревшие записи из JSON данных.

    Args:
        data_json (dict): JSON данные.
        list_file (list): Список актуальных файлов.

    Returns:
        dict: Очищенные JSON данные.
    """
    logger.info("Начало clear_json")
    list_deleted = [k for k in data_json if k not in list_file]

    for i in list_deleted:
        del data_json[i]
        logger.debug(f"Удален ключ {i} из data_json")

    logger.debug(f"Финальный data_json после очистки: {data_json}")
    return data_json
