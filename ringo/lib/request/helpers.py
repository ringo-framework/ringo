#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urlparse


def encode_unicode_dict(unicodedict, encoding="utf-8"):
    bytedict = {}
    for key in unicodedict:
        if isinstance(unicodedict[key], unicode):
            bytedict[key] = unicodedict[key].encode(encoding)
        elif isinstance(unicodedict[key], dict):
            bytedict[key] = encode_unicode_dict(unicodedict[key])
        else:
            bytedict[key] = unicodedict[key]
    return bytedict


def decode_bytestring_dict(bytedict, encoding="utf-8"):
    unicodedict = {}
    for key in bytedict:
        if isinstance(bytedict[key], str):
            unicodedict[key] = bytedict[key].decode(encoding)
        elif isinstance(bytedict[key], dict):
            unicodedict[key] = decode_bytestring_dict(bytedict[key])
        else:
            unicodedict[key] = bytedict[key]
    return unicodedict


def encode_values(values):
    """Returns a string with encode the values in the given dictionary.

    :values: dictionary with key values pairs
    :returns: String key1:value1,key2:value2...

    """
    # Because urlencode can not handle unicode strings we encode the
    # whole dictionary into utf8 bytestrings first.
    return urllib.urlencode(encode_unicode_dict(values))


def decode_values(encoded):
    """Returns a dictionay with decoded values in the string. See
    encode_values function.

    :encoded : String key1:value1,key2:value2...
    :returns: Dictionary with key values pairs
    """
    # We convert the encoded querystring into a bystring to enforce that
    # parse_pq returns a dictionary which can be later decoded using
    # decode_bystring_dict. If we use the encoded string directly the
    # returned dicionary would contain bytestring as unicode. e.g
    # u'M\xc3\xbcller' which can't be decoded later.
    encoded = str(encoded)

    # Now convert the query string into a dictionary with UTF-8 encoded
    # bytestring values.
    values = urlparse.parse_qs(encoded)
    for key in values:
        values[key] = values[key][0]
    # Finally convert this dictionary back into a unicode dictionary
    return decode_bytestring_dict(values)
