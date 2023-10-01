from app import ma
from app.quiz.model import *


class QuizSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Quiz
        load_instance = True
        include_relationships = True

    questions = ma.Nested("QuestionSchema", many=True)
    answers = ma.Nested("QuizanswerSchema", many=True)


class PlainQuizSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Quiz

    questions = ma.Nested("PlainQuestionSchema", many=True)


# class QuizstatSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Quizstat
#         include_fk = True

#     obtainable_score = ma.Integer()
#     date = ma.DateTime()
#     name = ma.String()
#     type = ma.String()
#     average = ma.Float()
#     percentage = ma.Float()


# class QuizanswerSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Quizanswer


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        load_instance = True

    options = ma.Nested("OptionSchema", many=True)


class PlainQuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        load_instance = True

    options = ma.Nested("PlainOptionSchema", many=True)


class OptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Option
        load_instance = True
        include_relationships = True


class PlainOptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Option
        include_relationships = True
        exclude = ("is_correct",)
