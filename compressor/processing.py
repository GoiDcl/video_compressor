import os
import subprocess


def compress_video(input_file: str | os.PathLike[str],
                   logger) -> bool | os.PathLike[str]:
    """
    Функция для сжатия видеофайлов.

    :param input_file: полученный видеофайл
    :param logger: для записи логов
    :return: В случае успеха - сжатый файл, в случае неудачи - False

    Алгоритм работы:
    0. Получаем файл для сжатия
    1. Получаем длительность видео с помощью ffprobe
    2. Задаём имя выходного файла (имя ориг. файла без расширения + _demo.mp4)
    3. Параметы сжатия:
            -i полученный файл
            -b:v битрейт видео
            -c:a аудиокодек
            -b:a битрейт аудио
            -r кадры в секунду
            -s разрешение
            -y не спрашивать разрешение на перезапись файла
            output file итоговый файл
    4. Выполняем сжатие и возвращаем итоговый файл
    5. В случае возникновения ошибок логгируем их и возвращаем False
    """

    FPS = os.environ.get('FPS')
    AUDIO_BITRATE = os.environ.get('AUDIO_BITRATE')
    AUDIO_CODEK = os.environ.get('AUDIO_CODEK')
    RESOLUTION = os.environ.get('RESOLUTION')
    VIDEO_BITRATE = os.environ.get('VIDEO_BITRATE')

    try:
        output_file = input_file[:-4] + '_demo.mp4'

        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-b:v', VIDEO_BITRATE,
            '-c:a', AUDIO_CODEK,
            '-b:a', AUDIO_BITRATE,
            '-r', FPS,
            '-s', RESOLUTION,
            '-y',
            output_file
        ]

        subprocess.run(ffmpeg_cmd)

        return output_file

    except subprocess.CalledProcessError as e:
        logger.error(e)
        return False
