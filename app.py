from flask import Flask, session, render_template, redirect, flash, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Todo

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///todos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/api/todos')
def list_todos():
    all_todos = [todo.serialize() for todo in Todo.query.all()] #needs to be in dict format to parse to JSON

    return jsonify(todos=all_todos) #todos sets a key for the list

@app.route('/api/todos/<int:id>')
def get_todo(id):
    todo = Todo.query.get_or_404(id)
    return jsonify(todo=todo.serialize())

@app.route('/api/todos', methods=['POST'])
def create_todo():
    # add logic if there is no title, return error "Missing required title"
    new_todo = Todo(title=request.json['title'])
    db.session.add(new_todo)
    db.session.commit()
    response_json = jsonify(todo=new_todo.serialize())
    return (response_json, 201) #specify created status code

@app.route('/api/todos/<int:id>', methods=['PATCH']) #Patch must be done on server side/thru ajax
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.title = request.json.get('title', todo.title) #these will allow us to pass in either 'title' or 'done', default to current value if not present
    todo.done = request.json.get('done', todo.done) #these will ignore additional data passed in, set a default value

    # db.session.query(Todo).filter_by(id=id).update(request.json) #this works whether they pass in title OR done
    #but it will break if they enter some random value

    db.session.commit()

    return jsonify(todo=todo.serialize())

@app.route('/api/todos/<int:id>', methods=["DELETE"])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify(message= "deleted")