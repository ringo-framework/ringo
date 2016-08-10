.. _usage_iexport:

*****************
Import and Export
*****************

Export configuration
--------------------
You can configure which fields and relations will be included in the export.
On default, if no configuration is provided all fields excluding the relations
will be exported.

The configuration is basically a JSON string. For the example we assume that
we want to export the users of ringo based application. In this export we just
need ceratain fields of the user object and want to add some of the users
profile data. Here is a example export configuration for this::

        ["id", "login", "password", {"profile": ["id", "uid", "email"]}]

This configuration is for exporting data in the users modul. So the first
fields in the configuration (id, login, password) refer to the user item. The
following dictionary will define the relation of the profile to the user. The
key in the dictionary must be named as the name of the relation in the model.
In this case it is named 'profile'. The following list define the fields of
the profile model which should be included in the export. This recursive
structure can be expanded to include further relations.
