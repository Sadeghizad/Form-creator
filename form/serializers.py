from .models import Answer
from rest_framework import serializers

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["question", "select", "option","text"]
    def validate(self, data):
        select = data.get('select', None)
        option = data.get('option', None)
        text = data.get('text', '').strip()

        # Check if all three fields are blank or None
        if not select and not option and not text:
            raise serializers.ValidationError("At least one of 'select', 'option', or 'text' must be provided.")
        
        return data
