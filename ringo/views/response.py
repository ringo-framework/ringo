from ringo.model.base import BaseItem, BaseList
from ringo.lib.imexport import JSONExporter


class JSONResponse(object):
    """Generic response item for JSON responses on the RESTfull api"""

    def __init__(self, success, data, params=None):
        """Create a new JSONResponse. The Response object has the
        following format::

        {
            "success":[true|false],
            "data": object
            "params": {
                "parm1": "value1",
                "parm2": "value1",
                ...
                "parmN": "value1"
            }
        }

        The format of the data or params attribute is not specified. It
        can basically contain any valid JSON. Usually the data attribute
        will contain a dictionary with the attributes of an item or a
        list of  dictionarys with values of items.

        :data: Payload included in the Response.
        :success: Generic status of the query
        :params: Optional parameters. Can include further information.
        E.g why the last request failed.
        """
        self._data = data
        self._success = success
        self._params = params

    def __json__(self, request):
        rvalue = {}
        rvalue['success'] = self._success
        if isinstance(self._data, BaseItem):
            exporter = JSONExporter(self._data.__class__)
            self._data = exporter.perform([self._data])
        elif isinstance(self._data, BaseList):
            exporter = JSONExporter(self._data.__class__)
            self._data = exporter.perform(self._data.items)
        rvalue['data'] = self._data
        rvalue['params'] = self._params
        return rvalue
