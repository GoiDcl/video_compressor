from rest_framework import serializers


class VideoCompressorSerializer(serializers.Serializer):
    """
    Сериализатор для эндпоинта сервиса сжатия видео.

    Поля:
        - file: файл, подлежащий сжатию
        - key: ключ авторизации для 1с
        - cookie: куки пользователя с веб-сервиса для 1с
    """

    file = serializers.FileField()
    key = serializers.CharField(required=False)
    cookie = serializers.CharField(required=False)

    class Meta:
        fields = ('file', 'key', 'cookie')
