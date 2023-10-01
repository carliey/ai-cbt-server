from flask import Blueprint
from app.route_guard import auth_required

from app.quiz.model import *
from app.quiz.schema import *

bp = Blueprint('quiz', __name__)

@bp.post('/quiz')
@auth_required()
def create_quiz():
    quiz = Quiz.create()
    return QuizSchema().dump(quiz), 201

@bp.get('/quiz/<int:id>')
@auth_required()
def get_quiz(id):
    quiz = Quiz.get_by_id(id)
    if quiz is None:
        return {'message': 'Quiz not found'}, 404
    return QuizSchema().dump(quiz), 200

@bp.patch('/quiz/<int:id>')
@auth_required()
def update_quiz(id):
    quiz = Quiz.get_by_id(id)
    if quiz is None:
        return {'message': 'Quiz not found'}, 404
    quiz.update()
    return QuizSchema().dump(quiz), 200

@bp.delete('/quiz/<int:id>')
@auth_required()
def delete_quiz(id):
    quiz = Quiz.get_by_id(id)
    if quiz is None:
        return {'message': 'Quiz not found'}, 404
    quiz.delete()
    return {'message': 'Quiz deleted successfully'}, 200

@bp.get('/quizs')
@auth_required()
def get_quizs():
    quizs = Quiz.get_all()
    return QuizSchema(many=True).dump(quizs), 200