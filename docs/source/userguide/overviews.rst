********************
Overviews and Search
********************

.. _userguide_overviews:

Overviews
=========
Each modul has an overview page which lists all items of the modul. Each
overview provides the following functionality:

 1. Sorting
 2. Searching
 3. Bundled Actions

.. image:: ../screenshots/ui/search.png

To open one of the shown items in the overview you can click simple somewhere
in the row. The item will be opened in read mode. Note that you need to click
on the row and not on the value as this triggers a search. See more details below.


Sorting
-------
The header of the overview table is clickable to sort the listing on the
selected header. Clicking on the header toggles between ascending and
descending sorting. A small icon shown on which column the sorting was done.

Bundled actions
---------------

Search
======
The search is based on the visible values in the overview. That means you can
search for anything which is displayed in one of the columns. If the search
string matches at least one value in the column the item will be found and
displayed in the overview. Optionally you can select a specific column
to restrict the search an this column. On default the search is done
over all visible columns.

.. hint::
   You can also a search by clicking on the literal value in a column. This
   will trigger a new search for the clicked value in the corresponding
   column.

The search is stackable. This way you can narrow down your search by refining
your search by doing another search on the last search result. You can see how
many filters are currently applied next to the options drop-down.
To pop the last filter from the search stack simply enter a empty search.
To reset the whole search stack at once select the "Reset current search
filter" option from the options drop-down.

You can save your current search under a user defined query name and make it
available for later use. This becomes very handy if you are in the need of
some often used predefined searches.

.. note::
   You can only save a search which actually has at least one found item in
   the search result. Further the name for your query must be unique. It is
   not possible to edit a saved search. You need to save it under a new name.

To save the current search stack, select the "Search current search stack"
option from the options drop-down. You can enter your desired name for the
query and then save it in your user settings.
The saved searches are then listed in the options dropdown. You can delete a
saved search by clicking on the cross symbol next to each filter.

Using operators
---------------
Operators can be put as first word of the search term. The operator changes
the search mode in the way that the search will evaluate the search term with the values in the list using the given operator. This can become handy to find items which to not match a certain criteria or for searches on dates.

.. note::
   Operators do not work in connection with regular expressions.

The follwing operators are supported:

 * "<" lower than
 * "<=" lower equal than
 * ">" greater than
 * ">=" greater equal than
 * "==" equal
 * "!=" not equal

Examples:

 * "== Foo" will match all values with match exactly the valie Foo.
 * "< 2015-04-01" will match all values lower than 2015-04-01. This is usefull for search on dates. Please limit the search on the datefield to get reasonable result.

Using regular expressions
-------------------------
You can change the behavior of the search by enabling regular expressions as
search term. To enabled regular expressions select "Enable regexpr in search"
from the search options menu. The search button will now have an additional
"+" sign to indicate that the regular expression is enabled.

For more details on regular expressions see `Regular Expression HOWTO <https://docs.python.org/2/howto/regex.html>`_
