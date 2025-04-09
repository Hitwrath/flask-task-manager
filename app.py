from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db,User,Task
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        email=request.form['email']
        password=request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login successful!','success')
            return redirect(url_for('my_tasks'))
        else:
            flash('Invalid email or password','error')
    
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registerd. Try logging in.','error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)

        new_user = User(username=username,email=email,password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('registration successful','success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/my_tasks')
def my_tasks():
    if 'user_id' not in session:
        flash('please login first.','error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    tasks = Task.query.filter_by(user_id=user.id).all()

    edit_task_id = request.args.get('edit',type= int)
    
    return render_template('myTasks.html',user_name=user,tasks=tasks,edit_task_id=edit_task_id)

@app.route('/add_task',methods=['POST'])
def add_task():
    if 'user_id' not in session:
        flash('Please log in first.','error')
        return redirect(url_for('login'))
    
    title = request.form['title']
    description = request.form.get('description')
    due_date_str = request.form.get('due_date')

    due_date = None
    if due_date_str:
        due_date =  datetime.strptime(due_date_str,'%Y-%m-%d')

    new_task = Task(
        title = title,
        description = description,
        due_date = due_date,
        user_id = session['user_id']
    )
    db.session.add(new_task)
    db.session.commit()

    flash('Task added successfully!','success')
    return redirect(url_for('my_tasks'))

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != session.get('user_id'):
        flash("unauthorised access",'error')
        return redirect(url_for('my_tasks'))
    
    task.is_completed = 'is_completed' in request.form
    db.session.commit()
    return redirect(url_for('my_tasks'))

@app.route('/update_task/<int:task_id>',methods=['POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id!=session.get('user_id'):
        flash("Unauthorised access","error")
        return redirect(url_for('my_tasks'))
    
    task.title = request.form['title']
    task.description = request.form.get('description')
    due_date_str = request.form.get('due_date')
    if due_date_str:
        from datetime import datetime
        task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
    else:
        task.due_date = None
    
    db.session.commit()
    return redirect(url_for('my_tasks'))

@app.route('/delete_task/<int:task_id>',methods=['GET','POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id!=session.get('user_id'):
        flash("Unauthorised access",'error')
        return redirect(url_for('my_tasks'))
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully!","success")
    return redirect(url_for('my_tasks'))


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out",'success')
    return redirect(url_for('home'))

if __name__ == 'main':
    app.run(debug=True)