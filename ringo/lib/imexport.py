"""Modul for the messanging system in ringo"""
import logging
import datetime
import json
import csv
import codecs
import cStringIO
import sets
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import xlsxwriter
import sqlalchemy as sa

from ringo.model.base import BaseItem
from ringo.model.user import UserSetting
from ringo.lib.helpers import serialize, deserialize
from ringo.lib.sql import DBSession
from ringo.lib.alchemy import get_props_from_instance

log = logging.getLogger(__name__)


class ExportConfiguration(object):

    """
    You can provide a JSON configuration file for the export to define
    which fields of the given modul should be exported in detail.
    Providing a configuration file allows you to export also
    `properties` and related items which are not part of the default
    export.

    Example export configuration::


        ["f1", "f2", "f3", {"bar": ["f4", "f5", {"baz": [...]}}]

    In this configuration "id", "foo", "bar" considered as fields of the
    exported item. In contrast the keys of the nested dictionarys are
    taken as the name of the relations. The following list defines again
    the fields of the items in the relation.  So assuming you are
    exporting items of type "Foo" the export will include fields "f1",
    "f2", and "f3". Further "Foo" is related to "Bar" items in the
    relation "bar". From the "Bar" items the fields "f4" and "f5" are
    included. The "Bar" items have themself a relation called "baz" and
    again you can follow the scheme to define a detail configuration of
    what should be in the export.

    The configuration also support wildcards. Use "*" so add all fields
    of the item or related item::

        ["*" {"bar": ["*", {"baz": [...]}}]
    """

    def __init__(self, jsonconfig):
        self.config = jsonconfig
        self.relations = self._parse(jsonconfig)

    def _parse(self, config, relation="root"):
        """Will return a dictionary with the field configuration for each
        relation found in the export configuration. The field configuration
        is a list of fieldnames.

        :config: Export configuration
        :relation: Name of the "current" relation. The name "root" is a
        placeholder for the elements on the first level of the export.
        :returns: Dict with realtion configuration

        """
        relations = {}
        relations[relation] = []
        for field in config:
            if isinstance(field, dict):
                for rel in field:
                    relations.update(self._parse(field[rel], rel))
            else:
                relations[relation].append(field)
        return relations

    def includes_wildcard(self):
        return "*" in self.config

    def get_relation_fields(self):
        fields = []
        for f in self.config:
            if f == "*":
                continue
            else:
                fields.append(f)
        return fields


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseItem):
            return obj.id
            # Let the base class default method raise the TypeError
        elif isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
            # Let the base class default method raise the TypeError
        elif isinstance(obj, UserSetting):
            return obj.id
        else:
            return json.JSONEncoder.default(self, obj)


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

    """Base exporter to export items of the given class. The
    exporter will return a list of dictionarys with key values pairs
    of the values for each items which should be exported.

    The export is done by calling the `perform` method of this
    class.

    On default the exporter will return all fields of the item but
    no relations or related items. However the Exporter is able to
    export related items if configured correct. In this case the
    Exporter will return a list of nested dictionaries.

    As a detailed configuration of the content of the export you can
    provide an ExportConfiguration to the exporter.

    On default the exported items will be `serialized`. This means
    that each value is converted into a export specific format. E.g
    dates are converted into ISO8601 notation in the JSONExporter.
    If set to false the values are real python values.
    """

    def __init__(self, clazz, serialized=True, config=None):
        """
        :clazz: Clazz of the items which will be exported.
        :fields: List of fields and relations which should be exported.
        :serialized: Flag to indicate that the exported values should be serialized.
        :config: ExportConfiguration for the exporter.

        """
        self._clazz = clazz
        self._serialized = serialized
        self._config = config

    def serialize(self, data):
        """Method to convert the given python listing with the exported
        items into a serialized form. This is depended on the concrete
        exporter. This default implementation just returns the given
        data as it is. You can overwrite this method in a more specific
        renderer.

        :data: List containing exported items.
        :returns: String representing the data
        """
        return data

    def flatten(self, data):
        """Will flatten nested data structures as found in Blobforms"""
        values = {}
        for key in data:
            # Handle data container of blobforms
            if key == "data":
                try:
                    jdata = json.loads(data[key])
                    for jkey in jdata:
                        values[jkey] = jdata[jkey]
                except ValueError:
                    values[key] = data[key]
            else:
                values[key] = data[key]
        return values

    def perform(self, items):
        """Will export the given items. Depending if the Exporter has
        been initialised with the `serialized` parameter the export will
        return a list of dictionaries (each with the values) or in the
        exporter specific format (e.g. JSON).

        :items: Items which will be exported.
        :returns: Exported items (format depends on the export configuration).

        """
        data = []
        # Check if the given item(s) is a list. If not we put it into a
        # temporary list.
        if not isinstance(items, list):
            _items = [items]
        else:
            _items = items
        for item in _items:
            # Check if a configuration is provided.
            if not self._config or len(self._config.config) == 0:
                # No configuration is provided. Export all fields
                # exluding relations.
                values = item.get_values(serialized=self._serialized)
            else:
                # Configuration is provided. Export fields and relations
                # based on the given configuration.
                values = {}
                if self._config.includes_wildcard():
                    fields = [p.key for p in get_props_from_instance(item)]
                    fields.extend(self._config.get_relation_fields())
                else:
                    fields = self._config.config
                for field in fields:
                    if isinstance(field, dict):
                        for relation in field:
                            clazz = getattr(self._clazz, relation).mapper.class_
                            exporter = Exporter(clazz,
                                                serialized=self._serialized,
                                                config=ExportConfiguration(field[relation]))
                            value = item.get_value(relation)
                            value = exporter.perform(value)
                            values[relation] = value
                    else:
                        values[field] = item.get_value(field)
            data.append(self.flatten(values))

        # If the input to the method was a single item we will return a
        # single exported item.
        if not isinstance(items, list):
            if len(data) > 0:
                data = data[0]
            else:
                data = None
        return self.serialize(data)


class XLSXExporter(Exporter):
    """Docstring for XLSXExporter. """

    def serialize(self, data):
        output = StringIO.StringIO()
        book = xlsxwriter.Workbook(output)
        if len(data) > 0:
            keys = sorted(data[0].keys())
            sheet = book.add_worksheet(self._clazz.__tablename__)
            row = 0
            col = 0
            # write header
            for key in keys:
                sheet.write(row, col, key)
                col += 1
            # write data
            col = 0
            row = 1
            for item in data:
                for key in keys:
                    value = serialize(item[key])
                    sheet.write(row, col, value)
                    col += 1
                row += 1
                col = 0
        book.close()
        output.seek(0)
        return output.read()


class JSONExporter(Exporter):
    """Docstring for JSONExporter. """

    def serialize(self, data):
        return json.dumps(data, cls=ExtendedJSONEncoder)


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

    def __init__(self, clazz, db=DBSession, use_strict=False):
        """@todo: to be defined1.

        :clazz: The class (inheriting from BaseItem) of the import data

        """
        if not issubclass(clazz, BaseItem):
            raise TypeError("%s is not a subclass of BaseItem" % clazz)

        self._clazz = clazz
        self._db = db
        self._clazz_type = self._get_types(clazz)
        self._use_strict = use_strict

    def _get_types(self, clazz):
        type_mapping = {}
        mapper = sa.orm.class_mapper(clazz)
        for prop in mapper.iterate_properties:
            if isinstance(prop, sa.orm.RelationshipProperty):
                type_mapping[prop.key] = str(prop.direction.name)
            else:
                type_mapping[prop.key] = str(prop.columns[0].type)
        return type_mapping

    def _deserialize_values(self, obj):
        """This function can be called after the basic deserialisation
        has finished. It is used to convert integer, date and datetime
        objects which are either not supported by the defaults decoders
        or not decoded correct (NULL values)

        :obj: Deserialized dictionary from basic deserialisation
        :returns: Deserialized dictionary with additional integer, date
        and datetime deserialisation
        """
        for field in obj:
            if (field not in self._clazz_type or
               obj[field] is None):
                continue
            else:
                datatype = self._clazz_type[field].lower()
                if datatype in ['manytoone', 'manytomany', 'onetomany', 'onetoone']:
                    continue
                obj[field] = deserialize(obj[field], datatype)
        return obj

    def _deserialize_relations(self, obj):
        """Deserialize items in a MANYTOMANY relation given as a list
        of primary keys. It will replace the id values of the related items with
        the loaded items.
        Other types of relations have a foreign key, which is an attribute at
        one side of the relation anyway. Thus, the relationship can be
        established by importing both sides of the relationship.

        :obj: Deserialized dictionary from basic deserialisation
        :returns: Deserialized dictionary with additional MANYTOMANY
        relations.
        """
        for field in obj.keys():
            # Just keep already deserialized relations
            if (isinstance(obj[field], BaseItem)
                or isinstance(obj[field], list) and all(
                    isinstance(i, BaseItem) for i in obj[field])):
                continue

            try:
                ftype = self._clazz_type[field]
            except KeyError:
                log.warning("Can not find field %s in %s"
                            % (field, self._clazz_type))
                continue

            # Handle all types of relations...
            if ftype in ["MANYTOONE", "ONETOONE", "ONETOMANY"]:
                # Remove related items from object if they are not MANYTOMANY.
                del obj[field]
            elif ftype == "MANYTOMANY":
                clazz = getattr(self._clazz, field).mapper.class_
                tmp = []
                for item_id in obj[field]:
                    item = self._db.query(clazz).get(item_id)
                    if item:
                        tmp.append(item)
                    else:
                        log.warning(("Can not load '%s' id: %s "
                                     "Relation '%s' of '%s' not set"
                                     % (clazz, item_id, field, self._clazz)))
                obj[field] = tmp
        return obj

    def deserialize(self, data):
        """Will convert the string data into a dictionary like data.

        :data: Importdata as string (JSON, XML...)
        :returns: Dictionary like data

        """
        return {}

    def perform(self, data, user=None, translate=lambda x: x, load_key="uuid"):
        """Will return a list of imported items. The list will contain a
        tupel of the item and a string which gives information on the
        operaten (update, create). For create operations the new item
        will be created with the given user.

        :data: Importdata as string (JSON, XML...)
        :user: User object. Used when creating objects.
        :translate: Translation method.
        :load_key: Define name of the key which is used to load the
        item.
        :returns: List of imported items

        """
        self.load_key = load_key
        data = self.deserialize(data)
        imported_items = []
        factory = self._clazz.get_item_factory()
        if self._use_strict:
            factory._use_strict = self._use_strict
        _ = translate
        for values in data:
            id = values.get(load_key)
            if load_key != "id" and "id" in values:
                # Only the database should manage primary keys.
                # Except when loading by primary key, allow trying to set it.
                del values["id"]
            try:
                item = factory.load(id, field=load_key)
                item.set_values(values, use_strict=self._use_strict)
                operation = _("UPDATE")
            except sa.orm.exc.NoResultFound:
                item = factory.create(user=user, values=values)
                self._db.add(item)
                operation = _("CREATE")
            imported_items.append((item, operation))
        return imported_items


class JSONImporter(Importer):
    """Docstring for JSONImporter."""

    def _deserialize_recursive(self, obj):
        for field in obj:
            if isinstance(obj[field], (dict, list)):
                clazz = getattr(self._clazz, field).mapper.class_
                importer = JSONImporter(clazz, db=self._db, use_strict=self._use_strict)
                if isinstance(obj[field], dict):
                    import_data = [obj[field]]
                    imported_item = importer.perform(json.dumps(import_data),
                                                     load_key=self.load_key)
                    obj[field] = imported_item[0][0]
                elif (obj[field] and all(
                        isinstance(i, dict) for i in obj[field])):
                    import_data = obj[field]
                    imported_item = importer.perform(json.dumps(import_data),
                                                     load_key=self.load_key)
                    obj[field] = [x[0] for x in imported_item]
        return obj

    def _deserialize_hook(self, obj):
        obj = self._deserialize_recursive(obj)
        obj = self._deserialize_values(obj)
        return self._deserialize_relations(obj)

    def deserialize(self, data):
        """Will convert the JSON data back into a dictionary with python values

        :data: String JSON data
        :returns: List of dictionary with python values
        """
        conv = json.loads(data)
        if isinstance(conv, dict):
            conv = [conv]
        return [self._deserialize_hook(c) for c in conv]


class CSVImporter(Importer):
    """Docstring for CSVImporter."""

    def _deserialize_hook(self, obj):
        conv = {}
        for k, v in obj.iteritems():
            conv[k] = unicode(v, "utf-8")
        conv = self._deserialize_values(conv)
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
