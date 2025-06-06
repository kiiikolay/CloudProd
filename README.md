# Яндекс.Диск Синхронизатор

Программа для автоматической синхронизации локальной папки с Яндекс.Диском.

## Описание

Эта программа обеспечивает автоматическую одностороннюю синхронизацию указанной локальной папки на вашем компьютере с папкой на Яндекс.Диске.
Она использует API Яндекс.Диска для отслеживания изменений в дирректории компьютера и обеспечивает её постоянную синхронизацию с дирректорией на Яндекс Диске.

## Возможности

*   **Односторонняя синхронизация:** Изменения, сделанные в локальной папке автоматически отражаются на Яндекс.Диске.
*   **Автоматическое отслеживание изменений:** Программа постоянно отслеживает изменения в файлах (добавление, удаление, изменение) и синхронизирует их.
*   **Фоновый режим работы:** Синхронизация происходит в фоновом режиме, не мешая вашей работе.
*   **Настройка интервала синхронизации:** Возможность задать интервал времени, через который программа будет проверять изменения.
*   **Логирование:**  Ведение журнала операций синхронизации для отслеживания работы программы и выявления возможных проблем.
*   **Поддержка больших файлов:** Оптимизированная работа с большими файлами для эффективной синхронизации.

## Требования

*   Python 3.12
*   Установленные библиотеки:
    *   black==25.1.0
    *   certifi==2025.1.31
    *   charset-normalizer==3.4.1
    *   click==8.1.8
    *   dotenv==0.9.9
    *   idna==3.10
    *   loguru==0.7.3
    *   mypy_extensions==1.1.0
    *   packaging==25.0
    *   pathspec==0.12.1
    *   platformdirs==4.3.7
    *   python-dotenv==1.1.0
    *   requests==2.32.3
    *   urllib3==2.4.0

## Установка

1.  Установите Python 3.12.
2.  Клонируйте репозиторий:

    ```bash
    git clone https://github.com/kiiikolay/CloudProd.git
    cd <название_папки_репозитория>
    ```

3.  Установите необходимые библиотеки:

    ```bash
    pip install -r requirements.txt
    ```

## Настройка

1.  **Получение токена Яндекс.Диска:**

    *   Перейдите по ссылке:  https://oauth.yandex.ru/authorize?response\_type=token&client\_id= <ID вашего приложения>
        *   Замените `<ID вашего приложения>` на ID вашего приложения, зарегистрированного в Яндекс.OAuth.  (Если у вас еще нет приложения, создайте его в [Яндекс.OAuth](https://oauth.yandex.ru/))
    *   Предоставьте приложению необходимые права доступа к Яндекс.Диску.
    *   Скопируйте полученный токен.

2.  **Конфигурационный файл (`.env`):**

    Создайте файл `.env` в корневой папке проекта со следующим содержимым, заменив значения на свои:

    ```.env
    API_KEY="YOUR_YANDEX_DISK_TOKEN"
    DIR_PATH="/path/to/your/local/folder"
    DISK_PATH="/path/to/your/remote/folder/on/yandexdisk"  # Относительно корневой папки Яндекс.Диска
    URL="https://cloud-api.yandex.net/v1/disk/resources"
    LOG_FILE="/path/to/your/log/folder"
    ```

    *   `API_KEY`:  Токен, полученный на предыдущем шаге.
    *   `DIR_PATH`:  Путь к локальной папке, которую нужно синхронизировать.
    *   `DISK_PATH`:  Путь к папке на Яндекс.Диске, с которой будет происходить синхронизация.  (Например, `/MySyncFolder`).  Путь указывается относительно корневой папки вашего Яндекс.Диска.
    *   `URL`:  URL API Яндекс Диска - "https://cloud-api.yandex.net/v1/disk/resources"
    *   `LOG_FILE`:  Путь к файлу логов (Например, `/log.json`)

## Запуск

Запустите программу из командной строки:

```bash
python cycle.py

Использование
После запуска программа начнет синхронизировать указанную локальную папку с Яндекс.Диском в фоновом режиме. Вы можете изменять файлы в любой из папок, и изменения будут автоматически перенесены в другую папку в соответствии с заданным интервалом синхронизации.

Обработка ошибок
Программа ведет журнал ошибок и предупреждений в файле log.json. В случае возникновения проблем, изучите этот файл для получения дополнительной информации.
