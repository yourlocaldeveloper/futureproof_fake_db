from flask import Flask, jsonify, request, g
from flask_cors import CORS
from controllers import people
from werkzeug import exceptions
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = "./database/database.db"

@app.route('/')
def home():
    init_db()
    return jsonify({'message': 'Hello from futureproof DB!'}), 200

@app.route('/people', methods=['GET', 'POST'])
def people_handler():
  fns = {
    'GET': people.index,
    'POST': people.create
  }
  resp, code = fns[request.method](request)
  return jsonify(resp), code

@app.route('/people/<int:people_id>', methods=['GET'])
def person_handler(people_id):
  fns = {
    'GET': people.show
  }
  resp, code = fns[request.method](request, people_id)
  return jsonify(resp), code

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()


def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

def query_db(query, args=(), one=False):
  cur = get_db().execute(query, args)
  get_db().commit()
  rv = cur.fetchall()
  cur.close()
  return (rv[0] if rv else None) if one else rv

@app.errorhandler(exceptions.NotFound)
def handle_404(err):
  return {'message': f'Could not be found: {err}'}, 404

@app.errorhandler(exceptions.BadRequest)
def handle_400(err):
    return {'message': f'Bad request: {err}'}, 400

@app.errorhandler(exceptions.InternalServerError)
def handle_500(err):
    return {'message': f"Internal Server Error: {err}"}, 500

if __name__ == "__main__":
    app.run(debug=True)