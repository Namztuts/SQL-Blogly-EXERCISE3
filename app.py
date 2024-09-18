"""Blogly application."""
from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, PostTag, Tag

app = Flask(__name__)

app.config['SECRET_KEY'] = "SupaSecret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///user_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.app_context().push()
connect_db(app)


@app.route('/')
def home():
    return redirect('/users')

@app.route('/users')
def show_users():
    '''Show list of all users in db'''
    users = User.query.order_by(User.first_name, User.last_name).all()
    return render_template('home.html', users=users)


@app.route('/users/new')
def new_user():
    '''Goes to a user creation form'''
    return render_template('new_user.html')

@app.route('/users/new', methods=['POST']) #on submit, the form does this
def add_user():
    '''Creates user based on user input'''
    first = request.form['first_name'].strip() #removing any leading or trailing spaces from user input
    last = request.form['last_name'].strip()
    url = request.form['img_url'].strip() or None
    
    if not first or not last:
        flash('First and last name are required!')
        return redirect('/users/new')
    
    new_user = User(first_name=first,last_name=last,img_url=url)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/users')


@app.route('/users/<int:user_id>')
def user_details(user_id):
    '''Shows details for a specific user'''
    user = User.query.get_or_404(user_id)
    posts = user.posts
    return render_template('details.html',user=user, posts=posts)


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST']) #when initially going to this URL (GET) grabbing data and auto filling the inputs
def user_update(user_id):
    '''Edits user based on user edits'''
    user = User.query.get_or_404(user_id)
    
    if request.method =='POST': #on submit of the form, this URL does this
        user.first_name= request.form['edit_first_name'].strip() #removing any leading or trailing spaces from user input
        user.last_name= request.form['edit_last_name'].strip()
        user.img_url= request.form['edit_img_url'].strip()
    
        db.session.commit()
        return redirect('/users')
    
    return render_template('edit_user.html', user=user) 


@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    '''Deletes a specific user'''
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect('/users')
#USERS ROUTES END

#POSTS ROUTES START
@app.route('/posts/<int:post_id>')
def show_user_post(post_id):
    '''Shows details for a specific post'''
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    return render_template('post_details.html',post=post, tags=tags)


@app.route('/users/<int:user_id>/posts/new')
def new_post(user_id):
    '''Goes to a form to create a new post'''
    user = User.query.get_or_404(user_id)
    return render_template('new_post.html', user=user)

@app.route('/users/<int:user_id>/posts/new', methods=['POST']) #on Submit, do this
def add_post(user_id):
    '''Creates a new post and returns back to post details'''
    title = request.form['post_title'].strip()
    content = request.form['post_content'].strip()
    
    if not title or not content:
        flash('Both a title and content is required to create a post!')
        return redirect(f'/users/{user_id}/posts/new')
    
    new_post = Post(title=title,content=content,user_id=user_id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/posts/{new_post.id}')


@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST']) #when initially going to this URL (GET) grabbing data and auto filling the inputs
def post_update(post_id):
    '''Edits post based on user edits'''
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    
    if request.method =='POST': #on submit of the form, this URL does this
        post.title= request.form['edit_post_title'].strip()
        post.content= request.form['edit_post_content'].strip()
        
        checked_tags = request.form.getlist('tag_name') #.getlist returns a list with the checked values | this list consists of strings
        tag_ids = [int(num) for num in checked_tags] #converting the list of strings to integers
        post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() #in_ | SELECT * FROM Tag WHERE id IN (1, 2, 3) | getting model objects of each tag to add

        db.session.add(post)
        db.session.commit()
        return redirect(f'/posts/{post_id}')
    
    return render_template('edit_post.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/delete')
def delete_post(post_id):
    '''Deletes a specific user'''
    post = Post.query.get_or_404(post_id)
    
    db.session.delete(post) #additional way to delete vs how i did it in the users route
    db.session.commit()
    flash(f'Post "{post.title}" has been deleted.')
    
    return redirect(f'/users/{post.user_id}')
#END POSTS ROUTES

#START TAGS ROUTS
@app.route('/tags')
def show_tags():
    '''Shows a list of all the tags'''
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)


@app.route('/tags/<int:tag_id>')
def tag_details(tag_id):
    '''Shows details for a specific tag'''
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts
    return render_template('tag_details.html',tag=tag, posts=posts)


@app.route('/tags/new')
def new_tag():
    '''Show new tag form'''
    return render_template('new_tag.html')

@app.route('/tags/new', methods=['POST'])
def add_tag():
    '''Creates a new tag'''
    name = request.form['tag_name'].strip()
    if not name:
        flash('Please enter a tag name!')
        return redirect(f'/tags/new')
        
    new_tag = Tag(name=name)
    db.session.add(new_tag)
    db.session.commit()
    return redirect('/tags')


@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def edit_tag(tag_id):
    '''Form to edit a specific tag'''
    tag = Tag.query.get_or_404(tag_id)
    
    if request.method =='POST': #on submit of the form, this URL does this
        tag.name= request.form['edit_tag_name'].strip()
    
        db.session.commit()
        return redirect(f'/tags/{tag_id}')
    
    return render_template('edit_tag.html', tag=tag)


@app.route('/tags/<int:tag_id>/delete')
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    
    db.session.delete(tag)
    db.session.commit()
    flash(f'Tag "{tag.name}" has been deleted.')
    
    return redirect(f'/tags')
