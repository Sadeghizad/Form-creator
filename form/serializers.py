
from rest_framework import serializers
from .models import Process, Form, Option, Question, Category, Answer
from django.db.models import Max

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        exclude = ['user']
        extra_kwargs = {
            'order': {'required': False}  
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        
        return representation    

    def validate(self, data):
       
        if data.get('is_private') and not data.get('password'):
            raise serializers.ValidationError("A password is required for private processes.")

        if not data.get('order'):
            raise serializers.ValidationError("Process must have at least one question.")
        
        user = self.context['request'].user
        for question_id in data['order']:
            question = Question.objects.get(id=question_id)
            if question.user != user:
                raise serializers.ValidationError("You can only add questions you created.")    
        
        return data  

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        exclude = ['user']    

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['user'] 

    def validate(self, data):    
        if data['type'] == 2 or data['type'] == 3:
                if not data.get('order'):
                    raise serializers.ValidationError("You must add options for test or checkbox questions.")
                user = self.context['request'].user
                for option_id in data['order']:
                    option = Option.objects.get(id=option_id)
                    if option.user != user:
                        raise serializers.ValidationError("You can only add options you created.")

        if data['type'] == 1 and data.get('order'):
            raise serializers.ValidationError("Text questions don't have options.")              


        return data                


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["question", "select", "option","text"]
    def validate(self, data):
        select = data.get('select', None)
        option = data.get('option', None)
        text = data.get('text', '').strip()

        
        if not select and not option and not text:
            raise serializers.ValidationError("At least one of 'select', 'option', or 'text' must be provided.")
        return data        


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.role == 'admin' or user.is_staff:
            validated_data['user'] = None  
        else:
            validated_data['user'] = self.context['request'].user 
        return super().create(validated_data)            

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        exclude = ['user'] 

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation    

    def validate(self, data):
        if data.get('is_private') and not data.get('password'):
            raise serializers.ValidationError("A password is required for private forms.")

        if not data.get('order'):
            raise serializers.ValidationError("Form must have at least one process.")

        user = self.context['request'].user
        for process_id in data['order']:
            process = Process.objects.get(id=process_id)
            if process.user != user and process.is_private:
                raise serializers.ValidationError("You can only add processes you own or that are public.")    
        return data    

    def validate_category(self, value):
        user = self.context['request'].user
        if value.user and value.user != user:
            raise serializers.ValidationError('You are not allowed to add your form to this category.')

        return value    


