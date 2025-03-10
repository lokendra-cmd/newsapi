from rest_framework import serializers

class URLSerializer(serializers.Serializer):
    url = serializers.URLField(required=True, help_text="URL of the news website to summarize") 