import os

import requests
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .decoder import encode_file_to_base64
from .logger import setup_logger
from .processing import compress_video
from .serializers import VideoCompressorSerializer

logger = setup_logger("video_compressor", "video_compressor.log")
URL_1C = os.environ.get("URL_1C")


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Необходимо для ограничения доступных методов."""
    pass


class VideoCompressorViewSet(CreateViewSet):
    """
    Вьюсет сервиса для сжатия видеофайлов.

    input_file: file
        Полученый для сжатия видеофайл
    key: string
        Ключ для передачи файла в 1с
    cookie: string
        Куки для авторизации в 1с

    encoded_file : base64 string
        Закодированный для передачи оригинальный видеофайл
    encoded_demo_file: base64 string
        Закодированный для передачи сжатый видеофайл

    Алгоритм работы:
    0. Получаем файл
    1. Сериализатор проверяет валидность полученных данных и в случае
        вознкновения ошибок возвращает ошибки и 400 статус код
    2. Отправляем файл в функцию для сжатия
    3. Если сжатие не удалось оповещаем о неудаче
    4. В случае успеха кодируем сжатый файл в base64
    5. Отправляем оригинал и сжатый файл в 1с, оповещаем об успехе
    """

    serializer_class = VideoCompressorSerializer

    def perform_create(self, serializer):
        if serializer.is_valid():
            input_file = serializer.validated_data["file"]
            key = serializer.validated_data["key"]
            cookie = serializer.validated_data["cookie"]

            with open(input_file.name, "wb") as file:
                file.write(input_file.read())

            logger.debug(f"Получен файл {input_file}. Начинаю сжатие...")

            compressed_file = compress_video(input_file.name, logger)

            if compressed_file:

                logger.debug(
                    "Сжатие файла прошло успешно. "
                    "Кодирую файлы в base64..."
                )
                encoded_orig_file = encode_file_to_base64(
                    input_file.name, logger
                )
                encoded_demo_file = encode_file_to_base64(
                    compressed_file, logger
                )
                if encoded_orig_file and encoded_demo_file:
                    logger.debug(
                        "Кодирование прошло успешно!"
                    )
                    try:
                        logger.debug(
                            "Отправляю файлы в 1с..."
                        )
                        url = URL_1C
                        headers = {
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                            "xrmccookie": cookie
                        }
                        data = {
                            "Данные": encoded_orig_file,
                            "Ключ": key,
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
                            "Ключ": key,
                            "Пакет": 1,
                            "ПоследнийПакет": 1
                        }
                        r = requests.post(url, json=data, headers=headers)
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
