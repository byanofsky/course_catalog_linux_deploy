import os
import course_catalog
import unittest
import tempfile
import flask

class CourseCatalogTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = 'tests/test.db'
        course_catalog.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../' + self.test_db_path
        course_catalog.app.config['TESTING'] = True
        self.app = course_catalog.app.test_client()
        with course_catalog.app.app_context():
            course_catalog.course_catalog.init_db()

    def tearDown(self):
        os.unlink(os.path.abspath(self.test_db_path))

    # Method to help with registering account
    def register(self, email, name, password, verify_password):
        return self.app.post('/register/', data=dict(
            email=email,
            name=name,
            password=password,
            verify_password=verify_password,
        ), follow_redirects=True)

    # Method to help with login
    def login(self, email, password):
        return self.app.post('/login/', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def add_school(self, name, url):
        return self.app.post('/school/add/', data=dict(
            name=name,
            url=url
        ), follow_redirects=True)

    def edit_school(self, school_id, name, url):
        return self.app.post('/school/%s/edit/' % school_id, data=dict(
            name=name,
            url=url
        ), follow_redirects=True)

    def add_category(self, name):
        return self.app.post('/category/add/', data=dict(
            name=name
        ), follow_redirects=True)

    def edit_category(self, school_id, name):
        return self.app.post('/category/%s/edit/' % school_id, data=dict(
            name=name
        ), follow_redirects=True)

    # Test on a blank db to make sure starting clean
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No courses' in rv.data
        rv = self.app.get('/schools/')
        assert b'No schools' in rv.data
        rv = self.app.get('/categories/')
        assert b'No categories' in rv.data

    # Test form validation on registraton form
    def test_registration_errors(self):
        # Test for valid email address
        rv = self.register('by', 'Brandon', '12345', '12345')
        assert b'Please enter a valid email address.' in rv.data
        # Test that name is entered
        rv = self.register('by', '', '12345', '12345')
        assert b'Please enter a valid name.' in rv.data
        # Test that password is valid
        rv = self.register('by@me.com', 'Brandon', '12', '12')
        assert b'Please enter a valid password, at least 3 characters long.' in rv.data
        # Test that password is verified
        rv = self.register('by@me.com', 'Brandon', '12345', '56789')
        assert b'Please re-enter your password correctly.' in rv.data
        # Valid registration
        rv = self.register('by@me.com', 'Brandon', '12345', '12345')
        assert b'You were successfully registered' in rv.data
        # Log user out
        self.app.get('/logout/')
        # Check that user was logged out successfully
        with self.app:
            self.app.get('/register/')
            assert 'user_id' not in flask.session
        # Attempt to register with a duplicate email address
        rv = self.register('by@me.com', 'Brandon', '12345', '12345')
        assert b'A user already exists with this email address.' in rv.data

    # Test form validation on login form
    def test_login_errors(self):
        # Register new account
        rv = self.register('by@me.com', 'Brandon', '12345', '12345')
        assert b'You were successfully registered' in rv.data
        # Log user out
        self.app.get('/logout/')
        # Check that user was logged out successfully
        with self.app:
            self.app.get('/register/')
            assert 'user_id' not in flask.session
        # Attempt login with invalid email address
        rv = self.login('by', '12345')
        assert b'Please enter a valid email address.' in rv.data
        # Attempt login with incorrect password
        rv = self.login('by@me.com', '567')
        assert b'This password is incorrect.' in rv.data
        # Attempt login for a user that does not exist
        rv = self.login('random@me.com', '12345')
        assert b'There is no user with this email address.' in rv.data
        # Successful login
        rv = self.login('by@me.com', '12345')
        assert b'You were successfully logged in' in rv.data

    # Test that cookies are stored on registration and login
    def test_registration_and_login_cookies(self):
        with self.app:
            # Register account
            rv = self.register('by@me.com', 'Brandon', '12345', '12345')
            assert b'You were successfully registered' in rv.data
            # Check that cookie is stored for user_id
            assert flask.session['user_id'] == 1
            # Logout and check message flashed
            rv = self.app.get('/logout/', follow_redirects=True)
            assert b'You were successfully logged out' in rv.data
            # Check that cookie is removed
            assert 'user_id' not in flask.session
            # Log back in and check that cookie is stored
            rv = self.login('by@me.com', '12345')
            assert b'You were successfully logged in' in rv.data
            assert flask.session['user_id'] == 1

    # Test 'Next' redirects after successful login
    def test_login_next_url(self):
        with self.app:
            self.register('by@me.com', 'Brandon', '12345', '12345')
            self.app.get('/logout/', follow_redirects=True)
            assert 'user_id' not in flask.session
            # Visit add_school page without being logged in and
            # store redirect url
            rv = self.app.get('/school/add/')
            url = rv.headers['Location']
            rv = self.app.post(url, data=dict(
                email='by@me.com',
                password='12345'
            ), follow_redirects=True)
            # After login, should redirect to add school page
            assert b'Add School' in rv.data
            assert flask.session['user_id'] == 1

    # Test add school and edit school form errors
    def test_add_edit_school_form_errors(self):
        # Register account
        self.register('by@me.com', 'Brandon', '12345', '12345')
        # Test with both fields blank
        rv = self.add_school('', '')
        assert b'Please enter a school name.' in rv.data
        assert b'Please enter a school url.' in rv.data
        # Blank school name
        rv = self.add_school('', 'www.school.com')
        assert b'Please enter a school name.' in rv.data
        # Blank url
        rv = self.add_school('Test School 1', '')
        assert b'Please enter a school url.' in rv.data
        # Create school
        rv = self.add_school('Test School 1', 'www.school.com')
        assert b'School created' in rv.data
        # Attempt to create school with same name
        rv = self.add_school('Test School 1', 'www.school2.com')
        assert b'A school already exists with that name.' in rv.data

        #Create a second school for testing
        self.add_school('Test School 2', 'www.school2.com')

        # Attempt edits
        rv = self.edit_school(1, '', '')
        assert b'Please enter a school name.' in rv.data
        assert b'Please enter a school url.' in rv.data
        rv = self.edit_school(1, 'Test School Edit', '')
        assert b'Please enter a school url.' in rv.data
        rv = self.edit_school(1, '', 'www.testschool.com')
        assert b'Please enter a school name.' in rv.data
        rv = self.edit_school(1, 'Test School 2', 'www.testschool.com')
        assert b'A school already exists with that name.' in rv.data

        # Successfully edit school
        rv = self.edit_school(1, 'Test School Edit', 'www.school.com')
        assert b'School edited' in rv.data

    # Test adding a school, check on view_all_schools, then delete
    def test_add_edit_and_delete_school(self):
        self.register('by@me.com', 'Brandon', '12345', '12345')
        # Create school
        rv = self.add_school('Udacity', 'www.udacity.com')
        assert b'School created' in rv.data
        assert b'Udacity' in rv.data
        assert b'www.udacity.com' in rv.data
        assert b'Brandon' in rv.data
        # Check on view_all_schools page
        rv = self.app.get('/schools/')
        assert b'Udacity' in rv.data
        # Edit school
        self.edit_school(1, 'Udacity Edited', 'www.udacity-edit.com')
        # Check on view_all_schools page
        rv = self.app.get('/schools/')
        assert b'Udacity Edited' in rv.data
        # Delete school
        rv = self.app.post('/school/1/delete/', follow_redirects=True)
        assert b'School successfully deleted' in rv.data
        # Check on view_all_schools page
        rv = self.app.get('/schools/')
        assert b'Udacity Edited' not in rv.data
        # TODO: check login won't work right now
        # rv = self.app.get(school_url + 'delete/', follow_redirects=True)
        # assert b'There is no school with that id' in rv.data

    # Test add category and edit category form errors
    def test_add_edit_category_form_errors(self):
        # Register account
        self.register('by@me.com', 'Brandon', '12345', '12345')
        # Blank category name
        rv = self.add_category('')
        assert b'Please enter a category name.' in rv.data
        # Create Category
        rv = self.add_category('Test Category 1')
        assert b'Category created' in rv.data
        # Attempt to create category with same name
        rv = self.add_category('Test Category 1')
        assert b'A category already exists with that name.' in rv.data

        #Create a second category for testing
        self.add_category('Test Category 2')

        # Attempt edits
        rv = self.edit_category(1, '')
        assert b'Please enter a category name.' in rv.data
        rv = self.edit_category(1, 'Test Category 2')
        assert b'A category already exists with that name.' in rv.data

        # Successfully edit category
        rv = self.edit_category(1, 'Test Category Edit')
        assert b'Category edited' in rv.data

    # Test adding a category, check on view_all_categories, then delete
    def test_add_edit_and_delete_category(self):
        self.register('by@me.com', 'Brandon', '12345', '12345')
        # Create category
        rv = self.add_category('Category Test')
        assert b'Category created' in rv.data
        assert b'Category Test' in rv.data
        assert b'Brandon' in rv.data
        # Check on view_all_categories page
        rv = self.app.get('/categories/')
        assert b'Category Test' in rv.data
        # Edit category
        self.edit_category(1, 'Category Edited')
        # Check on view_all_categories page
        rv = self.app.get('/categories/')
        assert b'Category Edited' in rv.data
        # Delete category
        rv = self.app.post('/category/1/delete/', follow_redirects=True)
        assert b'Category successfully deleted' in rv.data
        # Check on view_all_schools page
        rv = self.app.get('/categories/')
        assert b'Category Edited' not in rv.data
        # TODO: check login won't work right now
        # rv = self.app.get(school_url + 'delete/', follow_redirects=True)
        # assert b'There is no school with that id' in rv.data


if __name__ == '__main__':
    unittest.main()
