import logging
import os
import uuid
from logging.handlers import RotatingFileHandler

import requests
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .decoder import encode_file_to_base64
from .processing import compress_video
from .serializers import VideoCompressorSerializer


def setup_logger(name, log_file, level=logging.DEBUG):
    """
    Настройка логгера.

    Параметры
    ---------
    formatter
        настройка вывода инфорамации в лог
            levelname - уровень важности
            asctime - время регистрации записи
            name - название модуля, который создал запись
            message - сама запись
    handler
        обработчик ротации файлов. если текущее сообщение вот-вот
        позволит файлу журнала превысить максимальный размер,
        то обработчик закроет текущий файл и откроет следующий.
            maxBytes - максимальный размер лог-файла, 50 Мб
            backupCount - количество лог-файлов
    """
    BACKUP_COUNT = 5
    MAX_LOG_WEIGHT = 52428800

    formatter = logging.Formatter(
        "%(levelname)s - %(asctime)s - %(name)s - %(message)s"
    )
    handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_WEIGHT, backupCount=BACKUP_COUNT
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


logger = setup_logger("video_compressor", "video_compressor.log")
URL_1C = os.environ.get("URL_1C")


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Необходимо для ограничения доступных методов."""
    pass


class VideoCompressorViewSet(CreateViewSet):
    """
    Вьюсет сервиса для сжатия видеофайлов.

    Параметры
    ---------
    input_file: file
        Отправленный на сжатие видеофайл
    key: string
        ключ для передачи файла в 1с
    name:
    compressed_file : file
        Результат работы программы - сжатый файл

    Алгоритм работы:
    0. Получаем файл
    1. Сериализатор проверяет валидность полученных данных и в случае
        вознкновения ошибок возвращает ошибки и 400 статус код
    2. Отправляем файл в функцию для сжатия
    3.1 В случае успеха кодируем файлы в base64
    3.1.1 Создаём ключи для передачи файлов в 1с
    3.1.2 Отправляем оригинал и сжатый файл в 1с, оповещаем об успехе
    3.2 Если сжатие не удалось оповещаем о неудаче
    """

    serializer_class = VideoCompressorSerializer

    def perform_create(self, serializer):
        if serializer.is_valid():
            input_file = serializer.validated_data["file"]
            # key = serializer.validated_data["key"]
            # name = serializer.validated_data["name"]

            with open(input_file.name, "wb") as file:
                file.write(input_file.read())

            logger.debug(f"Получен файл {input_file}. Начинаю сжатие...")

            compressed_file = compress_video(input_file.name, logger)

            if compressed_file:
                logger.debug(
                    "Сжатие файла прошло успешно. "
                    "Кодирую файлы в base64 и создаю ключи..."
                )
                encoded_orig_file = encode_file_to_base64(
                    input_file.name, logger
                )
                encoded_demo_file = encode_file_to_base64(
                    compressed_file, logger
                )
                orig_key = str(uuid.uuid4())
                demo_key = str(uuid.uuid4())
                if encoded_orig_file and encoded_demo_file:
                    logger.debug(
                        "Кодирование прошло успешно!"
                    )
                    try:
                        logger.debug(
                            "Отправляю файлы в 1с..."
                        )
                        url = URL_1C
                        key = os.environ.get("COOKIE")
                        headers = {"XRMCCookie": key}
                        data = {
                            "Данные": encoded_orig_file,
                            "Ключ": orig_key,
                            "Пакет": 1,
                            "ПоследнийПакет": 1
                        }
                        r = requests.post(url, json=data, headers=headers)
                        logger.debug(
                            "Запрос на отправку файла успешно создан!\n"
                            "Ответ: {} {}".format(r.status_code, r.reason)
                        )
                        data = {
                            "Данные": encoded_demo_file,
                            "Ключ": demo_key,
                            "Пакет": 1,
                            "ПоследнийПакет": 1
                        }
                        r = requests.post(url, json=data)
                        logger.debug(
                            "Запрос на отправку файла успешно создан!\n"
                            "Ответ: {} {}".format(r.status_code, r.reason)
                        )
                        return Response(
                            status=status.HTTP_200_OK
                        )
                    except Exception as e:
                        logger.error(e)
            else:
                logger.error("Сжатие файла не удалось.")
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        else:
            logger.error(f"Возникли ошибки при передаче файла\n"
                         f"{serializer.errors}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

    """
    на случай если всё же придётся декодировать из base64

    def perform_create(self, serializer):
        if serializer.is_valid():
            encoded_file = serializer.validated_data["file"]
            key = serializer.validated_data["key"]
            name = serializer.validated_data["name"]

            logger.debug(f"Получен файл {name}. Начинаю декодирование...")

            input_file = decode_base64_to_file(encoded_file.name, name, logger)

            # with open(input_file, "wb") as file:
            #     file.write(input_file.read())

            if input_file:
                logger.debug(
                    "Декодирование прошло успешно! Приступаю к сжатию файла..."
                )

                compressed_file = compress_video(input_file.name, logger)

                if compressed_file:
                    logger.debug(
                        "Сжатие файла прошло успешно. "
                        "Кодирую файлы в base64 и создаю ключи..."
                    )
                    encoded_orig_file = encode_file_to_base64(
                        input_file.name, logger
                    )
                    encoded_demo_file = encode_file_to_base64(
                        compressed_file.name, logger
                    )
                    orig_key = str(uuid.uuid4())
                    demo_key = str(uuid.uuid4())
                    if encoded_orig_file and encoded_demo_file:
                        logger.debug(
                            "Кодирование прошло успешно!"
                        )
                        try:
                            logger.debug(
                                "Отправляю файлы в 1с..."
                            )
                            url = URL_1C
                            data = {
                                "Данные": encoded_orig_file,
                                "Ключ": orig_key,
                                "Пакет": 1,
                                "ПоследнийПакет": 1
                            }
                            r = requests.post(url, json=data)
                            logger.debug(
                                "Запрос на отправку файла успешно создан!\n"
                                "Ответ: {} {}".format(r.status_code, r.reason)
                            )
                            data = {
                                "Данные": encoded_demo_file,
                                "Ключ": demo_key,
                                "Пакет": 1,
                                "ПоследнийПакет": 1
                            }
                            r = requests.post(url, json=data)
                            logger.debug(
                                "Запрос на отправку файла успешно создан!\n"
                                "Ответ: {} {}".format(r.status_code, r.reason)
                            )
                            return Response(
                                status=status.HTTP_200_OK
                            )
                        except Exception as e:
                            logger.error(e)
                else:
                    logger.error("Сжатие файла не удалось.")
                    return Response(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            logger.error(f"Возникли ошибки при передаче файла\n"
                         f"{serializer.errors}")
            return Response(status=status.HTTP_400_BAD_REQUEST)
    """
