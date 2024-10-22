import graphene
from graphene_django import DjangoObjectType
from .models import Form, Process, Question, Answer, Option


class FormType(DjangoObjectType):
    class Meta:
        model = Form
        fields = ("id", "name", "category", "is_private", "processes")


class ProcessType(DjangoObjectType):
    class Meta:
        model = Process
        fields = (
            "id",
            "form",
            "category",
            "linear",
            "order",
            "is_private",
            "questions",
        )


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = ("id", "text", "type", "required", "order", "options")


class OptionType(DjangoObjectType):
    class Meta:
        model = Option
        fields = ("id", "text", "order")


class AnswerType(DjangoObjectType):
    class Meta:
        model = Answer
        fields = ("id", "question", "user", "text", "select", "option", "created_at")


class StartFormMutation(graphene.Mutation):
    class Arguments:
        form_id = graphene.ID(required=True)

    processes = graphene.List(ProcessType)
    question = graphene.Field(QuestionType)

    def mutate(self, info, form_id):
        user = info.context.user
        form = Form.objects.get(id=form_id, user=user)
        first_process = form.processes.order_by("order").first()

        if first_process.linear:
            first_question = first_process.questions.order_by("order").first()
            return StartFormMutation(question=first_question)
        else:
            return StartFormMutation(processes=form.processes.all())


class RecordAnswerMutation(graphene.Mutation):
    class Arguments:
        question_id = graphene.ID(required=True)
        answer_text = graphene.String(required=False)
        option_id = graphene.ID(required=False)
        option_ids = graphene.List(graphene.ID, required=False)  # For multiple select

    success = graphene.Boolean()

    def mutate(
        self, info, question_id, answer_text=None, option_id=None, option_ids=None
    ):
        user = info.context.user
        question = Question.objects.get(id=question_id)

        # Validate if the process is linear and check the sequence
        if question.process.linear:
            previous_questions = question.process.questions.filter(
                order__lt=question.order
            )
            for prev_q in previous_questions:
                if not Answer.objects.filter(question=prev_q, user=user).exists():
                    raise Exception("You must answer the previous question first.")

        # Record the answer based on the question type
        if question.type == 1:  # Text
            Answer.objects.create(question=question, user=user, text=answer_text)
        elif question.type == 2:  # Checkbox (multiple select)
            answer = Answer.objects.create(question=question, user=user)
            options = Option.objects.filter(id__in=option_ids)
            answer.select.set(options)
        elif question.type == 3:  # Test (single select)
            option = Option.objects.get(id=option_id)
            Answer.objects.create(question=question, user=user, option=option)

        return RecordAnswerMutation(success=True)


class Mutation(graphene.ObjectType):
    start_form = StartFormMutation.Field()
    record_answer = RecordAnswerMutation.Field()


class Query(graphene.ObjectType):
    forms = graphene.List(FormType)
    form = graphene.Field(FormType, id=graphene.ID(required=True))

    def resolve_forms(self, info):
        return Form.objects.all()

    def resolve_form(self, info, id):
        return Form.objects.get(id=id)


schema = graphene.Schema(query=Query, mutation=Mutation)
