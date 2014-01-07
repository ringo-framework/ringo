"""Modul for the messanging system in ringo"""
import logging
import datetime
from time import mktime
import json

log = logging.getLogger(__name__)

class RingoJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if (isinstance(obj, datetime.datetime)
           or isinstance(obj, datetime.date)):
            return obj.isoformat()
            #return int(mktime(obj.timetuple()))

class Exporter(object):

    """Docstring for Exporter. """

    def __init__(self, clazz):
        """@todo: to be defined1.

        :clazz: @todo

        """
        self._clazz = clazz

    def _get_data(self, item):
        data = {}
        for col in item.get_columns():
            data[col] = getattr(item, col)
        return data


    def serialize(self, data):
        """Will convert the given python data dictionary into a string
        containing JSON data

        :data: Dictionary containing Python data.
        :returns: String representing the data

        """
        return ""

    def perform(self, item):
        """Returns the serialized item as string

        :item: @todo
        :returns: @todo

        """
        data = self._get_data(item)
        return self.serialize(data)

class JSONExporter(Exporter):

    """Docstring for JSONExporter. """

    def serialize(self, data):
        return json.dumps(data, cls = RingoJSONEncoder)

class Importer(object):
    """Docstring for Importer."""

    def __init__(self, clazz):
        """@todo: to be defined1.

        :clazz: The clazz for which we will import data

        """
        self._clazz = clazz

    def _convert(self, data):
        """Will convert the string data into a dictionary like data.

        :data: Importdata as string (JSON, XML...)
        :returns: Dictionary like data

        """
        return {}

    def _set_values(self, item, values):
        """@todo: Docstring for _set_values.

        :item: @todo
        :values: @todo
        :returns: @todo

        """
        for key, value in values.iteritems():
            setattr(item, key, value)
        return item

    def perform(self, request, data):
        """Will return a list of imported items

        :request: Current request
        :data: Importdata as string (JSON, XML...)
        :returns: List of imported items

        """
        convdata = self._convert(data)
        factory = self._clazz.get_item_factory()
        items = []
        for values in convdata:
            uuid = values.get('uuid')
            try:
                item = factory.load(uuid, uuid=True)
            except:
                item = factory.create(user=request.user)
            self._set_values(item, values)
            items.append(item)
        return items


class JSONImporter(Importer):
    """Docstring for JSONImporter."""

    def _convert(self, data):
        conv = json.loads(data)
        if isinstance(conv, list):
            return conv
        else:
            return [conv]
