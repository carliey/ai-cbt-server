from app.route_guard import auth_required
from flask import Blueprint, g, jsonify, request
from app.quiz.model import *
from app.quiz.schema import *

from helpers import document_helper

bp = Blueprint("quiz", __name__)


@bp.post("/quiz")
@auth_required()
def create_quiz():
    administrator_id = g.user.id
    title = request.json.get("title")
    questions = request.json.get("questions")
    participants = request.json.get("participants")
    date = request.json.get("date")
    duration = request.json.get("duration")
    instruction = request.json.get("instruction")
    description = request.json.get("description")

    quiz = Quiz.create(
        title, administrator_id, date, duration, instruction, description, questions
    )
    return QuizSchema().dump(quiz), 200


@bp.get("/quiz/<int:id>")
@auth_required()
def get_quiz(id):
    quiz = Quiz.get_by_id(id)
    if quiz is None:
        return {"message": "Quiz not found"}, 404
    return QuizSchema().dump(quiz), 200


@bp.patch("/quiz/<int:id>")
@auth_required()
def update_quiz(id):
    quiz = Quiz.get_by_id(id)
    if quiz is None:
        return {"message": "Quiz not found"}, 404
    quiz.update()
    return QuizSchema().dump(quiz), 200


@bp.delete("/quiz/<int:id>")
@auth_required()
def delete_quiz(id):
    quiz = Quiz.get_by_id(id)
    if quiz is None:
        return {"message": "Quiz not found"}, 404
    quiz.delete()
    return {"message": "Quiz deleted successfully"}, 200


@bp.get("/quizs")
@auth_required()
def get_quizs():
    quizs = Quiz.get_all()
    return QuizSchema(many=True).dump(quizs), 200


@bp.post("/extract-participants")
def upload_excel():
    if "excel" not in request.files:
        return jsonify({"error": "No file part"}), 400

    excel_file = request.files["excel"]

    if excel_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if excel_file and allowed_file(excel_file.filename):  # Define allowed_file function
        participants = document_helper.extract_participants_from_excel(excel_file)
        return jsonify(participants)
    else:
        return jsonify({"error": "Invalid file type"}), 400


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"xlsx", "xls"}
