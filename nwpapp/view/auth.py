import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_admin.contrib.sqla import ModelView

from nwpapp.model.auth_model import db, User
from nwpapp.controller.auth_db import has_credentials


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = db.session.query(User).filter_by(name=username).first()

        if user is None:
            error = "Incorrect username."
        elif not user.active:
            error = "Inactive user."
        else:
            # if not has_credentials(username, password):
                # error = "Invalid credentials"
                error = None

        if error is None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.query(User).filter_by(id=user_id).first()


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


class AdminView(ModelView):
    def is_accessible(self):
        if g.user is None:
            return False

        if g.user.admin:
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if g.user is not None:
                # permission denied
                flash("Not an Admin user.")
            # login
            return redirect(url_for("auth.login"))
