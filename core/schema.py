import graphene
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ValidationError
from form.models import Form, Process, Question, Option, Answer
from graphql_jwt.decorators import login_required
import graphql_jwt

# Types
class OptionType(DjangoObjectType):
    class Meta:
        model = Option

class QuestionType(DjangoObjectType):
    options = graphene.List(OptionType)

    class Meta:
        model = Question

    def resolve_options(self, info):
        if self.order:  # Ensure we check if order exists
            return Option.objects.filter(id__in=self.order)
        return []

    # def resolve_options_to_show(self, info):
    #     if self.order:
    #         option_ids = self.order  # Assuming this is the ordered list of option IDs
    #         options = [Option.objects.get(id=option_id) for option_id in option_ids]
    #         return options    
    #     return []    

class ProcessType(DjangoObjectType):
    questions_to_show = graphene.List(QuestionType)

    class Meta:
        model = Process

class FormType(DjangoObjectType):
    processes_to_show = graphene.List(ProcessType)

    class Meta:
        model = Form

    def resolve_processes_to_show(self, info):
        user = info.context.user
        processes_to_show = []

        # Iterate through each process ID in form's `order`
        for process_id in self.order:
            try:
                process = Process.objects.get(pk=process_id)
                question_ids = process.order  # Retrieve the ordered question IDs
                questions = [Question.objects.get(id=q_id) for q_id in question_ids]

                if self.linear:
                    # Filter out already answered questions for this form and user
                    answered_question_ids = Answer.objects.filter(
                        form=self,
                        user=user,
                        question__in=questions
                    ).values_list('question_id', flat=True)
                    
                    # Only show the first unanswered question if any remain
                    unanswered_questions = [q for q in questions if q.id not in answered_question_ids]
                    process.questions_to_show = unanswered_questions[:1] if unanswered_questions else []
                    
                    # If we find the first process with unanswered questions, stop further iteration
                    if process.questions_to_show:
                        processes_to_show.append(process)
                        break
                else:
                    # For free forms, show all questions in the process order
                    process.questions_to_show = questions
                    processes_to_show.append(process)

            except Process.DoesNotExist:
                continue

        return processes_to_show
# Queries
class Query(graphene.ObjectType):
    form = graphene.Field(FormType, form_id=graphene.ID(required=True))

    @login_required
    def resolve_form(self, info, form_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")

        form = Form.objects.get(pk=form_id)
        
        # Pass the form instance to context for further use
        info.context.form_instance = form

        processes_to_show = []
        if form.order:
            for process_id in form.order:
                try:
                    process_instance = Process.objects.get(pk=process_id)
                    processes_to_show.append(process_instance)
                except Process.DoesNotExist:
                    continue

        form.processes_to_show = processes_to_show
        return form

# Input and Mutations
class AnswerInput(graphene.InputObjectType):
    question_id = graphene.ID(required=True)
    option_id = graphene.ID()  # Used if the question is single-choice (test)
    select_ids = graphene.List(graphene.ID)  # Used if the question is multiple-choice (checkbox)
    text = graphene.String()  # Used if the question is open-ended
    form_id = graphene.ID(required=True) 

class AnswerType(DjangoObjectType):
    class Meta:
        model = Answer


class SubmitAnswerMutation(graphene.Mutation):
    class Arguments:
        input = AnswerInput(required=True)

    answer = graphene.Field(AnswerType)

    @login_required
    def mutate(self, info, input):
        user = info.context.user

        # Fetch the question and validate it exists
        try:
            question = Question.objects.get(pk=input.question_id)
        except Question.DoesNotExist:
            raise ValidationError("Question not found")

        # Fetch the form and ensure it exists
        try:
            form = Form.objects.get(pk=input.form_id)
        except Form.DoesNotExist:
            raise ValidationError("Form not found")

        # Build ordered list of questions across all processes in form.order
        ordered_questions = []
        for process_id in form.order:
            try:
                process = Process.objects.get(pk=process_id)
                ordered_questions.extend(process.order)
            except Process.DoesNotExist:
                continue

        # Check if the question is within the form's ordered questions
        if question.id not in ordered_questions:
            raise ValidationError("Question not part of the ordered sequence in this form.")

        # Enforce linear order for answering questions if form is linear
        if form.linear:
            question_index = ordered_questions.index(question.id)
            previous_questions = Answer.objects.filter(
                form=form,
                user=user,
                question_id__in=ordered_questions[:question_index]
            ).count()

            # Ensure that all previous questions in the order are answered first
            if previous_questions < question_index:
                raise ValidationError("Answer previous questions in order first.")

        # Validation: Ensure the correct field is filled based on question type
        if question.type == 1:  # Text question
            if not input.text:
                raise ValidationError("Text field must be filled for text question.")
            if input.option_id or input.select_ids:
                raise ValidationError("Only the text field should be filled for text questions.")
        elif question.type == 3:  # Single-option question
            if not input.option_id:
                raise ValidationError("Option must be filled for single-choice question.")
            if input.text or input.select_ids:
                raise ValidationError("Only the option field should be filled for single-choice questions.")
        elif question.type == 2:  # Multiple-choice question
            if not input.select_ids:
                raise ValidationError("Select options must be filled for multiple-choice question.")
            if input.text or input.option_id:
                raise ValidationError("Only select options should be filled for multiple-choice questions.")

        # Create the answer
        answer = Answer(user=user, question=question, form=form)

        # Add the respective answer based on the question type
        if input.text:
            answer.text = input.text
        elif input.option_id:
            answer.option = Option.objects.get(pk=input.option_id)
        elif input.select_ids:
            options = Option.objects.filter(pk__in=input.select_ids)
            answer.save()
            answer.select.set(options)

        answer.save()
        return SubmitAnswerMutation(answer=answer)




# Main Schema with Mutation
class Mutation(graphene.ObjectType):
    submit_answer = SubmitAnswerMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)