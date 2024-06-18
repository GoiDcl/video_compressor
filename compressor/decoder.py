import base64
import os


def encode_file_to_base64(file_path: str | os.PathLike[str],
                          logger) -> str | bool:
    """
    Функция для кодирования файла в base64 строку.

    :param file_path: путь до файла
    :param logger: для записи логов
    :return: в случае успеха возвращаем файл, в случае неудачи - False
    """
    try:
        with open(file_path, 'rb') as file:
            encoded_data = base64.b64encode(file.read()).decode('utf-8')

        return encoded_data

    except Exception as e:
        logger.error(f"Ошибка кодирования в Base64: {e}")
        return False
