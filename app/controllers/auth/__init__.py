from flask import Blueprint, render_template, flash, request, redirect, url_for, session, get_flashed_messages
from flask.ext.login import login_user, current_user, logout_user
from flask.views import MethodView
from pymongo.errors import DuplicateKeyError
from app import config
from app.models.client import Client, Admin
from app.util import password
import logging

auth = Blueprint(
    'auth',
    __name__,
    template_folder=config.TEMPLATES,
    subdomain=config.AUTH_SUBDOMAIN,
)

class AuthLogin(MethodView):

    def get(self):
        return render_template("auth/login.html")

    def post(self):
        form = request.form
        em = form['email']
        pw = form['password']
        a = Admin.find_one({'email':em})
        v = a.verify_pwd(pw)
        if a and v:
            rem = False
            if form.get("remember-me"): rem = True
            success = login_user(a, remember=rem)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Please try again", "danger")

        return render_template("auth/login.html", form=form)

class AuthRegister(MethodView):

    def get(self):
        return render_template("auth/register.html")

    def post(self):
        form = request.form
        pwd = form['password']
        cpwd = form['confirm_password']
        if not Admin.passwords_match(pwd, cpwd):
            flash("Passwords do not match", "danger")
            return render_template("auth/register.html", form=form)
        try:
            cl = Client()
            cl.name = form['org']
            cl.save()
        except DuplicateKeyError as e:
            logging.exception(e)
            flash("Organization name already taken", "danger");
            return render_template("auth/register.html", form=form)
        try:
            a = Admin()
            a.name = form['name']
            a.email = form['email']
            a.password = form['password']
            a.client = cl
            a.save()
        except DuplicateKeyError as e:
            logging.exception(e)
            flash("Email address already taken", "danger");
            return render_template("auth/register.html", form=form)

        login_user(a)
        return redirect(url_for("facebook.index"))


class AuthLogout(MethodView):

    def get(self):
        logout_user()
        return redirect(url_for(".login"))

auth.add_url_rule("/login", view_func=AuthLogin.as_view('login'))
auth.add_url_rule("/logout", view_func=AuthLogout.as_view('logout'))
auth.add_url_rule("/register", view_func=AuthRegister.as_view('register'))
