from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import exc
import math
import sqlite3
import sympy as smp
from sympy import *
import time
from datetime import datetime
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Inventorydata(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Class = db.Column(db.String(2),nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Cost = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Inventorydata('{self.ID}', '{self.Name}', '{self.Quantity}', '{self.Cost}')"


class Homepagedata(db.Model):
    ID= db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100),nullable=False)   
    Email = db.Column(db.String(100),nullable=False)
    Subject = db.Column(db.String(100),nullable=False)
    
    def __repr__(self):
        return f"Homepagedata('{self.Name}','{self.Email}', '{self.Subject}')"


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class inventorypage(FlaskForm):
     Name = StringField('Part Number', validators=[DataRequired()])
     Class = StringField('Class',validators=[DataRequired()])
     Quantity = IntegerField("Quantity", validators=[DataRequired()])
     Cost = DecimalField("Cost",validators=[DataRequired()])
     Submit = SubmitField('Add')

class demandpage(FlaskForm):
     Class = StringField('Class of Inventory', validators=[DataRequired()])
     Demand = DecimalField("Demand Rate", validators=[DataRequired()])
     SetCost = DecimalField("Setup Cost",validators=[DataRequired()])
     HoldCost = DecimalField("Holding Cost",validators=[DataRequired()])
     Submit = SubmitField("Calculate")

class datainvf(FlaskForm):
    ID = StringField('Part Number')
    Class=StringField('Class')
    B1=SubmitField("Get Record")
    B2=SubmitField("Update Record")

class demandpage1(FlaskForm):
    Class = StringField('Class of Inventory', validators=[DataRequired()])
    Demand = DecimalField("Average Demand", validators=[DataRequired()])
    Lead =   IntegerField("Lead Time", validators=[DataRequired()])
    Stock =  DecimalField("Safety Stock", validators=[DataRequired()])
    Submit=  SubmitField("Calculate")

class updatepage(FlaskForm):
    Class = StringField('Class',validators=[DataRequired()])
    Quantity = IntegerField("Quantity", validators=[DataRequired()])
    Cost = DecimalField("Cost",validators=[DataRequired()])
    Submit = SubmitField('Add')

class variabledemand(FlaskForm):
    SetCost = DecimalField('Set-up Cost', validators=[DataRequired()])
    HoldingCost = DecimalField('Holding Cost', validators=[DataRequired()])
    a = DecimalField('Value of Parameter a', validators=[DataRequired()])
    b = DecimalField('Value of Parameter b', validators=[DataRequired()])
    c = DecimalField('Value of Parameter c', validators=[DataRequired()])
    Submit = SubmitField('Evaluate for the case')

class staticcase(FlaskForm):
    alpha = DecimalField('Alpha', validators=[DataRequired()])
    Submit = SubmitField('Calculate')

class expcase(FlaskForm):
    alpha = DecimalField('Alpha', validators=[DataRequired()])
    lambd = DecimalField('Value of Lambda', validators=[DataRequired()])
    Submit = SubmitField('Calculate')

@app.route("/")
@app.route("/home", methods=['GET','POST'])
def home():
    if request.method=="POST":
        Name = request.form['name']
        Email = request.form['email']
        Subject = request.form['subject']
        query = Homepagedata(Name=Name, Email=Email, Subject=Subject)
        try:
            db.session.add(query)
            db.session.commit()
        except:
            db.session.rollback()
            flash("Error", 'danger')
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/inventory", methods=['GET','POST'])
def inventory():
    form = inventorypage()
    if current_user.is_authenticated:
        if request.method=='POST':
            if form.validate_on_submit():
                Name = form.Name.data
                Class = form.Class.data
                Quantity = form.Quantity.data
                Cost = form.Cost.data
                inventory = Inventorydata(Name=form.Name.data, Quantity=form.Quantity.data, Cost = form.Cost.data, Class=form.Class.data)
                try:
                    db.session.add(inventory)
                    db.session.commit()
                    flash('Your Record has been added','success')
                except:
                     db.session.rollback()
                     flash('Error in Connection','danger')
            else:
                flash('Please check the entered information', 'danger')
    else:
        form1 = RegistrationForm()
        flash('Unauthorized access', 'danger')
        return render_template('register.html',form=form1)


    return render_template('inventory.html',form = form)
        


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route("/BOM")
def BOM():
    return render_template('BOM.html')
@app.route("/Report")
def report():
    return render_template('50113a02-9ea4-11eb-8b25-0cc47a792c0a_id_50113a02-9ea4-11eb-8b25-0cc47a792c0a.html')



@app.route("/Demand",methods=['GET','POST'])
def demand():
    if current_user.is_authenticated:
        if request.method=='POST':
            model=request.form['model']
            if model=='EOQ':
                return redirect(url_for("DemandEoq"))
            if model=='Fixed Order Quantity':
                return redirect(url_for("DemandFoq"))
    else:
        form1 = RegistrationForm()
        flash('Unauthorized access', 'danger')
        return render_template('register.html',form=form1)


    return render_template('Demand.html')

@app.route("/DemandEoq",methods = ['GET','POST'])
def DemandEoq():
    form = demandpage()
    if request.method=="POST":
        Class = form.Class.data
        Demand= form.Demand.data
        SetCost=form.SetCost.data
        HoldCost=form.HoldCost.data
        lot = math.sqrt((2*SetCost*Demand)/HoldCost)
        return render_template('DemandEoq.html',form=form,lot = lot)
    return render_template('DemandEoq.html', form=form)

@app.route("/DemandFoq",methods = ['GET','POST'])
def DemandFoq():
    form = demandpage1()
    if request.method=="POST":
        Class = form.Class.data
        Demand= form.Demand.data
        Lead=form.Lead.data
        Stock=form.Stock.data
        avg = Demand*Lead
        lot = avg + Stock
        return render_template('DemandFoq.html',form=form,lot = lot)
    return render_template('DemandFoq.html', form=form)

@app.route("/Database",methods = ['GET','POST'])
def datainv():
    form=datainvf()
    rows=[]
    if request.method=='POST':
        Part = form.ID.data
        Class = form.Class.data
        if Part=="":
            try:
                rows=Inventorydata.query.filter_by(Class=Class).all()
            except:
                flash("Connection Error",'danger')
        else:
            if request.form.get('Upd',None) == 'Update':
                flash("Update the details", 'danger')
                return redirect(url_for('updateform', part = Part))
            if request.form.get('Del',None) == 'Delete':
                Inventorydata.query.filter_by(Name = Part).delete()
                db.session.commit()
                flash(f'Record Deleted', 'danger')
            else:
                rows = Inventorydata.query.filter_by(Name=Part).all()
        if not rows:
            flash("NO RECORD FOUND",'danger')
    return render_template("view.html",form=form,rows = rows)

@app.route("/updateform/<part>", methods = ['GET','POST'])
def updateform(part):
    form = updatepage()
    if request.method=='POST':
        Class_form = form.Class.data
        Quantity_form = form.Quantity.data
        Cost_form = form.Cost.data
        try:
            record = Inventorydata.query.filter_by(Name=part).first()
            record.Class = Class_form
            record.Quantity=Quantity_form
            record.Cost = Cost_form
            db.session.commit()
            flash(f"Updated {part} Sucessfully",'success')
            return redirect(url_for("datainv"))
        except:
            db.session.rollback()
            flash("Failed to update", 'Danger')
    return render_template("update.html", form = form)

@app.route("/variabledeamand", methods = ['GET','POST'])
def stocastic():
    form=variabledemand()
    if current_user.is_authenticated:
        if request.method=='POST':
            demandtype=request.form['demandtype']
            setcost = form.SetCost.data
            holdcost = form.HoldingCost.data
            a = form.a.data
            b = form.b.data
            c = form.c.data
            if demandtype=='Static':
                return redirect(url_for("staticd", setcost = setcost, holdcost = holdcost, A=a, B=b, C=c))
            if demandtype=='Linear':
                return redirect(url_for("lineard", setcost = setcost, holdcost = holdcost, A=a, B=b, C=c))
            if demandtype=='Exp':
                return redirect(url_for("expd", setcost = setcost, holdcost = holdcost, A=a, B=b, C=c))

    else:
        form1 = RegistrationForm()
        flash('Unauthorized access', 'danger')
        return render_template('register.html',form=form1)
    return render_template('variabledemand.html', form = form)


def raphson(fnx,l):
    t1 = smp.symbols('t1')
    h = smp.diff(fnx,t1)
    l.append(1)
    l.append(1-fnx.subs(t1,1)/h.subs(t1,1))
    start = time.time()
    while(1):
        n = len(l)
        if round(l[n-1],4) == round(l[n-2], 4):
            break 
        l.append(l[n-1]-fnx.subs(t1,l[n-1])/h.subs(t1,l[n-1]))
        end = time.time()
        if end-start>5:
            print(end-start)
            break  

@app.route("/staticdemandcase/<setcost>/<holdcost>/<A>/<B>/<C>", methods=['GET', 'POST'])
def staticd(setcost, holdcost, A, B, C):
    form = staticcase()
    A = float(A)
    B = float(B)
    C = float(C)
    setcost = float(setcost)
    holdcost = float(holdcost)
    if request.method=='POST':
        Alpha = form.alpha.data
        Alpha = float(Alpha)
        a,b,c,alpha,t1 = smp.symbols('a b c alpha t1')
        t2 = ((a+(b-1)*alpha)/(c*alpha))*(1 - smp.exp(-c*t1))
        cs, ci = smp.symbols('cs ci')
        K = cs/(t1+t2) + (ci/(t1+t2))*((((a+(b-1)*alpha)/c)*(t1 + (smp.exp(-c*t1)-1)/c))+(alpha*t2**2)/2)
        K = K.subs(a,A).subs(b,B).subs(c,C).subs(alpha,Alpha).subs(cs,setcost).subs(ci,holdcost)
        h = smp.diff(K,t1)
        l = []
        raphson(h,l)
        n = len(l)
        finalt1 = l[n-1]
        t2 = t2.subs(t1,l[n-1]).subs(a,A).subs(alpha,Alpha).subs(b,B).subs(c,C)
        K = K.subs(t1,l[n-1])
        if K<0 or l[n-1]<0 or t2<0: 
            K = "No optimised solution"
            l[n-1] = "No optimized solution"
            t2 = "No optimised solution"
        return render_template("staticcase.html", form=form, t2=t2, K=K, t1 = l[n-1])

    return render_template('staticcase.html', form = form)

@app.route("/Expdemandcase/<setcost>/<holdcost>/<A>/<B>/<C>", methods=['GET', 'POST'])
def expd(setcost, holdcost, A, B, C):
    form = expcase()
    A = float(A)
    B = float(B)
    C = float(C)
    setcost = float(setcost)
    holdcost = float(holdcost)
    if request.method=='POST':
        Alpha = form.alpha.data
        Alpha = float(Alpha)
        L = form.lambd.data
        L = float(L)
        a,b,c,alpha,t1,l = smp.symbols('a b c alpha t1 l')
        cs, ci = smp.symbols('cs ci')
        t2 = (smp.log(1 - l*a/(c*alpha)*(1 - smp.exp(-c*t1)) + (b-1)*l/(l-c)*(smp.exp(-l*t1)-smp.exp(-c*t1))))/-l
        K = cs/(t1+t2) + (ci/(t1+t2))*(a/c*(t1 + (smp.exp(-c*t1) - 1)/c) - (b-1)*alpha/(l-c)*((smp.exp(-c*t1)-1)/c - (smp.exp(-l*t1)-1)/l) + alpha/l*((1 - smp.exp(-l*t2))/l - t2*smp.exp(-l*t2)))
        K = K.subs(a,A).subs(b,B).subs(c,C).subs(alpha,Alpha).subs(cs,setcost).subs(ci,holdcost).subs(l,L)
        h = smp.diff(K,t1)
        li=[]
        raphson(h,li)
        n = len(li)
        finalt1 = li[n-1]
        t2 = t2.subs(t1,li[n-1]).subs(a,A).subs(alpha,Alpha).subs(b,B).subs(c,C).subs(l,L)
        print(t2)
        K = K.subs(t1,li[n-1])
        if K<0 or li[n-1]<0 or t2<0: 
            K = "No optimised solution"
            li[n-1] = "No optimized solution"
            t2 = "No optimised solution"
        return render_template("expcase.html", form=form, t2=t2, K=K, t1 = li[n-1])
    return render_template("expcase.html", form = form)


if __name__ == '__main__':
    app.run(debug=True)
