from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User
from patterns.user_factory import UserFactory

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for(f"{user.role}.dashboard"))
            
        flash('Invalid credentials.')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        try:
            user = UserFactory.create_user(
                role=role,
                name=request.form['name'],
                email=request.form['email'],
                password_hash=generate_password_hash(request.form['password']),
                specialty=request.form.get('specialty')
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(str(e))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))