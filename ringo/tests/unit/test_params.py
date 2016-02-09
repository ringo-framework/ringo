#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest


@pytest.mark.parametrize("data",
                         [
                             ({"backurl": "/foo/bar/baz"}, "/foo/bar/baz"),
                             ({"missing": "/foo/bar/baz"}, None),
                             ({"backurl": ""}, ""),
                         ])
def test_get_backurl(apprequest, data):
    from ringo.lib.request.params import get_backurl
    apprequest.GET = data[0]
    backurl = get_backurl(apprequest)
    assert backurl == data[1]


@pytest.mark.parametrize("data",
                         [
                             ({"values": "foo=bar&baz=foo"},
                              {"foo": "bar", "baz": "foo"}),
                             ({"values": "foo=Dr%2C+XXX&bar=foo%3A"},
                              {"foo": "Dr, XXX", "bar": "foo:"}),
                             ({"missing": "/foo/bar/baz"}, {}),
                             ({"values": ""}, {}),
                         ])
def test_get_values(apprequest, data):
    from ringo.lib.request.params import get_values
    apprequest.GET = data[0]
    backurl = get_values(apprequest)
    assert backurl == data[1]


values = [
            ({"foo": "bar", "baz": "foo"}, "foo=bar&baz=foo"),
            ({"foo": "Dr, XXX", "bar": "foo:"}, "foo=Dr%2C+XXX&bar=foo%3A"),
            ({"foo": u"Dr.&Dr. XXX", "bar": u"äüöÄÜÖ"}, u"foo=Dr.%26Dr.+XXX&bar=%C3%A4%C3%BC%C3%B6%C3%84%C3%9C%C3%96"),
            ({"a": "b", "c": "d", "e": "f"}, "a=b&c=d&e=f"),
            ({}, "")
         ]

@pytest.mark.parametrize("data", values)
def test_encode_values(data):
    from ringo.lib.request.helpers import encode_values
    result = encode_values(data[0])
    assert result == data[1]


@pytest.mark.parametrize("data", values)
def test_decode_values(data):
    from ringo.lib.request.helpers import decode_values
    result = decode_values(data[1])
    assert result == data[0]

values2 = [
            {"foo": "bar", "baz": "foo"},
            {"foo": "Dr, XXX", "bar": "foo:"},
            {"foo": u"Dr.&Dr. XXX", "bar": u"äüöÄÜÖ"},
            {"a": "b", "c": "d", "e": "f"},
            {}
         ]


@pytest.mark.parametrize("data", values2)
def test_decode_encode_values(data):
    from ringo.lib.request.helpers import encode_values
    from ringo.lib.request.helpers import decode_values
    encoded = encode_values(data)
    decoded = decode_values(encoded)
    assert decoded == data
