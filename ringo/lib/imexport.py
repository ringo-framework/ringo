"""Modul for the messanging system in ringo"""
import logging
import datetime
from time import mktime
import json
from sqlalchemy.orm import ColumnProperty, class_mapper

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
        self._clazz_type = self._get_types(clazz)

    def _get_types(self, clazz):
        type_mapping = {}
        for col in clazz.get_columns():
            prop = getattr(clazz, col)
            type_mapping[col] = str(prop.type)
        return type_mapping

    def deserialize(self, data):
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
            if key == "id": continue
            setattr(item, key, value)
        return item

    def perform(self, request, data):
        """Will return a list of imported items

        :request: Current request
        :data: Importdata as string (JSON, XML...)
        :returns: List of imported items

        """
        values = self.deserialize(data)
        factory = self._clazz.get_item_factory()
        uuid = values.get('uuid')
        try:
            item = factory.load(uuid, uuid=True)
        except:
            item = factory.create(user=request.user)
        self._set_values(item, values)
        return item

class JSONImporter(Importer):
    """Docstring for JSONImporter."""

    def _deserialize_hook(self, obj):
        """This function is called after the basic deserialisation has
        finished. It is used to convert data and datetime objects which
        is not supported by the defauls JSON decoder

        :obj: Deserialized dictionary from basic deserialisation
        :returns: Deserialized dictionary with additional date and
        datetime deserialisation
        """
        for field in obj:
            if self._clazz_type[field] == "DATE" and obj[field] is not None:
                obj[field] = datetime.datetime.strptime(obj[field],
                                                        "%Y-%m-%d").date()
            elif (self._clazz_type[field] == "DATETIME"
                  and obj[field] is not None):
                obj[field] = datetime.datetime.strptime(obj[field],
                                                        "%Y-%m-%dT%H:%M:%S.%f")
        return obj

    def deserialize(self, data):
        """Will convert the JSON data back into a dictionary with python values

        :data: String JSON data
        :returns: Python dictionary with python values
        """
        conv = json.loads(data, object_hook=self._deserialize_hook)
        return conv
