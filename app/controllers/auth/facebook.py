from flask import Blueprint, render_template, request, redirect, url_for, Response
from flask.views import MethodView
from flask.ext.login import login_required, current_user
from app import config
from app.models.client import SocialAccount, FacebookPage, PageCategory
from flask_oauth import OAuth
import logging
from urlparse import parse_qs, urlparse
import json

oauth = OAuth()

facebook = Blueprint(
    "facebook",
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/facebook",
    subdomain=config.AUTH_SUBDOMAIN,
)

fb_app = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.FACEBOOK_APP_ID,
    consumer_secret=config.FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'manage_pages,read_insights,ads_management'}
)

@fb_app.tokengetter
def get_facebook_token(token=None):
    sa = current_user.social_account(SocialAccount.FACEBOOK)
    return (sa.token, config.FACEBOOK_APP_SECRET)

@facebook.route("/login", methods=['GET', 'POST'])
@login_required
def login():
    return fb_app.authorize(
        callback=url_for('.authorized',
            next=request.args.get('next'), _external=True)
    )

@facebook.route("/authorized", methods=['GET', 'POST'])
@fb_app.authorized_handler
@login_required
def authorized(resp):
    if resp is None:
        flash("You denied the request", "danger")
        return redirect(url_for(".index"))

    try:
        append = True
        sa = current_user.social_account(account_type=SocialAccount.FACEBOOK)
        if sa.token: append = False
        sa.token = resp.get('access_token')
        if append: current_user.social_accounts.append(sa)
        current_user.save()
    except Exception as e:
        logging.exception(e)

    return redirect(url_for(".verify"))

def get_pages(user_id):
    pages = []
    res = fb_app.get("/{}/accounts".format(user_id))
    pages = [p for p in res.data.get("data")]
    while res.data.get("paging", {}).get("next"):
        res = fb_app.get(
            "/{}/accounts".format(user_id),
            data={
                "after":res.data.get("paging", {}).get("cursor").get("after")
            }
        )
        pages+= [p for p in res.data.get("data")]

    return pages

def get_long_token(token):
    long_token = fb_app.get(
        "/oauth/access_token",
        data={
            'grant_type':'fb_exchange_token',
            'fb_exchange_token':token,
            'client_id':config.FACEBOOK_APP_ID,
            'client_secret':config.FACEBOOK_APP_SECRET,
        }
    )
    token = parse_qs(long_token.data, keep_blank_values=True)
    return {'token':token.get('access_token', [""])[0], 'expires':token.get('expires', [""])[0]}

class Index(MethodView):
    decorators = [ login_required, ]

    def get(self):
        return render_template("auth/facebook/index.html")

class Verify(MethodView):
    decorators = [ login_required, ]
    def get(self):
        return render_template("auth/facebook/load_pages.html")

class LoadPages(MethodView):
    decorators = [ login_required, ]
    def get(self):
        sa = current_user.social_account(SocialAccount.FACEBOOK)
        res = fb_app.get(
            "/debug_token",
            data={
                'input_token':sa.token
            }
        )
        if res:
            data = res.data.get('data')
            sa.id = data.get("user_id")
            sa.app_id = data.get("app_id")
            [sa.permissions.append(p) for p in data.get("scopes") if p not in sa.permissions]
            current_user.save()
            token = get_long_token(sa.token)
            sa.token = token['token']
            sa.expires = token['expires']
            current_user.save()
            pages = get_pages(sa.id)
            logging.info(pages)
            for page in pages:
                for p in current_user.facebook_pages:
                    if page.get("id") == p.id:
                        break
                else:
                    fp = FacebookPage()
                    fp.name = page.get("name")
                    fp.token = page.get("access_token")
                    fp.id = page.get("id")
                    [fp.permissions.append(perm) for perm in page.get("perms")]
                    for pc in page.get("category_list", []):
                        pca = PageCategory()
                        pca.id = pc.get("id")
                        pca.name = pc.get("name")
                        fp.categories.append(pca)
                    current_user.facebook_pages.append(fp)
            current_user.save()
        return render_template("auth/facebook/pages.html")

class SavePage(MethodView):
    decorators = [login_required,]

    def post(self):
        id = request.form["id"]
        logging.info(id);
        cfp = current_user.client.facebook_page
        for p in current_user.facebook_pages:
            if p.id == id:
                res = current_user.client.update({"$set":{"facebook_page":p._json()}})
                logging.info(res)
                break

        return Response(json.dumps({'id':id}), mimetype='application/json')

facebook.add_url_rule("/", view_func=Index.as_view('index'))
facebook.add_url_rule("/verify", view_func=Verify.as_view('verify'))
facebook.add_url_rule("/loadpages", view_func=LoadPages.as_view('load_pages'))
facebook.add_url_rule("/save_page", view_func=SavePage.as_view('save_page'))
