from flask import Flask, render_template, flash, request, url_for, redirect, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from Models._user import User, Budget, Category, Expenditure, Feedback, db, connect_to_db
from Forms.forms import RegistrationForm, LoginForm
from passlib.hash import sha256_crypt
from functools import wraps
import gc, os
import datetime
import smtplib
from random import choice
from calendar import HTMLCalendar
from content_manager import CategoriesText
import pygal
from datetime import datetime as dt
import numpy as np
import pandas_datareader.data as web
from fbprophet import Prophet
from pathlib import Path
import os.path
import csv
from itertools import zip_longest
import pickle
import requests

#url = "https://www.fast2sms.com/dev/bulk"
app = Flask(__name__)
conn = 'sqlite:///'+ os.path.abspath(os.getcwd())+"/DataBases/test.db"
admin = Admin(app,name='Admin')
model1 = pickle.load(open('Models/total.pkl','rb'))
model2 = pickle.load(open('Models/food.pkl','rb'))
model3 = pickle.load(open('Models/travel.pkl','rb'))
model4 = pickle.load(open('Models/clothing.pkl','rb'))
model5 = pickle.load(open('Models/entertainment.pkl','rb'))
model6 = pickle.load(open('Models/onlineshopping.pkl','rb'))
model7 = pickle.load(open('Models/electricity.pkl','rb'))
model8 = pickle.load(open('Models/waterbill.pkl','rb'))
model9 = pickle.load(open('Models/gas.pkl','rb'))
model10 = pickle.load(open('Models/groceries.pkl','rb'))

connect_to_db(app,conn)
EMAIL_ADDRESS = "financialadvisor20113@gmail.com"
EMAIL_PASSWORD = "finaadvi"
app.config['SECRET_KEY'] = os.urandom(24)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Feedback, db.session))
admin.add_view(ModelView(Expenditure, db.session))

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('You need to login first!', "warning")
            return redirect(url_for('login_page'))
    return wrap

def already_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            flash("You are already logged in!", "success")
            return redirect(url_for('dashboard'))
        else:
            return f(*args, **kwargs)
    return wrap

def verify(_username, _password):
    if User.query.filter_by(username=_username).first() is None:
        flash("No such user found with this username", "warning")
        return False
    if not sha256_crypt.verify(_password, User.query.filter_by(username=_username).first().password):
        flash("Invalid Credentials, password isn't correct!", "danger")
        return False
    return True

@app.route('/register/', methods=['GET','POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == 'POST':
            _username = request.form['username']
            _email = request.form['email']
            _password = sha256_crypt.encrypt(str(form.password.data))
            user = User(username = _username, email = _email, password = _password)
            db.create_all()
            if User.query.filter_by(username=_username).first() is not None:
                flash('User Already registered with username {}'.format(User.query.filter_by(username=_username).first().username), "warning")
                return render_template('register.html', form=form)
            if User.query.filter_by(email=_email).first() is not None:
                flash('Email is already registered with us {}'.format(User.query.filter_by(email=_email).first().username), "warning")
                return render_template('register.html', form=form)
            flash("Thank you for registering!", "success")
            db.session.add(user)
            db.session.commit()
            db.session.close()
            gc.collect()
            session['logged_in'] = True
            session['username'] = _username
            session.modified = True
            return redirect(url_for('dashboard'))
        return render_template('register.html', form=form)
    except Exception as e:
        return render_template('error.html',e=e)

@app.route('/login/', methods=['GET','POST'])
@already_logged_in
def login_page():
    try:

        form = LoginForm(request.form)
        if request.method == 'POST':

            _username = request.form['username']
            _password = request.form['password']


            if verify(_username, _password) is False:
                return render_template('login.html', form=form)
            session['logged_in'] = True
            session['username'] = _username
            gc.collect()
            return redirect(url_for('dashboard'))

        return render_template('login.html', form=form)


    except Exception as e:
        return render_template('error.html',e=e)

@app.route('/forget_password/', methods=['GET', 'POST'])
def forget_password():
    _email = None
    try:
        if request.method=="POST":
            if request.form['submit'] == "Send Email":
                _email = request.form['email']
                if User.query.filter_by(email=_email).first() is None:
                    flash('Email is not registered with us', "danger")
                    _email = None
                else:
                    session['username'] = User.query.filter_by(email=_email).first().username
                    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                        smtp.ehlo()
                        smtp.starttls()
                        smtp.ehlo()
                        smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
                        secret_key = choice(("556257", "787637", "768686", "278672", "879745", "876876", "168373", "365262", "876721", "218982"))
                        session['otp'] = secret_key
                        session.modified = True
                        subject ='Financial Advisor Forget Password!! !'
                        body = "Your One Time password: {} \n Valid till half an hour from the generation of the OTP.".format(secret_key)
                        msg=f'subject: {subject}\n\n{body}'
                        smtp.sendmail(EMAIL_ADDRESS,_email, msg)
                        flash("Mail Sent!", "success")
                return render_template('forget_password.html')
            if request.form['submit'] == "Verify OTP":
                otp = request.form['otp']
                if 'username' in session:
                    if otp == session['otp']:
                        session['logged_in'] = True
                        return redirect(url_for('dashboard'))
                    else:
                        flash("OTP is incorrect. Try again!", "warning")
                        return render_template('forget_password.html')
                else:
                    flash("First enter email!")
                    return render_template('forget_password.html')
        else:
            return render_template('forget_password.html')
    except Exception as e:
            return render_template('error.html', e=e)


@app.route('/', methods=['GET','POST'])
def main():
    return render_template('main.html')

CATS = CategoriesText()

def initialize_categories():
    if Category.query.first() == None:

        categories_daily = ['Food', 'Travel', 'Clothing', 'Entertainment', 'Online Shopping']
        categories_monthly = ['Electricity Bill', 'Water Bill', 'Gas', 'Groceries']
        for cat in categories_daily:
            category_obj = Category(category=cat, category_daily=True, category_primary=True)
            db.session.add(category_obj)

        for cat in categories_monthly:
            category_obj = Category(category=cat, category_daily=False, category_primary=True)
            db.session.add(category_obj)

        db.session.commit()
        db.session.close()
        gc.collect()
        return True
    return False

def pie_chart(_categories, _values, _title='Expenditure'):
    pie_chart = pygal.Pie(width=800, height=400)
    pie_chart.title = _title
    for cat, val in zip(_categories, _values):
        pie_chart.add(cat, val)
    return pie_chart.render_data_uri()

def gauge_chart(title_list, val_list, max_valList):

    gauge = pygal.SolidGauge(
    half_pie=True, inner_radius=0.70,
    style=pygal.style.styles['default'](value_font_size=10))

    percent_formatter = lambda x: '{:.10g}%'.format(x)
    rupees_formatter = lambda x: '{:.10g} Rs'.format(x)
    gauge.value_formatter = rupees_formatter

    for title, val, max_val in zip(title_list, val_list, max_valList):
        if max_val == 0:
            max_val = 1
        gauge.add(title, [{'value': int(val), 'max_value': int(max_val)}])

    return gauge.render_data_uri()

def convert_toPercent(_list):
    ''' accepts a list and returns the list '''
    a = sum(_list)
    _new_list = []
    if a != 0:
        for i in _list:
            _new_list.append((i/a)*100)
        return _new_list
    return _list

def calculate_expenditure(category_id, userid, today= True):
    sum = 0
    if today:
        for obj in Expenditure.query.filter_by(expenditure_userid= userid).all():
            if obj.category_id == category_id and obj.date_of_expenditure.day == dt.today().day:
                sum += obj.spent
        return sum
    else:
        for obj in Expenditure.query.filter_by(expenditure_userid= userid).all():
            if obj.date_of_expenditure.month == dt.today().month and obj.category_id == category_id:
                sum += obj.spent
        return sum

def calculate_expenditureBudget_month(userid, month):
    sum_expense = 0
    sum_budget = 0
    for obj in Expenditure.query.filter_by(expenditure_userid= userid).all():
        if obj.date_of_expenditure.month == month:
            sum_expense += obj.spent
    for obj in Budget.query.filter_by(budget_userid= userid).all():
        if obj.budget_year == dt.today().year and obj.budget_month == month:
            sum_budget += obj.budget_amount
    return sum_expense, sum_budget

@app.route('/dashboard/',methods=['GET','POST'])
@login_required
def dashboard():
    html_cal = HTMLCalendar()
    t = dt.today()
    html_code =  html_cal.formatmonth(dt.today().year,dt.today().month, True)
    html_code =  html_code.replace('>%i<'%t.day, ' bgcolor="#9124a3" style="color:white;border-radius:10px" data-toggle="tooltip" title="Today"><b>%i</b><'%t.day)
    username = session['username']
    user_email = User.query.filter_by(username=username).first().email
    user_id = User.query.filter_by(username=username).first().id
    all_expenditure = Expenditure.query.filter_by(expenditure_userid=user_id).all()
    daily_cats = Category.query.filter_by(category_daily=True).all()
    pie_data = [pie_chart([cat for cat in CATS['Daily'] + CATS['Monthly']], convert_toPercent([calculate_expenditure(category_object.id, userid=User.query.filter_by(username=username).first().id, today= False) for category_object in Category.query.all()]), "My Expenditure Distribution this Month."),
                pie_chart([cat for cat in CATS['Daily']], convert_toPercent([calculate_expenditure(category_object.id, userid=User.query.filter_by(username=username).first().id, today= True) for category_object in Category.query.all()]) , "My Expenditure Distribution today!")]
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    l = [calculate_expenditureBudget_month(userid=User.query.filter_by(username=username).first().id, month = month) for month in range(1,13)]
    exp, budg =  zip(*l)
    gauge_data = gauge_chart(['{}{}'.format(a,b) for a, b in zip(months,[' Expenses']*12)], exp, budg)

    _budg = budg[dt.today().month - 1]
    _exp = exp[dt.today().month - 1]
    if _budg > 1:
        if _exp > _budg:
#            payload = "sender_id=FSTSMS&message=You have exceeded your budget limit this month&language=english&route=p&numbers=9408905901"
#            headers = {
#            'authorization': "TePMhjXU8qBE6VwmknOvugLYro9IbxDGAlyfFiZcWN3SKJ74Haw1bteaQMPBHIy8Rjohdi275vJrNku4",
#            'Content-Type': "application/x-www-form-urlencoded",
#            'Cache-Control': "no-cache",
#            }
#            response = requests.request("POST", url, data=payload, headers=headers)
#            print(response.text)
#            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#                smtp.ehlo()
#                smtp.starttls()
#                smtp.ehlo()
#                smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
#                subject ='Financial Advisor'
#                body = "You have exceeded your budget limit this month by {} Rs.".format(_exp - _budg)
#                msg=f'subject: {subject}\n\n{body}'
#                smtp.sendmail(EMAIL_ADDRESS, user_email, msg)
            flash("You have exceeded your budget limit this month by {} Rs.".format(_exp - _budg),"danger")

        elif _exp == _budg:
#            payload = "sender_id=FSTSMS&message=Expenses equalled to budget this month, time to stop spending&language=english&route=p&numbers=9408905901"
#            headers = {
#            'authorization': "TePMhjXU8qBE6VwmknOvugLYro9IbxDGAlyfFiZcWN3SKJ74Haw1bteaQMPBHIy8Rjohdi275vJrNku4",
#            'Content-Type': "application/x-www-form-urlencoded",
#            'Cache-Control': "no-cache",
#            }
#            response = requests.request("POST", url, data=payload, headers=headers)
#            print(response.text)
#            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#                smtp.ehlo()
#                smtp.starttls()
#                smtp.ehlo()
#                smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
#                subject ='Financial Advisor'
#                body = "Expenses equalled to budget this month, time to stop spending"
#                msg=f'subject: {subject}\n\n{body}'
#                smtp.sendmail(EMAIL_ADDRESS, user_email, msg)
            flash("Expenses equalled to budget this month, time to stop spending","warning")
        else:
#            payload = "sender_id=FSTSMS&message=Keep spending&language=english&route=p&numbers=7817058927"
#            headers = {
#            'authorization': "TePMhjXU8qBE6VwmknOvugLYro9IbxDGAlyfFiZcWN3SKJ74Haw1bteaQMPBHIy8Rjohdi275vJrNku4",
#            'Content-Type': "application/x-www-form-urlencoded",
#            'Cache-Control': "no-cache",
#            }
#            response = requests.request("POST", url, data=payload, headers=headers)
#            print(response.text)
#            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#                smtp.ehlo()
#                smtp.starttls()
#                smtp.ehlo()
#                smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
#                subject ='Financial Advisor'
#                body = "Keep spending, you have {} Rs. to spend".format(_budg - _exp)
#                msg=f'subject: {subject}\n\n{body}'
#                smtp.sendmail(EMAIL_ADDRESS, user_email, msg)
            flash("Keep spending, you have {} Rs. to spend".format(_budg - _exp),"success")

    try:
        username = session['username']
        user_id = User.query.filter_by(username=username).first().id
        all_expenditure = Expenditure.query.filter_by(expenditure_userid=user_id).all()

        if request.method == 'POST':
            initialize_categories()
            username = session['username']
            if request.form['submit'] == "Set Password":
                new_password = request.form['NewPassword']
                new_password = sha256_crypt.encrypt(str(new_password))
                User.query.filter_by(username = username).first().password = new_password
                db.session.commit()
                db.session.close()
                session.clear()
                gc.collect()
                with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
                    subject ='Financial Advisor'
                    body = "Password Changed"
                    msg=f'subject: {subject}\n\n{body}'
                    smtp.sendmail(EMAIL_ADDRESS, user_email, msg)
                flash("Password Changed!", "success")
                flash("Login Again!")
                return redirect(url_for('login_page'))
            if request.form['submit'] == 'Save Email':
                new_email = request.form['email']
                User.query.filter_by(username = username).first().email = new_email
                db.session.commit()
                db.session.close()
                gc.collect()
                flash("Email changed", "success")
                return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'aHome', isDaily=True, pie_data = pie_data, gauge_data = gauge_data, user_email = user_email)

            if request.form['submit'] == "Set Budget":
                _budget_userid = User.query.filter_by(username = username).first().id
                flag = 0
                for obj in Budget.query.filter_by(budget_userid= _budget_userid).all():
                    if obj.budget_year == dt.today().year and obj.budget_month == dt.today().month:
#                        payload = "sender_id=FSTSMS&message=Budget successfully changed for this month&language=english&route=p&numbers=7817058927"
#                        headers = {
#                        'authorization': "TePMhjXU8qBE6VwmknOvugLYro9IbxDGAlyfFiZcWN3SKJ74Haw1bteaQMPBHIy8Rjohdi275vJrNku4",
#                        'Content-Type': "application/x-www-form-urlencoded",
#                        'Cache-Control': "no-cache",
#                        }
#                        response = requests.request("POST", url, data=payload, headers=headers)
#                        print(response.text)
#                        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#                            smtp.ehlo()
#                            smtp.starttls()
#                            smtp.ehlo()
#                            smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
#                            subject ='Financial Advisor'
#                            body = ("Budget successfully changed for this month! from {} to {}".format(obj.budget_amount , request.form['amount'], ))
#                            msg=f'subject: {subject}\n\n{body}'
#                            smtp.sendmail(EMAIL_ADDRESS, user_email, msg)
                        flash("Budget successfully changed for this month! from {} to {}".format(obj.budget_amount , request.form['amount'], ), "success")
                        obj.budget_amount = request.form['amount']
                        db.session.commit()
                        db.session.close()
                        gc.collect()
                        flag = 1
                if flag == 0:
                    _budget_amount = request.form['amount']
                    _budget_month = dt.today().month
                    _budget_year = dt.today().year
                    budget_object = Budget(budget_userid = _budget_userid, budget_year = _budget_year, budget_month = _budget_month,  budget_amount = _budget_amount)
                    db.session.add(budget_object)
                    db.session.commit()
                    session['current_budget_id'] = budget_object.id
                    db.session.close()
                    gc.collect()
#                    payload = "sender_id=FSTSMS&message=Budget Set&language=english&route=p&numbers=7817058927"
#                    headers = {
#                    'authorization': "TePMhjXU8qBE6VwmknOvugLYro9IbxDGAlyfFiZcWN3SKJ74Haw1bteaQMPBHIy8Rjohdi275vJrNku4",
#                    'Content-Type': "application/x-www-form-urlencoded",
#                    'Cache-Control': "no-cache",
#                    }
#                    response = requests.request("POST", url, data=payload, headers=headers)
#                    print(response.text)
                    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                        smtp.ehlo()
                        smtp.starttls()
                        smtp.ehlo()
                        smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
                        subject ='Financial Advisor'
                        body = "Budget Set!"
                        msg=f'subject: {subject}\n\n{body}'
                        smtp.sendmail(EMAIL_ADDRESS, user_email, msg)
                        smtp.ehlo()
                    flash("Budget Set!", "success")

                l = [calculate_expenditureBudget_month(userid=User.query.filter_by(username=username).first().id, month = month) for month in range(1,13)]
                exp, budg =  zip(*l)
                gauge_data = gauge_chart(['{}{}'.format(a,b) for a, b in zip(months,[' Expenses']*12)], exp, budg)

                return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'aHome', isDaily=True, pie_data = pie_data, gauge_data = gauge_data, user_email = user_email)

            if request.form['submit'] == "predict":
                food = request.form.get('food')
                travel = request.form.get('travel')
                clothing = request.form.get('clothing')
                entertainment = request.form.get('entertainment')
                onlineshopping = request.form.get('onlineshopping')
                electricity = request.form.get('electricity')
                waterbill = request.form.get('waterbill')
                gas = request.form.get('gas')
                groceries = request.form.get('groceries')
                total = (int(food) + int(travel) + int(clothing) + int(entertainment) + int(onlineshopping) + int(electricity) + int(waterbill) + int(gas) + int(groceries))
                food = int(food)
                travel = int(travel)
                clothing = int(clothing)
                entertainment = int(entertainment)
                onlineshopping = int(onlineshopping)
                electricity = int(electricity)
                waterbill = int(waterbill)
                gas = int(gas)
                groceries = int(groceries)
                fo = int(food)
                tr = int(travel)
                cl = int(clothing)
                en = int(entertainment)
                on = int(onlineshopping)
                el = int(electricity)
                wa = int(waterbill)
                ga = int(gas)
                gr = int(groceries) 
                prediction2 = model2.predict([[food]])
                prediction3 = model3.predict([[travel]])
                prediction4 = model4.predict([[clothing]])
                prediction5 = model5.predict([[entertainment]])
                prediction6 = model6.predict([[onlineshopping]])
                prediction7 = model7.predict([[electricity]])
                prediction8 = model8.predict([[waterbill]])
                prediction9 = model9.predict([[gas]])
                prediction10 = model10.predict([[groceries]])
                food_ = int(prediction2[0])
                travel_ = int(prediction3[0])
                clothing_ = int(prediction4[0])
                entertainment_ = int(prediction5[0])
                onlineshopping_ = int(prediction6[0])
                electricity_ = int(prediction7[0])
                waterbill_ = int(prediction8[0])
                gas_ = int(prediction9[0])
                groceries_ = int(prediction10[0])
                total_ = food_+ travel_ + clothing_ + entertainment_ + onlineshopping_ + electricity_ + waterbill_ + gas_ + groceries_
                saving = total - total_
                return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'atable',food=food_,travel=travel_,clothing=clothing_,entertainment=entertainment_,onlineshopping=onlineshopping_,electricity=electricity_,waterbill=waterbill_,gas=gas_,groceries=groceries_,fo=food,tr=travel,cl=clothing,en=entertainment,on=onlineshopping,el=electricity,wa=waterbill,ga=gas,gr=groceries,total=total,total_=total_,saving=saving)

                username = session['username']
                tmp = Path("static/prophet.png")
                tmp_csv = Path("static/numbers.csv")
                if tmp.is_file():
                    os.remove(tmp)
                if tmp_csv.is_file():
                    os.remove(tmp_csv)
                return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'smtable')

            for key in CATS.keys():
                for cat in CATS[key]:
                    if request.form['submit'] == "Set {} amount".format(cat):
                        _expenditure_userid = User.query.filter_by(username = username).first().id
                        _spent = request.form['amount']
                        _where_spent = request.form['location']
                        _category_id = Category.query.filter_by(category = cat).first().id
                        _category_name = Category.query.filter_by(category = cat).first().category
                        _date_of_expenditure = dt.today()
                        _description = request.form['comment']
                        expenditure_object = Expenditure(expenditure_userid = _expenditure_userid, spent = _spent, where_spent= _where_spent, category_id = _category_id,  date_of_expenditure = _date_of_expenditure, description = _description, category_name = _category_name)
                        db.session.add(expenditure_object)
                        db.session.commit()
                        db.session.close()
                        gc.collect()
                        return redirect('/dashboard')
#                        payload = "sender_id=FSTSMS&message=Expenditure recorded&language=english&route=p&numbers=7817058927"
#                        headers = {
#                        'authorization': "TePMhjXU8qBE6VwmknOvugLYro9IbxDGAlyfFiZcWN3SKJ74Haw1bteaQMPBHIy8Rjohdi275vJrNku4",
#                        'Content-Type': "application/x-www-form-urlencoded",
#                        'Cache-Control': "no-cache",
#                        }
#                        response = requests.request("POST", url, data=payload, headers=headers)
#                        print(response.text)
#                        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#                            smtp.ehlo()
#                            smtp.starttls()
#                            smtp.ehlo()
#                            smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
#                            subject ='Financial Advisor'
#                            body = "Expenditure recorded of {}!".format(cat)
#                            msg=f'subject: {subject}\n\n{body}'
#                            smtp.sendmail(EMAIL_ADDRESS, user_email, msg)
                        flash("Expenditure recorded of {}!".format(cat),"success")

                        pie_data = [pie_chart([cat for cat in CATS['Daily'] + CATS['Monthly']], convert_toPercent([calculate_expenditure(category_object.id, userid=User.query.filter_by(username=username).first().id, today= False) for category_object in Category.query.all()]), "My Expenditure Distribution this Month."),
                                    pie_chart([cat for cat in CATS['Daily']], convert_toPercent([calculate_expenditure(category_object.id, userid=User.query.filter_by(username=username).first().id, today= True) for category_object in Category.query.all()]) , "My Expenditure Distribution today!")]

                        l = [calculate_expenditureBudget_month(userid=User.query.filter_by(username=username).first().id, month = month) for month in range(1,13)]
                        exp, budg =  zip(*l)
                        gauge_data = gauge_chart(['{}{}'.format(a,b) for a, b in zip(months,[' Expenses']*12)], exp, budg)

                        if Category.query.filter_by(category = cat).first().category_daily == True:
                            return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'expense', isDaily=True, pie_data = pie_data, gauge_data = gauge_data, user_email = user_email)
                        else:
                            return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'expense', isDaily=False, pie_data = pie_data, gauge_data = gauge_data, user_email = user_email)


            return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'aHome',expenditures=all_expenditure)
        else:
            return render_template('dashboard.html',CATS = CATS, html_code = html_code, active_tab = 'aHome', pie_data = pie_data, gauge_data = gauge_data, user_email = user_email,expenditures=all_expenditure)
    except Exception as e:
        return render_template('error.html',e=e)

@app.route('/expenditure_table/exdelete/<int:id>')
def exdelete(id):
    expenditure = Expenditure.query.get_or_404(id)
    db.session.delete(expenditure)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/logout/')
@login_required
def logout():
    flash("You have been logged out!", "success")
    session.clear()
    gc.collect()
    return redirect(url_for('main'))

@app.errorhandler(500)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', e=e)

@app.route('/user')
def user():
    return render_template('Admin/user.html')

@app.route('/tables', methods=['GET','POST'])
def tables():
    all_user = User.query.all()
    return render_template('Admin/tables.html',users=all_user)

@app.route('/tables/delete/<int:id>')
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("Data is Deleted")
    return redirect('/tables')

@app.route('/tables/edit/<int:id>' , methods = ['GET', 'POST'])
def edit(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST' :
        user.username = request.form['username']
        user.email = request.form['email']
        user.password = sha256_crypt.encrypt(str(request.form['password']))
        db.session.commit()
        flash("Data is Updated")
        return redirect('/tables')
    else :
        return render_template('Admin/edit.html', user=user)

@app.route('/tables/add/', methods=['GET','POST'])
def add_user():
    try:
        form = RegistrationForm(request.form)
        if request.method == 'POST':
            _username = request.form['username']
            _email = request.form['email']
            _password = sha256_crypt.encrypt(str(form.password.data))
            user = User(username = _username, email = _email, password = _password)
            db.create_all()
            if User.query.filter_by(username=_username).first() is not None:
                flash('User Already registered with username {}'.format(User.query.filter_by(username=_username).first().username), "warning")
                return redirect(url_for('tables'))
            if User.query.filter_by(email=_email).first() is not None:
                flash('Email is already registered with us {}'.format(User.query.filter_by(email=_email).first().username), "warning")
                return redirect(url_for('tables'))
            db.session.add(user)
            db.session.commit()
            db.session.close()
            gc.collect()
            session['logged_in'] = True
            session['username'] = _username
            session.modified = True
            flash("User is Added",_username)
            return redirect(url_for('tables'))
        return render_template('Admin/add.html', form=form)
    except Exception as e:
        return render_template('error.html',e=e)

#@app.route('/userpro', methods=['GET','POST'])
#def userpro():
#    try:
#        form = RegistrationForm(request.form)
#        if request.method == 'POST':
#            user.username = request.form['username']
#            user.email = request.form['email']
#            user.password = sha256_crypt.encrypt(str(request.form['password']))
#            db.session.commit()
#            flash("Data is Updated")
#            return redirect('/userpro')
#        return render_template('userpro.html', form=form)
#    except Exception as e:
#        return render_template('error.html',e=e)
#
@app.route('/feedback_page/', methods=['GET','POST'])
def feedback_page():
    try:
        if request.method == 'POST':
            _feedbackname = request.form['feedback_name']
            _feedbackemail = request.form['feedback_email']
            _feedbacksub = request.form['feedback_subject']
            _feedbackmsg = request.form['feedback_message']
            feedback = Feedback(feedback_name = _feedbackname, feedback_email = _feedbackemail, feedback_subject = _feedbacksub, feedback_message =  _feedbackmsg)
            db.create_all()
            db.session.add(feedback)
            db.session.commit()
            db.session.close()
            gc.collect()
            return render_template('feedback.html')
    except Exception as e:
        return render_template('error.html',e=e)

@app.route('/feedback_table')
def feedback_table():
    all_feedback = Feedback.query.all()
    return render_template('Admin/feedback_table.html', feedbacks=all_feedback)

#@app.route('/feedback_table/fdelete/<int:id>')
#def fdelete(id):
#    feedbacks = Feedback.query.get_or_404(id)
#    db.session.delete(feedbacks)
#    db.session.commit()
#    flash("Data is Deleted")
#    return redirect('/feedback_table')

@app.route('/feedback_table/fdelete/<int:id>')
def fdelete(id):
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    flash("Data is Deleted")
    return redirect('/feedback_table')

@app.route('/Adashboard')
def Adashboard():
    flash("HII, Welcome to Financial Advisor")
    return render_template('Admin/Adashboard.html')

@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['username']!= 'Admin123' or request.form['password']!= 'Admin123':
            flash("Invalid Credentials, Please try again","warning")
        else:
            return redirect(url_for('Adashboard'))
    return render_template('Admin/adminlogin.html')


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response



def yahoo_stocks(symbol, start, end):
    return web.DataReader(symbol, 'yahoo', start, end)

def get_historical_stock_price(stock):
    print ("Getting historical stock prices for stock ", stock)

    startDate = datetime.datetime(2010, 1, 4)
    endDate = datetime.datetime(2020, 6, 28)
    stockData = yahoo_stocks(stock, startDate, endDate)
    return stockData

@app.route("/plot" , methods = ['POST', 'GET'] )
def main1():
    if request.method == 'POST':
        stock = request.form['companyname']
        df_whole = get_historical_stock_price(stock)

        df = df_whole.filter(['Close'])

        df['ds'] = df.index
        df['y'] = np.log(df['Close'])
        original_end = df['Close'][-1]

        model = Prophet()
        model.fit(df)
        num_days = 10
        future = model.make_future_dataframe(periods=num_days)
        forecast = model.predict(future)

        print (forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
        df.set_index('ds', inplace=True)
        forecast.set_index('ds', inplace=True)

        viz_df = df.join(forecast[['yhat', 'yhat_lower','yhat_upper']], how = 'outer')
        viz_df['yhat_scaled'] = np.exp(viz_df['yhat'])
        close_data = viz_df.Close
        forecasted_data = viz_df.yhat_scaled
        date = future['ds']
        #date = viz_df.index[-plot_num:-1]
        forecast_start = forecasted_data[-num_days]

        d = [date, close_data, forecasted_data]
        export_data = zip_longest(*d, fillvalue = '')
        with open('static/numbers.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(("Date", "Actual", "Forecasted"))
            wr.writerows(export_data)
        myfile.close()

        return render_template("plot.html", original = round(original_end,2), forecast = round(forecast_start,2), stock_tinker = stock.upper())

if __name__ == "__main__":
    db.create_all()
    app.run()
