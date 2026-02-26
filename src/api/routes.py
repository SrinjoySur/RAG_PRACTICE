from flask import Blueprint

welcome_bp=Blueprint('welcome',__name__)

@welcome_bp.route('/welcome')
def welcome():
    return "Welcome Dear Customer!!!"