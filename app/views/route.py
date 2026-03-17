from flask import (
    Blueprint, render_template
)

bp = Blueprint('route', __name__)

@bp.route('/route', methods=['GET'])
def admin():
    return render_template('route.html')
