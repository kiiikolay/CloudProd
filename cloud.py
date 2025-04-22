import os
from loguru import logger
from curses.ascii import isalpha
import requests
import pprint
from config import API, DIR_PATH, DISK_PATH, URL, LOG_FILE

logger.add(LOG_FILE, format='{level} {time} {file} {function} {line} {message} {exception}',
           serialize=True, level="INFO", rotation="500 MB")



class Connector:
    def __init__(self):
        logger.debug("Инициализация Connector")
        self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {API}'}
        self.url = URL
        self.disk_path = DISK_PATH
        self.file_path = DIR_PATH
        logger.debug(f"URL: {self.url}, Disk Path: {self.disk_path}")


    def load(self, path_file, replace=False, f_path=None):
        """
        Загружает файл на диск.
        """
        file_name = os.path.basename(f_path) if f_path else "unknown_file_name" #Если f_path == None
        logger.info(f"Попытка загрузки файла: {file_name}, Replace: {replace}")

        try:
            upload_url = f"{self.url}/upload?path={self.disk_path + '/' + file_name}&overwrite={replace}"
            logger.debug(f"URL запроса: {upload_url}")
            resp = requests.request(
                "GET",
                upload_url,
                headers=self._headers
            )

            # Проверяем статус код ответа
            if resp.status_code != 200:
                logger.error(f"Ошибка при запросе на загрузку. Status Code: {resp.status_code}, Response: {resp.text}")
                return

            resp_json = resp.json()
            logger.debug(f"Ответ от сервера при запросе на загрузку: {resp_json}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к серверу: {e}")
            return  # Или выбросьте исключение, в зависимости от вашей логики

        if resp_json:
            if 'href' in resp_json:
                logger.debug(f"Путь к файлу для загрузки: {path_file}")
                try:
                    with open(path_file, "rb") as f:
                        response = requests.put(resp_json['href'], files={'file': f})

                        # Проверяем статус код ответа при загрузке файла
                        if response.status_code >= 400:  # 4xx и 5xx коды считаем ошибками
                            logger.error(f"Ошибка при загрузке файла. Status Code: {response.status_code}, Response: {response.text}")
                            response.raise_for_status()  # Вызываем исключение для обработки

                        logger.info(f"Файл {file_name} успешно загружен.  Status Code: {response.status_code}")  # Логируем status code

                except FileNotFoundError:
                    logger.error(f"Файл по пути {path_file} не найден")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Ошибка при загрузке файла: {e}")
                except Exception as e:
                    logger.exception(f"Неожиданная ошибка при загрузке файла: {e}")  # Логируем все остальные исключения с трассировкой стека
            else:
                logger.warning(f"Ключ 'href' отсутствует в ответе сервера: {resp_json}")
        else:
            logger.warning("Не получен ответ от сервера при подготовке к загрузке.")


    def reload(self, path_file, f_path=None):
        """
        Перезагружает файл, устанавливая replace в True.
        """
        logger.info(f"Перезагрузка файла: {f_path}")
        self.load(path_file=path_file, replace=True, f_path=f_path)

    def delete(self, f_path):
        """
        Удаляет файл.
        """
        logger.info(f"Попытка удаления файла: {f_path}")

        params = {
            "path": DISK_PATH + f"/{f_path}"
        }

        try:
            response = requests.delete(self.url, headers=self._headers, params=params)
            response.raise_for_status() # Проверка на ошибки HTTP
            if response.status_code == 204:
                logger.info(f"Файл {f_path} успешно удален.")
                return True, "Файл успешно удален."
            else:
                logger.warning(f"Неожиданный статус код {response.status_code} при удалении файла.")
                return False, f"Неожиданный статус код {response.status_code} при удалении файла."
        except requests.exceptions.RequestException as e:
             logger.error(f"Ошибка при удалении файла {f_path}: {e}")
             return False, f"Ошибка при удалении файла: {e}"
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при удалении файла {f_path}: {e}")
            return False, f"Неожиданная ошибка при удалении файла: {e}"

    def info(self):
        """
        Получает информацию о файлах в указанной директории.
        """
        logger.info(f"Запрос информации о файлах в директории: {DISK_PATH}")
        info = {}
        params = {'path': DISK_PATH}

        try:
            response = requests.request("GET", self.url, params=params, headers=self._headers).json()
            logger.debug(f"Ответ от сервера при запросе информации: {response}")

            names = []
            if 'name' in response:
                names.append(response['name'])

            if '_embedded' in response and 'items' in response['_embedded']:
                for item in response['_embedded']['items']:
                    if 'name' in item:
                        names.append(item['name'])
            result = names[1:]
            logger.info(f"Получен список файлов: {result}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе информации о файлах: {e}")
            return [] # Или обработайте ошибку иначе
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при получении информации о файлах: {e}")
            return []



# if __name__ == '__main__':
    # a = Connector()
    # a.load()
    # a.reload()
    # a.delete()
    # a.info()










"""___________________________________________________________________________________________"""
# """  Запрос содержимого и путь папки на Диске  """
#
# url = "https://cloud-api.yandex.net/v1/disk/resources"
#
# params = {'path': 'app:/'}
# headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {API}'}
#
# response = requests.request("GET", url, params=params, headers=headers)
#
# print(response.text)