from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096))
    user_id = db.Column(db.String(4096))
    auth_key = db.Column(db.String(4096))
    login = db.Column(db.Integer)
    access_level = db.Column(db.Integer)

    def __init__(self, name, user_id, authkey, login, access_level):
        self.name = name
        self.user_id = user_id
        self.auth_key = authkey
        self.login = login
        self.access_level = access_level

def delete_all():
    try:
        db.session.query(User).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()


def get_user_row_if_exists(user_id):
    get_user_row = User.query.filter_by(user_id=user_id).first()
    if get_user_row is not None:
        return get_user_row
    else:
        print("That user does not exist")
        return False

def add_user_and_login(name, user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.login = 1
        db.session.commit()
    else:
        new_user = User(name, user_id, None, 1, 0)
        db.session.add(new_user)
        db.session.commit()

def user_logout(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.login = 0
        db.session.commit()


def add_auth_key(user_id, auth_key):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.auth_key = auth_key
        db.session.commit()

def get_auth_key(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        return row.auth_key
    else:
        print("User with id: " + user_id + " doesn't exist")

def view_all():
    row = User.query.all()
    print_results(row)

def print_results(row):
    for n in range(0, len(row)):
        print(f"{row[n].id} | {row[n].name} |{row[n].user_id} | {row[n].auth_key} | {row[n].login} | {row[n].access_level}")


def get_all_logged_in_users():
    row = User.query.filter_by(login=1).all()
    print_results(row)
    online_users = {"users":[]}
    for n in range(0, len(row)):
        if row[n].access_level == 0:
            read = "unchecked"
            write = "unchecked"
        elif row[n].access_level == 1:
            read = "checked"
            write = "unchecked"
        else:
            read = "checked"
            write = "checked"
        online_users["users"].append([row[n].name, row[n].user_id, read, write])
    return online_users


def add_user_permission(user_id, read, write):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        if read and write:
            row.access_level = 2
        elif read:
            row.access_level = 1
        else:
            row.access_level = 0
        db.session.commit()

def get_user_access(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        get_user_row = User.query.filter_by(user_id=user_id).first()
        access_level = get_user_row.access_level
        return access_level
