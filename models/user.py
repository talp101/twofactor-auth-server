# ourapp/models.py

from sqlalchemy.ext.hybrid import hybrid_property

from app import bcrypt, db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    _subject = db.Column(db.String(128))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext_password):
        self._password = bcrypt.generate_password_hash(plaintext_password.encode('utf-8'))

    @hybrid_property
    def subject(self):
        return self._password

    @subject.setter
    def _set_subject(self, plaintext_subject):
        self._subject = bcrypt.generate_password_hash(plaintext_subject.encode('utf-8'))

    def check_password_hash(self, plaintext_password):
        return bcrypt.check_password_hash(self._password, plaintext_password)

    def check_subject_hash(self, plaintext_subject):
        return bcrypt.check_password_hash(self._subject, plaintext_subject)
