from uuid import uuid4

from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from utils import (
    error_for_list_title,
    error_for_todo_title,
    find_list_by_id,
)

import werkzeug

app = Flask(__name__)
app.secret_key='secret1'

@app.before_request
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.route("/")
def index():
    return redirect(url_for('get_lists'))

@app.route("/lists/new")
def add_todo_list():
    return render_template('new_list.html')

@app.route("/lists")
def get_lists():
    return render_template('lists.html',
                           lists=session['lists'])

@app.route("/lists", methods=["POST"])
def create_list():
    title = request.form["list_title"].strip()

    error = error_for_list_title(title, session['lists'])
    if error:
        flash(error, "error")
        return render_template('new_list.html', title=title)

    session['lists'].append({
        'id': str(uuid4()),
        'title': title,
        'todos': [],
    })

    flash("The list has been created.", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

@app.route("/lists/<list_id>")
def show_list(list_id):
    lst = find_list_by_id(list_id, session['lists'])
    if not lst:
        raise werkzeug.exceptions.NotFound(description="List not found")
    
    return render_template('list.html', lst=lst)

@app.route("/lists/<list_id>/todos", methods=["POST"])
def create_todo(list_id):
    todo_title = request.form['todo'].strip()
    lst = find_list_by_id(list_id, session['lists'])
    if not lst:
        raise werkzeug.exceptions.NotFound(description="List not found")
    
    error = error_for_todo_title(todo_title)
    if error:
        flash(error, "error")
        return render_template('list.html', lst=lst)
    
    lst['todos'].append({
        'id': str(uuid4()),
        'title': todo_title,
        'completed': False,
    })

    flash("The todo was added.", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

if __name__ == "__main__":
    app.run(debug=True, port=5003)

'''

input: The user enters text into the form
output: A new todo is created and is added to the current todo list

rules:
- When the form is submitted, the screen should automatically redraw itself
- If the new todo has a valid title, the new todo should not be marked as completed
- Issue a flash success message after successfully creating a new todo
# - Todo title is required and must have a max size of 100 characters, if not flash an error message
# - Duplicate todo titles are permitted
- The list of todo lists at /lists should show an updated count
- if the requested todo list does not exist, code needs to issue a 404 status code


'''