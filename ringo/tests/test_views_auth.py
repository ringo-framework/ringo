#from pyramid import testing
#from ringo.tests import BaseFunctionalTest, BaseUnitTest
#
#
#class TestViews(BaseUnitTest):
    #def test_login_fails_empty(self):
    #    """ Make sure we can't login with empty credentials"""
    #    self.app.post('/auth/login', status=200)

    #def test_login_fails_empty(self):
    #    """ Make sure we can't login with empty credentials"""
    #    from ringo.views.auth import login
    #    self.config.add_route('login', 'auth/login')
    #    request = testing.DummyRequest(post={
    #        'submit': True,
    #    })
    #    view = login(request)
    #    response = view.post()


    #def test_login_succeeds(self):
    #    """ Make sure we can login """
    #    admin = User(username='sontek', password='temp', kind=u'admin')
    #    admin.activated = True
    #    self.session.add(admin)
    #    self.session.flush()

    #    from app.accounts.views import LoginView
    #    self.config.add_route('index', '/')
    #    self.config.add_route('dashboard', '/dashboard')

    #    request = self.get_csrf_request(post={
    #            'submit': True,
    #            'Username': 'sontek',
    #            'Password': 'temp',
    #        })

    #    view = LoginView(request)
    #    response = view.post()

    #    assert response.status_int == 302
