import datetime
from api.models.__init__ import db



class UserAccess(db.Model):
    __tablename__ = "user_acess"
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username        = db.Column(db.String(80), nullable=False)
    token           = db.Column(db.Text, nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Username {self.username}'