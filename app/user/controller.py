from flask import Blueprint, g, jsonify, request

from app.user.model import User
from app.user.schema import UserSchema
from app.route_guard import auth_required

bp = Blueprint("user", __name__)


@bp.post("/login")
def login():
    data = request.json

    email = data.get("email")
    user = User.get_by_email(email)

    if user is None:
        return jsonify({"message": "User not found"}), 404
    if not user.check_password(data.get("password")):
        return jsonify({"message": "Wrong password"}), 401
    # generate token
    token = user.generate_token()
    return jsonify({"token": token, "user": UserSchema().dump(user)}), 200


@bp.patch("/reset-password")
@auth_required()
def reset_password():
    new_password = request.json.get("password")
    if not new_password:
        return jsonify({"message": "Password is required"}), 400
    elif len(new_password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    g.user.reset_password(new_password)
    return jsonify({"message": "Password updated successfully"}), 200


@bp.patch("/update-profile")
@auth_required()
def update_profile():
    print("ran")
    new_name = request.json.get("name")
    new_about = request.json.get("about")

    if not new_name and not new_about:
        return jsonify({"message": "No changes provided"}), 400
    user = (
        g.user
    )  # Get the authenticated user from the request context (assuming @auth_required sets it)
    print(user)
    updated = user.update(new_name, new_about)
    if updated:
        return (
            jsonify(
                {
                    "message": "Profile updated successfully",
                    "data": UserSchema().dump(user),
                }
            ),
            200,
        )
    return jsonify({"error": "error updating profile"}), 400


@bp.post("/register")
def register():
    data = request.json
    user = User.get_by_email(data.get("email"))
    if user is not None:
        return jsonify({"message": "User already exists"}), 400
    user = User.create(
        data.get("email"), data.get("password"), data.get("name"), data.get("about")
    )
    if user is not None:
        return jsonify({"message": "User created"}), 201
    return jsonify({"message": "User not created"}), 400
