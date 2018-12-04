#!/usr/bin/env python3
# Importing needed modules
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash,
                   make_response,
                   session as login_session)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Items
import random
import string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests
import datetime
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']
APPLICATION_NAME = "Item-Catalog"


# Enable CSRF protection globally for a Flask app
csrf = CSRFProtect(app)


# validating current logged in user
def checkUser():
    email = login_session['email']
    return session.query(User).filter_by(email=email).one_or_none()


# Add new user into database
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get user by his/her ID
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Get user ID by his/her email address
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Create new state
def new_state():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in range(32))
    login_session['state'] = state
    return state


# Connect to Google and authenticate user
@app.route('/gconnect', methods=['POST'])
@csrf.exempt
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode())
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
                                            'connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("you are now logged in as %s" % login_session['username'], "success")
    return jsonify(name=login_session['username'],
                   email=login_session['email'],
                   img=login_session['picture'])


# Disconnect user
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected', "success")
        return redirect(url_for("home"))
    else:
        response = make_response(json.dumps('Failed to revoke token for given '
                                            'user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all categories with 9 recent items
@app.route('/')
@app.route('/catalog/')
def home():
    state = new_state()
    items = session.query(Items).order_by(Items.id.desc()).limit(9).all()
    return render_template('catalog.html', items=items, STATE=state,
                           login_session=login_session)


# Show a category items
@app.route('/catalog/<string:category_name>/')
def showCategory(category_name):
    state = new_state()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id).all()
    return render_template('catalog.html', items=items, STATE=state,
                           login_session=login_session)


# Create a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if "username" not in login_session:
        flash("Sorry you need to login before creating a new item !!",
              "danger")
        return redirect(url_for("home"))
    if request.method == 'POST':
        date = datetime.datetime.now().strftime('%d/%m/%Y')
        print(date)
        newitem = Items(name=request.form['name'],
                        description=request.form['description'],
                        category_id=request.form['category'],
                        user_id=login_session['user_id'], date=date)
        session.add(newitem)
        session.commit()
        flash('New Item "{}" is Successfully Created'.format(newitem.name),
              "success")
        return redirect(url_for('home'))
    else:
        categories = session.query(Category).all()
        return render_template('newitem.html',
                               login_session=login_session,
                               categories=categories)


# Search for an item
@app.route("/search", methods=['POST'])
def search():
    items = session.query(Items).\
        filter(Items.name.
               like("%{}%".format(request.form["search"]))).all()
    return render_template('catalog.html', items=items,
                           login_session=login_session)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
