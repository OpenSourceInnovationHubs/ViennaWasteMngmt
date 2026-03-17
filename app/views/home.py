from flask import (
    Blueprint, render_template, redirect
)

bp = Blueprint('home', __name__)

@bp.route('/')
def redirect_to_home():
    return redirect('/home')


@bp.route('/home', methods=['GET'])
def home():
    return render_template('home.html')
