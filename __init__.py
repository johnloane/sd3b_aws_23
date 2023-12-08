from flask import Flask, render_template, request, session, abort, redirect
import pathlib
import os
import json
from flask_sqlalchemy import SQLAlchemy
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests 
from google.oauth2 import id_token
import requests
from pip._vendor import cachecontrol
from . import my_db, pb 
import time

db = my_db.db
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Dkit1234!@localhost/sd3b_23'

db.init_app(app)


GOOGLE_CLIENT_ID = "817858895140-04ppifkt6d84b13k7gis5ao1ch3fp4bi.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://sd3b.online/callback"
)



alive = 0
data = {}

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper

@app.route("/")
def index():
   return render_template("google_login.html")


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500) # State does not match!
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_sensors")


@app.route("/protected_sensors")
@login_is_required
def protected_sensors():
    my_db.add_user_and_login(session['name'], session['google_id'])
    #Write the name and google_id to the database
    return render_template("protected_sensors.html", user_id=session['google_id'], online_users = my_db.get_all_logged_in_users())

@app.route('/grant-<user_id>-<read>-<write>', methods=["POST"])
def grant_access(user_id, read, write):
    # This should only work for admins who are identfied by google_id
    print(f"Granting permission for {user_id}-{read}-{write}")
    if session['google_id'] == "115286914554441662160":
        print("Adding user permission to db")
        my_db.add_user_permission(user_id, read, write)
        token = my_db.get_token(user_id)
        if token is not None:
            timestamp, ttl = pb.parse_token(token)
            current_time = time.time()
            print(f"Timestamp {timestamp} Current time {current_time} TTL {ttl} ")
            if (timestamp+900) - current_time > 0:
                print("Revoking access to current key")
                pb.revoke_access(token)
        if read == "true" and write == "true":
            print("Granting read and write access")
            token = pb.grant_read_write_access(user_id)
            my_db.add_token(user_id, token)
            access_response={'token':token, 'uuid':user_id, 'cipher_key':pb.cipher_key}
            return json.dumps(access_response)
        elif read == "true":
            print("Granting read access")
            token = pb.grant_read_access(user_id)
            my_db.add_token(user_id, token)
            access_response={'token':token, 'uuid':user_id, 'cipher_key':pb.cipher_key}
            return json.dumps(access_response)
        else:
            access_response={'token':123, 'uuid':user_id, 'cipher_key':pb.cipher_key}
            return json.dumps(access_response)
    else:
        print("Non admin trying to grant privileges")
        return json.dumps({"access":"denied"})

@app.route('/get_token', methods=["POST"])
def get_token():
    user_id = session['google_id']
    print(f"{session['name']} with {session['google_id']} reqesting token")
    token = my_db.get_token(session['google_id'])
    token_response = {'token':token, 'uuid':user_id, 'cipher_key':pb.cipher_key}
    return json.dumps(token_response)

@app.route('/get_sensor_token-<uuid>')
def get_sensor_token(uuid):
    token = my_db.get_token(uuid)
    token_response = {'token':token}
    return json.dumps(token_response)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/keep_alive")
def keep_alive():
   global alive, data
   alive += 1
   keep_alive_count = str(alive)
   data['keep_alive'] = keep_alive_count
   parsed_json = json.dumps(data)
   return str(parsed_json)



if __name__ == '__main__':
    app.run()
