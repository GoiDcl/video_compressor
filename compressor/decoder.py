import base64


def decode_base64_to_file(base64_string, output_file, logger):
    try:
        decoded_data = base64.b64decode(base64_string)

        with open(output_file, 'wb') as output_file:
            output_file.write(decoded_data)

        logger.debug(f"Файл успешно декодирован и сохранён как {output_file}")

    except Exception as e:
        logger.error(f"Ошибка декодирования из Base64: {e}")
        return False


def encode_file_to_base64(file_path, logger):
    try:
        with open(file_path, 'rb') as file:
            encoded_data = base64.b64encode(file.read()).decode('utf-8')

        return encoded_data

    except Exception as e:
        logger.error(f"Ошибка кодирования в Base64: {e}")
        return False
