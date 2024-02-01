import subprocess
import os


def compress_video(input_file, logger, target_size=10, byte=8):
    """
    Функция для сжатия видеофайлов.

    :param logger: для записи логов
    :param input_file: полученный видеофайл
    :param target_size: параметр для вычисления итогового битрейта,
        выставленно минимальное значение для наилучшей компрессии
    :param byte: переменная хранящая количество битов в байте
    :return: Возвращаемое значение. В случае успеа - сжатый файл,
        в случае неудачи - False

    Алгоритм работы:
    0. Получаем файл для сжатия
    1. Получаем длительность видео с помощью ffprobe
    2. Задаём имя выходного файла (имя ориг. файла + _compr
    3. Вносим длительность видео в переменную duration
    4. Вычисляем итоговый битрейт
    5. Выполняем сжатие. Параметы:
            -i полученный файл
            -b:v битрейт видео
            -c:a аудиокодек
            -b:a битрейт аудио
            -r кадры в секунду
            -s разрешение
            output file итоговый файл
    6. Выполняем сжатие и возвращаем итоговый файл
    7. В случае возникновения ошибок прерываем выполнение и возвращаем False
    """

    ffprobe_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', input_file
    ]

    FPS = os.environ.get('FPS')
    AUDIO_BITRATE = os.environ.get('AUDIO_BITRATE')
    AUDIO_CODEK = os.environ.get('AUDIO_CODEK')
    RESOLUTION = os.environ.get('RESOLUTION')

    try:
        output_file = input_file[:-4] + '_demo.mp4'
        duration = float(
            subprocess.check_output(ffprobe_cmd).decode('utf-8').strip()
        )
        bitrate = int((target_size * byte) / duration)

        # '-progress', './video_compressor.log',
        # '-stats_period', '2',
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-b:v', f'{bitrate}k',
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
