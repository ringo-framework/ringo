"""Modul for the messanging system in ringo"""
import logging
import datetime
import json
import csv
import codecs
import cStringIO
import sets

log = logging.getLogger(__name__)


class UnicodeCSVWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fields, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames=fields,
                                     dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writeheader(self):
        self.writer.writeheader()

    def writerow(self, row):
        tmp_dict = {}
        for k, v in row.iteritems():
            try:
                tmp_dict[k] = v.encode("utf-8")
            except AttributeError:
                tmp_dict[k] = v
        self.writer.writerow(tmp_dict)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class Exporter(object):

    """Docstring for Exporter. """

    def __init__(self, clazz):
        """@todo: to be defined1.

        :clazz: @todo

        """
        self._clazz = clazz

    def serialize(self, data):
        """Will convert the given python data dictionary into a string
        containing JSON data

        :data: Dictionary containing Python data.
        :returns: String representing the data

        """
        return ""

    def flatten(self, data):
        """Will flatten nested data structures as found in Blobforms"""
        values = {}
        for key in data:
            # Handle data container of blobforms
            if key == "data":
                jdata = json.loads(data[key])
                for jkey in jdata:
                    values[jkey] = jdata[jkey]
            else:
                values[key] = data[key]
        return values

    def perform(self, items):
        """Returns the serialized item as string

        :items: @todo
        :returns: @todo

        """
        data = []
        for item in items:
            data.append(self.flatten(item.get_values(serialized=True)))
        return self.serialize(data)


class JSONExporter(Exporter):
    """Docstring for JSONExporter. """

    def serialize(self, data):
        return json.dumps(data)


class CSVExporter(Exporter):
    """Docstring for CSVExporter. """

    def _collect_keys(self, data):
        """The function will collect all keys (fields) within the given
        items. This is needed in case of blobform items as those items
        has a generic data field which may contain variable number of
        fields depending if the item has a value for the fields or
        not."""
        keys = sets.Set()
        for item in data:
            keys = keys.union(item.keys())
        return keys

    def serialize(self, data):
        outfile = cStringIO.StringIO()
        writer = UnicodeCSVWriter(outfile, sorted(self._collect_keys(data)))
        writer.writeheader()
        writer.writerows(data)
        outfile.seek(0)
        return outfile.read()


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

    def _deserialize_dates(self, obj):
        """This function can be called after the basic deserialisation has
        finished. It is used to convert data and datetime objects which
        is not supported by the defaults decoders

        :obj: Deserialized dictionary from basic deserialisation
        :returns: Deserialized dictionary with additional date and
        datetime deserialisation
        """
        for field in obj:
            if not obj[field]:
                # Ignore empty values as coversion will fail.
                continue
            if not field in self._clazz_type or not obj[field]:
                continue
            if self._clazz_type[field] == "DATE" and obj[field] is not None:
                obj[field] = datetime.datetime.strptime(obj[field],
                                                        "%Y-%m-%d").date()
            elif (self._clazz_type[field] == "DATETIME"
                  and obj[field] is not None):
                obj[field] = datetime.datetime.strptime(obj[field],
                                                        "%Y-%m-%d %H:%M:%S")
        return obj

    def deserialize(self, data):
        """Will convert the string data into a dictionary like data.

        :data: Importdata as string (JSON, XML...)
        :returns: Dictionary like data

        """
        return {}

    def perform(self, request, data):
        """Will return a list of imported items. The list will contain a
        tupel of the item and a string which gives information on the
        operaten (update, create).

        :request: Current request
        :data: Importdata as string (JSON, XML...)
        :returns: List of imported items

        """
        imported_items = []
        import_data = self.deserialize(data)
        factory = self._clazz.get_item_factory()
        _ = request.translate
        for values in import_data:
            uuid = values.get('uuid')
            try:
                # uuid might be empty for new items, which will raise an
                # error on loading.
                item = factory.load(uuid or "thisuuiddoesnotexist", uuid=True)
                operation = _("UPDATE")
            except:
                item = factory.create(user=request.user)
                operation = _("CREATE")
            # Ignore id, uuid field in import.
            if "id" in values:
                del values["id"]
            if "uuid" in values:
                del values["uuid"]
            item.set_values(values)
            imported_items.append((item, operation))
        return imported_items


class JSONImporter(Importer):
    """Docstring for JSONImporter."""

    def _deserialize_hook(self, obj):
        return self._deserialize_dates(obj)

    def deserialize(self, data):
        """Will convert the JSON data back into a dictionary with python values

        :data: String JSON data
        :returns: List of dictionary with python values
        """
        conv = json.loads(data, object_hook=self._deserialize_hook)
        if isinstance(conv, dict):
            return [conv]
        return conv


class CSVImporter(Importer):
    """Docstring for CSVImporter."""

    def _deserialize_hook(self, obj):
        conv = {}
        for k, v in obj.iteritems():
            conv[k] = unicode(v, "utf-8")
        conv = self._deserialize_dates(conv)
        return conv

    def deserialize(self, data):
        """Will convert the CSV data back into a dictionary with python values

        :data: String CSV data
        :returns: List of dictionary with python values
        """
        result = []
        infile = cStringIO.StringIO(data)
        reader = csv.DictReader(infile)
        for conv in reader:
            conv = self._deserialize_hook(conv)
            result.append(conv)
        return result
