import unittest

from mock import Mock
from pyramid import testing

from ringo.views.request import handle_POST_request


class HandlePostTests(unittest.TestCase):


    def generate_request(self):
        request = testing.DummyRequest()
        request.translate = Mock(return_value="")
        request.context = Mock()
        request.context.__model__ = Mock()
        request.cache_item_modul = Mock()
        return request


    def test_handlePost_with_invalid_form(self):
        request = self.generate_request()
        form = Mock()
        form.validate.return_value = False
        result = handle_POST_request(form, event="", callback=None, request=request)
        assert result == False


    def test_handlePost_with_blobform(self):
        request = self.generate_request()
        request.params['blobforms'] = Mock()
        form = Mock()
        form.validate.return_value = False
        result = handle_POST_request(form, event="", callback=None, request=request)
        assert result == False