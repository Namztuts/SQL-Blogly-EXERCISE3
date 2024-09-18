#python3 -m unittest test.py | run test

from unittest import TestCase
from app import app
from models import db, User, Post, Tag, PostTag, connect_db

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tag_db_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class TagsViewsTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Add sample user and post before each test"""
        
        user = User(first_name="TestFirst", last_name="TestLast", img_url='www.google.com')
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.user = user
        

        post = Post(title="TestTitle", content="TestContent", user_id=f"{user.id}" )
        db.session.add(post)
        db.session.commit()

        self.post_id = post.id
        self.title = post.title
        self.content = post.content
        self.post = post
        
        
        tag = Tag(name='TestTag')
        db.session.add(tag)
        db.session.commit()
        
        self.tag_id = tag.id
        self.tag = tag

    def tearDown(self):
        """Clean up any messed up test after each test"""
        db.session.remove()
        db.drop_all()
        db.create_all()

    def test_list_tags(self):
        with app.test_client() as client:
            resp = client.get("/tags")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('TestTag', html)
            
    def test_show_tag(self):
        with app.test_client() as client:
            resp = client.get(f"/tags/{self.tag_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>TestTag</h1>', html) 
            
    def test_new_tag(self):
        with app.test_client() as client:
            data = {'tag_name':'TestingTag'}
            resp = client.post('/tags/new', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'>TestingTag</a>', html)
            
    def test_delete_tag(self):
        with app.test_client() as client:
            resp = client.get(f'/tags/{self.tag_id}/delete')
            
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/tags', resp.location)
            
    
