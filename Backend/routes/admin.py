from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import db, Consultant, SystemPolicy

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/consultants')
@admin_required
def consultants():
    users = Consultant.query.all()
    return render_template('admin/consultants.html', consultants=users)

@admin_bp.route('/approve/<int:id>', methods=['POST'])
@admin_required
def approve(id):
    c = Consultant.query.get_or_404(id)
    c.approval_status = 'approved'
    db.session.commit()
    flash('Consultant approved.')
    return redirect(url_for('admin.consultants'))

@admin_bp.route('/reject/<int:id>', methods=['POST'])
@admin_required
def reject(id):
    c = Consultant.query.get_or_404(id)
    c.approval_status = 'rejected'
    db.session.commit()
    flash('Consultant rejected.')
    return redirect(url_for('admin.consultants'))

@admin_bp.route('/policies', methods=['GET', 'POST'])
@admin_required
def policies():
    if request.method == 'POST':
        name = request.form['name']
        val = request.form['value']
        policy = SystemPolicy.query.filter_by(policy_name=name).first()
        if not policy:
            policy = SystemPolicy(policy_name=name, policy_value=val, updated_by=session['user_id'])
            db.session.add(policy)
        else:
            policy.policy_value = val
        db.session.commit()
        flash('Policy updated.')
    items = SystemPolicy.query.all()
    return render_template('admin/policies.html', policies=items)