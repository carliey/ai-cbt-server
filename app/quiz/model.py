from app import db
from app.user.model import User
import os


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(255), nullable=False)
    administrator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    administrator = db.relationship(
        "User",
        primaryjoin=administrator_id == User.id,
        backref=db.backref("quizzes", lazy="dynamic"),
    )
    questions = db.relationship(
        "Question", secondary="quiz_question", backref="question"
    )
    answers = db.relationship(
        "Quizanswer",
        primaryjoin="Quiz.id==Quizanswer.quiz_id",
        backref="quiz",
        lazy="dynamic",
    )
    participants = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    instruction = db.Column(db.String)
    description = db.Column(db.String)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return True

    def update(
        self,
        title=None,
        instruction=None,
        duration=None,
        description=None,
        date=None,
        questions=[],
    ):
        self.updated_at = db.func.now()
        self.title = title or self.name
        self.description = description or self.description
        self.instruction = instruction or self.instruction
        self.duration = duration or self.duration
        self.date = date or self.date
        db.session.commit()
        return True

    def add_participants_to_quiz(self, participants):
        participants_list = self.participants
        for participant in participants:
            # Check if the participant is not already added to the quiz by comparing 'id'
            if not any(p["id"] == participant["id"] for p in participants_list):
                participants_list.append(participant)

        # Update the participants list for the quiz
        self.participants = participants_list
        db.session.commit()

    def publish(self):
        if self.is_published:
            return False

        participants = self.participants
        quiz_url = (
            f"{os.environ['SITEURL']}/quiz/{self.id}"  # Replace with the actual URL
        )

        for participant in participants:
            email = participant["email"]
            fullname = participant["fullname"]

            # Customize your email subject and body as needed
            subject = f"Quiz Invitation for {self.name}"
            message = (
                f"Hi {fullname},\n\nYou have been invited to take part in the quiz: {self.name}. "
                f"Please click the following link to start the quiz: {quiz_url}\n\n"
                f"Best regards,\nYour Quiz Administrator"
            )

            # Send the email using your send_email_to_participant function
            # send_mail.delay(f"{self.title} | {self.administrator.name}", subject, message, email)
            print("send email to", email)

        self.is_published = True
        db.session.commit()
        return True

    def unpublish(self):
        self.is_published = False
        db.session.commit()
        return True

    def delete(self):
        self.is_deleted = True
        self.updated_at = db.func.now()
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, is_deleted=False).first()

    @classmethod
    def get_all(cls):
        return cls.query.filter_by(is_deleted=False).all()

    @classmethod
    def get_all_by_administrator_id(cls, administrator_id):
        quizzes = cls.query.filter_by(administrator_id=administrator_id).order_by(
            db.desc("created_at")
        )
        return quizzes

    @classmethod
    def create(
        cls,
        title,
        administrator_id,
        date,
        duration,
        instruction,
        description,
        questions: list = [],
    ):
        quiz = cls(
            title=title,
            administrator_id=administrator_id,
            date=date,
            duration=duration,
            instruction=instruction,
            description=description,
            questions=questions,
        )
        quiz.save()
        Question.add_to_quiz(quiz.id, questions)
        return quiz


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    options = db.relationship("Option")
    has_multi_answers = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()
        return True

    def update(self, text=None, options=[]):
        self.updated_at = db.func.now()
        self.text = text or self.text
        if self.text:
            for option in options:
                o = Option.get_by_id(option.get("id"))
                if o:
                    if option.get("option"):
                        o.update(option.get("option"), option.get("is_correct"))
                    else:
                        o.delete()
                else:
                    Option.create(
                        option.get("option"), self.id, option.get("is_correct")
                    )
        else:
            self.delete()
        db.session.commit()
        return True

    def delete(self):
        for option in self.options:
            option.delete()
        db.session.delete(self)
        db.session.commit()
        return True

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def create(cls, text):
        if text:
            question = cls(text=text)
            question.save()
            return question

    @classmethod
    def add_to_quiz(cls, quiz_id, questions: list = []):
        for question in questions:
            new_question = cls.create(question["question"], False)
            if new_question:
                answers = 0
                for option in question["options"]:
                    Option.create(
                        option["option"], new_question.id, option["is_correct"]
                    )
                    if option["is_correct"]:
                        answers += 1
                if answers > 1:
                    new_question.has_multi_answers = True
                    new_question.update()
                db.session.execute(
                    quiz_question.insert().values(
                        quiz_id=quiz_id, question_id=new_question.id
                    )
                )
        db.session.commit()
        return True


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return True

    def update(self, text=None, is_correct=None, question_id=None):
        self.updated_at = db.func.now()
        self.text = text or self.text
        self.is_correct = is_correct if is_correct != None else self.is_correct
        self.question_id = question_id or self.question_id
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        return True

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.query.filter(Option.id.in_(ids)).all()

    @classmethod
    def get_by_text(cls, text):
        return cls.query.filter(cls.text.like("%" + text + "%")).all()

    @classmethod
    def get_by_question_id(cls, question_id):
        return cls.query.filter_by(question_id=question_id).all()

    @classmethod
    def get_by_question_ids(cls, question_ids):
        return cls.query.filter(Option.question_id.in_(question_ids)).all()

    @classmethod
    def create(cls, text, question_id, is_correct):
        if text:
            option = cls(text=text, question_id=question_id, is_correct=is_correct)
            option.save()
            return option


quiz_question = db.Table(
    "quiz_question",
    db.Column("question_id", db.Integer, db.ForeignKey("question.id")),
    db.Column("quiz_id", db.Integer, db.ForeignKey("quiz.id")),
)


class Quizanswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"))
    participant_id = db.Column(db.Integer)
    participant = db.Column(db.Text)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))
    question = db.relationship(
        "Question", primaryjoin="Question.id==Quizanswer.question_id"
    )
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"))
    option = db.relationship("Option", primaryjoin="Option.id==Quizanswer.option_id")
    is_correct = db.Column(db.Boolean, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return True

    def update(self):
        self.updated_at = db.func.now()
        db.session.commit()
        return True

    def delete(self):
        db.session.delete(self)
        return True

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_quiz(cls, quiz):
        return cls.query.filter_by(quiz=quiz).all()

    @classmethod
    def get_by_participant(cls, participant_id):
        return cls.query.filter_by(participant_id=participant_id).all()

    @classmethod
    def create(cls, quiz_id, participant_id, question_id, option_id):
        answer = cls.get_by_participant(quiz_id, participant_id, question_id)
        if not answer:
            answer = cls(
                quiz_id=quiz_id, participant_id=participant_id, question_id=question_id
            )
            answer.save()
        option = Option.get_by_id(option_id)
        answer.option_id = option.id
        answer.is_correct = option.is_correct
        answer.update()
        return answer
