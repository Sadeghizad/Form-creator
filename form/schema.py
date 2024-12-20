import graphene
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ValidationError
from .models import Form, Process, Question, Option, Answer
from report.models import UserViewForm, UserViewQuestion
from graphql_jwt.decorators import login_required
from django.core.cache import cache
import graphql_jwt


class OptionType(DjangoObjectType):
    class Meta:
        model = Option


class QuestionType(DjangoObjectType):
    options = graphene.List(OptionType)

    class Meta:
        model = Question

    def resolve_options(self, info):
        if self.order:
            return Option.objects.filter(id__in=self.order)
        return []


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

        for process_id in self.order:
            try:
                process = Process.objects.get(pk=process_id)
                questions = [Question.objects.get(id=q_id) for q_id in process.order]

                if self.linear:
                    answered_question_ids = Answer.objects.filter(
                        form=self, user=user, question__in=questions
                    ).values_list("question_id", flat=True)

                    unanswered_questions = [
                        q for q in questions if q.id not in answered_question_ids
                    ]

                    if unanswered_questions:
                        next_question = unanswered_questions[0]

                        UserViewQuestion.objects.get_or_create(
                            user=user, question=next_question
                        )
                        process.questions_to_show = [next_question]
                        processes_to_show.append(process)
                        break
                else:

                    for question in questions:
                        UserViewQuestion.objects.get_or_create(
                            user=user, question=question
                        )

                    process.questions_to_show = questions
                    processes_to_show.append(process)

            except Process.DoesNotExist:
                continue

        return processes_to_show


class Query(graphene.ObjectType):
    form = graphene.Field(
        FormType, form_id=graphene.ID(required=True), password=graphene.String()
    )
    previous_questions = graphene.List(QuestionType, form_id=graphene.ID(required=True))

    @login_required
    def resolve_form(self, info, form_id, password=None):
        try:
            form = Form.objects.get(pk=form_id)

            if form.is_private and form.password != password:
                raise ValidationError("Invalid password for the form.")

            UserViewForm.objects.get_or_create(user=info.context.user, form=form)

            info.context.form_instance = form
            # cached_form = cache.get(f"form_{form_id}")
            # if cached_form:
            #     return cached_form

            # cache.set(f"form_{form_id}", form, 300)
            return form

        except Form.DoesNotExist:
            raise ValidationError("Form not found.")

    @login_required
    def resolve_previous_questions(self, info, form_id):
        user = info.context.user

        try:
            form = Form.objects.get(pk=form_id)
        except Form.DoesNotExist:
            raise ValidationError("Form not found.")

        ordered_questions = []
        for process_id in form.order:
            try:
                process = Process.objects.get(pk=process_id)
                ordered_questions.extend(process.order)
            except Process.DoesNotExist:
                continue

        answered_question_ids = Answer.objects.filter(form=form, user=user).values_list(
            "question_id", flat=True
        )

        previous_questions = [
            Question.objects.get(pk=q_id)
            for q_id in ordered_questions
            if q_id in answered_question_ids
        ]
        return previous_questions


class AnswerInput(graphene.InputObjectType):
    question_id = graphene.ID(required=True)
    option_id = graphene.ID()
    select_ids = graphene.List(graphene.ID)
    text = graphene.String()
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

        try:
            question = Question.objects.get(pk=input.question_id)
        except Question.DoesNotExist:
            raise ValidationError("Question not found")

        try:
            form = Form.objects.get(pk=input.form_id)
        except Form.DoesNotExist:
            raise ValidationError("Form not found")

        ordered_questions = []
        for process_id in form.order:
            try:
                process = Process.objects.get(pk=process_id)
                ordered_questions.extend(process.order)
            except Process.DoesNotExist:
                continue

        if question.id not in ordered_questions:
            raise ValidationError(
                "Question not part of the ordered sequence in this form."
            )

        if form.linear:
            question_index = ordered_questions.index(question.id)
            previous_questions = Answer.objects.filter(
                form=form, user=user, question_id__in=ordered_questions[:question_index]
            ).count()

            if previous_questions < question_index:
                raise ValidationError("Answer previous questions in order first.")

        if question.type == 1:
            if not input.text:
                raise ValidationError("Text field must be filled for text question.")
            if input.option_id or input.select_ids:
                raise ValidationError(
                    "Only the text field should be filled for text questions."
                )
        elif question.type == 3:
            if not input.option_id:
                raise ValidationError(
                    "Option must be filled for single-choice question."
                )
            if input.text or input.select_ids:
                raise ValidationError(
                    "Only the option field should be filled for single-choice questions."
                )
        elif question.type == 2:
            if not input.select_ids:
                raise ValidationError(
                    "Select options must be filled for multiple-choice question."
                )
            if input.text or input.option_id:
                raise ValidationError(
                    "Only select options should be filled for multiple-choice questions."
                )

        answer, created = Answer.objects.update_or_create(
            user=user,
            question=question,
            form=form,
            defaults={
                "text": input.text,
                "option": (
                    Option.objects.get(pk=input.option_id) if input.option_id else None
                ),
            },
        )

        if input.select_ids:
            options = Option.objects.filter(pk__in=input.select_ids)
            answer.select.set(options)

        answer.save()
        return SubmitAnswerMutation(answer=answer)


class Mutation(graphene.ObjectType):
    submit_answer = SubmitAnswerMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
