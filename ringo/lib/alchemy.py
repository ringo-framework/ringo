"""Modul with helper functions to work with sqlalchemy."""
from sqlalchemy.orm import ColumnProperty, class_mapper


def get_columns_from_clazz(clazz, include_relations=False):
    return [prop.key for prop in class_mapper(clazz).iterate_properties
            if isinstance(prop, ColumnProperty) or include_relations]


def get_columns_from_instance(item, include_relations=False):
    return get_columns_from_clazz(item.__class__, include_relations)


def get_relations_from_clazz(clazz):
    only_columns = set(get_columns_from_clazz(clazz))
    with_relations = set(get_columns_from_clazz(clazz, True))
    return with_relations-only_columns
