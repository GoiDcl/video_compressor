from rest_framework import serializers


class VideoCompressorSerializer(serializers.Serializer):
    """
    Сериализатор для эндпоинта сервиса сжатия видео.

    Содержит единственное поле - файл подлежащий сжатию.
    """

    file = serializers.FileField()
    key = serializers.CharField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        fields = ('file', 'key', 'name')
