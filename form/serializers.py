from rest_framework import serializers
from .models import Process, Form, Option, Question, Category, Answer

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        exclude = ['user']

    def create(self, validated_data):
        form = validated_data['form']
        if form.user != self.context['request'].user:
            raise serializers.ValidationError("You do not have permission to add processes to this form.")

       
        if 'order' not in validated_data:
            last_order = Process.objects.filter(form=form).aggregate(models.Max('order'))['order__max'] or 0
            validated_data['order'] = last_order + 1
            print(validated_data['order'])

      
        return super().create(validated_data)  

    def to_representation(self, instance):
        representation = super().to_representation(instance)

      
        if not instance.is_private:
            representation.pop('password', None)
        
        return representation

    def validate(self, data):
       
        if data.get('is_private') and not data.get('password'):
            raise serializers.ValidationError("A password is required for private processes.")
        
        return data  

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        exclude = ['user'] 

    def create(self, validated_data):
        process = validated_data['process']
        if process.form.user != self.context['request'].user:
            raise serializers.ValidationError("You do not have permission to add questions to this process.")
      
        if 'order' not in validated_data:
            last_order = Question.objects.filter(process=process).aggregate(models.Max('order'))['order__max'] or 0
            validated_data['order'] = last_order + 1
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

    def validate(self, data):
        
        if data.get('is_private') and not data.get('password'):
            raise serializers.ValidationError("A password is required for private forms.")
        return data    
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        
        if not instance.is_private:
            representation.pop('password', None)
        
        return representation
