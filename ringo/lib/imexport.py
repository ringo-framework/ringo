"""Modul for the messanging system in ringo"""
import logging
import datetime
import json
import csv
import codecs
import cStringIO
import sets
import sqlalchemy as sa

from ringo.model.base import BaseItem
from ringo.model.user import UserSetting
from ringo.lib.helpers import serialize

log = logging.getLogger(__name__)


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


class RecursiveExporter(object):

    """Recurisve exporter for items of type clazz. For each item in the
    export the exporter will traverse down the relations of the items
    based on a given export configuration. If no export configuration is
    given the Exporter exports all fields of the items excluding
    relations and blobforms.

    Example export configuration::

    ["id", "foo", "bar", {"baz": ["f1", "f2", {"r1": [...]}, "baq": [...]}]

    In this configuration "id", "foo", "bar"... "f2" are considered as
    fields of the exported items. In contrast the keys of the nested
    dictionarys are taken as the name of the relations. The following
    list defines again the fields of the items in the relation.
    """

    def __init__(self, clazz, config):
        """@todo: to be defined1.

        :clazz: Clazz
        :config: Export configuration

        """
        if config:
            self._config = self._parse_config(json.loads(config))
        else:
            self._config = {"root": None}
        self._clazz = clazz
        self._data = {}

    def _parse_config(self, config, relation="root", result=None):
        """Will return a dictionary with the field configuration for each
        relation found in the export configuration. The field configuration
        is a list of fieldnames.

        :config: Export configuration
        :relation: Name of the "current" relation. The name "root" is a
        placeholder for the elements on the first level of the export.
        :result: temporary relation configuration. Is neeed for recursion in
        this function
        :returns: Dict with realtion configuration

        """
        if result is None:
            result = {}
        result[relation] = []
        for field in config:
            if isinstance(field, dict):
                for rel in field:
                    result[rel] = self._parse_config(field[rel],
                                                     rel,
                                                     result)[rel]
                    result[relation].append(rel)
            else:
                result[relation].append(field)
        return result

    def _iter_export(self, export, relation_config, relation):
        raise NotImplementedError()

    def _remove_duplicates(self):
        raise NotImplementedError()

    def perform(self, items):
        """@todo: Docstring for perform.
        function

        :arg1: @todo
        :returns: @todo

        """
        fields_to_export = self._config["root"]
        exporter = Exporter(self._clazz, fields_to_export, serialized=False)
        export = exporter.perform(items)
        self._iter_export(export, self._config, "root")
        self._remove_duplicates()
        return self._data


class RecursiveRelationExporter(RecursiveExporter):

    """Recursive Expoert for items of type clazz. After the export has
    finished the exported data will are returned as a dictionary. Each
    key in the dictionary will hold the exported values of the
    configured relations in the export configuration. The items of type
    clazz acn be found in the dict under the key 'root'"""

    def get_relation_config(self):
        return self._config

    def _iter_export(self, export, relation_config, relation):
        if self._data.get(relation) is None:
            self._data[relation] = []
        for item in export:
            temp = {}
            for field in item:
                if field in relation_config:
                    fields_to_export = relation_config[field]
                    if isinstance(item[field], list) and len(item[field]) > 0:
                        clazz = item[field][0].__class__
                        exporter = Exporter(clazz,
                                            fields_to_export,
                                            serialized=False)
                        self._iter_export(exporter.perform(item[field]),
                                          relation_config,
                                          field)
                    elif item[field] is not None:
                        clazz = item[field]
                        exporter = Exporter(clazz,
                                            fields_to_export,
                                            serialized=False)
                        self._iter_export(exporter.perform([item[field]]),
                                          relation_config,
                                          field)
                else:
                    temp[field] = item[field]
            self._data[relation].append(temp)

    def _remove_duplicates(self):
        for relation in self._data:
            visited = []
            unique = []
            for item in self._data[relation]:
                hashv = hash(unicode(item))
                if hashv not in visited:
                    visited.append(hashv)
                    unique.append(item)
                else:
                    continue
            self._data[relation] = unique


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

    def __init__(self, clazz, fields=None, serialized=True, relations=False):
        """Base exporter to export items of the given class. The
        exporter will return a list of dictionarys with key values pairs
        of the values for each items which should be exported. The
        fields to be exported can be configured. You can configure if
        the values should be serialized too.

        On default no relations will be exported. This can be changed by
        either setting the relations flag to true or defining relations
        explicit in the fields attribute.

        Exported relations will the id of the linked items.

        :clazz: Clazz of the items which will be exported
        :fields: List of fields and relations which should be exported.
        If no fields are provided all fields excluding the relations
        will be exported. The order of the configured fields will
        determine the order of the fields in the export (If supported
        e.g CSV).
        :serialized: Flag to indicate that the exported values should be
        serialized e.g dates will be converted into ISO8601 format. If
        realtions are included in the export the serialzed form will be
        the string representation of the item.
        Defaults to True.

        """
        self._clazz = clazz
        self._fields = fields
        self._serialized = serialized
        self._relations = relations

    def serialize(self, data):
        """Will convert the given python data dictionary into a string
        containing JSON data

        :data: Dictionary containing Python data.
        :returns: String representing the data

        """
        return data

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
            # Ensure that every item has a UUID. Set missing UUID here
            # if the item has no uuid set yet.
            if not item.uuid:
                item.reset_uuid()
            if self._fields is None:
                # Default export. Export all fields excluding relations
                values = item.get_values(serialized=self._serialized,
                                         include_relations=self._relations)
            else:
                values = {}
                for field in self._fields:
                    value = item.get_value(field)
                    if self._serialized:
                        value = serialize(value)
                    values[field] = value
            data.append(self.flatten(values))
        return self.serialize(data)


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

    def __init__(self, clazz, db=None):
        """@todo: to be defined1.

        :clazz: The clazz for which we will import data

        """
        self._clazz = clazz
        self._db = db
        self._clazz_type = self._get_types(clazz)

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
            if (not field in self._clazz_type
               or not self._clazz_type[field] in ['DATE',
                                                  'DATETIME',
                                                  'INTEGER']
               or obj[field] is None):
                continue
            elif obj[field] == "":
                obj[field] = None
                continue
            elif self._clazz_type[field] == "INTEGER":
                obj[field] = int(obj[field])
            elif self._clazz_type[field] == "DATE":
                obj[field] = datetime.datetime.strptime(
                    obj[field], "%Y-%m-%d").date()
            elif self._clazz_type[field] == "DATETIME":
                obj[field] = datetime.datetime.strptime(
                    obj[field], "%Y-%m-%d %H:%M:%S")
        return obj

    def _deserialize_relations(self, obj):
        """Will deserialize items in a MANYTOMANY relation. Other
        relations do not need to be handled as they should have a
        foreign key to the related item which is part of the items field
        anyway. It will replace the id values of the related items with
        the loaded items. This only works if there is a db connection
        available.

        :obj: Deserialized dictionary from basic deserialisation
        :returns: Deserialized dictionary with additional MANYTOMANY
        relations.
        """
        for field in obj.keys():
            ftype = self._clazz_type[field]
            # Handle all types of relations...
            if ftype in ["MANYTOMANY", "MANYTOONE",
                         "ONETOONE", "ONETOMANY"]:
                # Remove the items from the list if there is no db
                # connection or of there are not MANYTOMANY.
                if not self._db or (ftype != "MANYTOMANY"):
                    del obj[field]
                    continue
                clazz = getattr(self._clazz, field).mapper.class_
                tmp = []
                for item_id in obj[field]:
                    q = self._db.query(clazz).filter(clazz.id == item_id)
                    try:
                        tmp.append(q.one())
                    except:
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

    def perform(self, data, user=None, translate=lambda x: x, use_uuid=True):
        """Will return a list of imported items. The list will contain a
        tupel of the item and a string which gives information on the
        operaten (update, create). For create operations the new item
        will be created with the given user.

        :data: Importdata as string (JSON, XML...)
        :user: User object. Used when creating objects.
        :translate: Translation method.
        :use_uuid: Loading items by their uuid.
        :returns: List of imported items

        """
        imported_items = []
        import_data = self.deserialize(data)
        factory = self._clazz.get_item_factory()
        _ = translate
        for values in import_data:
            if use_uuid:
                id = values.get('uuid')
                if "id" in values:
                    del values["id"]
            else:
                id = values.get('id')
            try:
                # uuid might be empty for new items, which will raise an
                # error on loading.
                item = factory.load(id or "thisiddoesnotexist",
                                    uuid=use_uuid)
                item.set_values(values)
                operation = _("UPDATE")
            except:
                item = factory.create(user=user, values=values)
                operation = _("CREATE")
            imported_items.append((item, operation))
        return imported_items


class JSONImporter(Importer):
    """Docstring for JSONImporter."""

    def _deserialize_hook(self, obj):
        obj = self._deserialize_values(obj)
        return self._deserialize_relations(obj)

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
