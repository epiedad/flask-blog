import os
import flask_blog
import unittest
import tempfile

class FlaskTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, flask_blog.app.config['DATABASE'] = tempfile.mkstemp()
        flask_blog.app.config['TESTING'] = True
        self.app = flask_blog.app.test_client()
        flask_blog.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flask_blog.app.config['DATABASE'])

    #Test app functionality

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in rv.data

    def test_login_logout(self):
        rv = self.login('admin','default')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('fasdfd', 'default')
        assert 'Invalid username' in rv.data
        rv = self.login('admin', 'fasdf')
        assert 'Invalid password' in rv.data

    def test_add_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data
        
        
if __name__ == '__main__':
    unittest.main()
