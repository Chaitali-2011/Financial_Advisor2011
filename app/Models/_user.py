from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer,  autoincrement=True, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    registeron = db.Column(db.DateTime, nullable=False ,default=datetime.now)
    

def __repr__(self):
        return '<User {}>'.format(self.username)


class Category(db.Model):
    """ This is the category table """

    __tablename__ = "categories"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category = db.Column(db.String(64))
    category_daily = db.Column(db.Boolean, default=False)  # is it daily expense related, False implies, it can be both daily and monthly!?
    category_primary =  db.Column(db.Boolean, default=False)  # if not true, it means , this category is added explicitly by user!


class Budget(db.Model):
    """ This is the user's budget """

    __tablename__ = "budget"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # the data type of the budget should match the data type of the price
    budget_amount = db.Column(db.Numeric(15, 2))
    budget_userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    budget_month = db.Column(db.Integer) 
    budget_year = db.Column(db.Integer)

    user = db.relationship("User", backref=db.backref('budget'))

    def __repr__(self):
        """ Provide useful info """

        return "<Budget id=%s budget=%s budget_userid=%s budget_month=%s budget_year=%s>" % (
            self.id, self.budget_amount, self.budget_userid, self.budget_month, self.budget_year)


class Expenditure(db.Model):
    """ This contains expenditures """

    __tablename__ = "expenditures"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    spent = db.Column(db.Numeric(15, 2), default=0)
    date_of_expenditure = db.Column(db.DateTime)
    expenditure_userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    where_spent = db.Column(db.String(100))
    description = db.Column(db.UnicodeText)
    category_name = db.Column(db.String(64))
#    category_name = db.Column(db.String(64), db.ForeignKey('categories.category'))
    

    user = db.relationship("User", backref=db.backref('expenditures'))

    category = db.relationship("Category", backref=db.backref('expenditures'))
    
    def __repr__(self):
        return '<Expenditure {}>'.format(self.id)

class Feedback(db.Model):
    """ This contains feedbacks """

    __tablename__ = "feedbacks"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    feedback_name = db.Column(db.String(80), nullable=False)
    feedback_email = db.Column(db.String(120), nullable=False)
    feedback_subject = db.Column(db.String(80), nullable=False)
    feedback_message = db.Column(db.String(200), nullable=False)
    feedback_datetime = db.Column(db.DateTime, nullable=False ,default=datetime.now)
    
    
    
def connect_to_db(app, spent_database):
    """ Connect the database to our Flask app. """

    # Configure to use the database
    app.config['SQLALCHEMY_DATABASE_URI'] = spent_database
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app)
    
    
def __repr__(self):
    return '<Feedback {}>'.format(self.id)
