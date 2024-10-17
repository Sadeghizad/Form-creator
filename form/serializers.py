from rest_framework import serializers
from .models import Process, Form, Option, Question, Category, Answer
from django.db.models import Max

class ProcessSerializer(serializers.ModelSerializer):
    forms = serializers.SerializerMethodField()
    class Meta:
        model = Process
        exclude = ['user']
        extra_kwargs = {
            'order': {'required': False}  
        }

    def get_forms(self, obj):  
        return "id: {}, name: {}".format(obj.form.id, obj.form.name) 

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        
        return representation    

    def create(self, validated_data):
        form = validated_data.get('form')
        if form.user != self.context['request'].user:
            raise serializers.ValidationError("You do not have permission to add processes to this form.")

        if 'order' not in validated_data:
            last_order = Process.objects.filter(form=form).aggregate(Max('order'))['order__max'] or 0
            validated_data['order'] = last_order + 1

        if Process.objects.filter(form=form, order=validated_data['order']).exists():
            raise serializers.ValidationError("The combination of form and order must be unique.")        

        return super().create(validated_data)  

    def validate(self, data):
       
        if data.get('is_private') and not data.get('password'):
            raise serializers.ValidationError("A password is required for private processes.")
        
        return data  

class OptionSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    class Meta:
        model = Option
        fields = '__all__'

    def get_question(self, obj):  
        return "id: {}, text: {}".format(obj.question.id, obj.question.text)     

    def create(self, validated_data):
        question = validated_data['question']
        if question.process.form.user != self.context['request'].user:
            raise serializers.ValidationError("You do not have permission to add options to this question.")
        if question.type == 1:
            raise serializers.ValidationError("Options cannot be defined for text questions.")
        return super().create(validated_data)    

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        exclude = ['user'] 
        extra_kwargs = {
            'order': {'required': False}  # Make order optional
        }

    def create(self, validated_data):
        process = validated_data['process']
        form = validated_data['form']
        if process.form.user != self.context['request'].user:
            raise serializers.ValidationError("You do not have permission to add questions to this process.")

        if 'order' not in validated_data:
            last_order = Question.objects.filter(process=process).aggregate(Max('order'))['order__max'] or 0
            validated_data['order'] = last_order + 1

        if Question.objects.filter(form=form, process=orcess, order=validated_data['order']).exists():
            raise serializers.ValidationError("The combination of form, process and order must be unique.")   

        return super().create(validated_data)    


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

    def validate(self, data):
        question = data['question']
        process = question.process  
       
        if process.linear:
            if question.type == 1 and not data.get('text'):  # Text 
                raise serializers.ValidationError("This question requires a text answer.")
            elif question.type == 2 and not data.get('select'):  # Checkbox
                raise serializers.ValidationError("This question requires at least one option to be selected.")
            elif question.type == 3 and not data.get('option'):  # Test
                raise serializers.ValidationError("This question requires an option to be selected.")

        return data        


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'        

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
        return data    
    
    
