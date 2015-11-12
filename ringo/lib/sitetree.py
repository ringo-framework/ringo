#!/usr/bin/env python
# encoding: utf-8
from ringo.lib.helpers.misc import get_open_url, get_item_modul


"""Modul to handle the sitetree structure of the application in order to
render a breadcrumb widget.

The sitemap is a dictionary which builds a tree hirachy of the
application. It should have the following structure::


    {
        "key": {"parent_site": $parent_key,
                "parent_item": $attritute_of_item_which_links_to_parent
                "display_item": $alternative_item_to_display,
                "display_format": "Prefix of {item}"
                "actions": {'foo': 'Foo description'}}
        ...
    }

**key**
    The *key* of the dictionary is the base *URL* of the modul.  E.g Calling
    the edit page of the user modul have the URL users/edit/1.  In this
    example *users* is the base URL. If this url is called the the entry
    point to build the breadcrumbs will be the entry in the dictionary named
    users. If no key can be found in the dictionary which named like the
    base url than no breadcrumbs can be build and no breadcrumbs are visible
    in the UI. This way you can configure breadcrumbs on only selected
    pages.

**parent_site**
    The parent_site refers to a *key* of the parent site in the sitemap.
    It must match the name of a key in the dictionary.

**parent_item**
    The item defines the name of the attribute of the currently loaded
    item (in the model) which links to the parent item in the models
    hirachy tree. Think of haven in A -> B -> C relation in your model
    and you call the page to edit C. Then item refers to the name of C's
    attribute which links to B.

**display_item**
    Usually the str representation of the related item is used as
    breadcrumb element. Setting the display_item allows to define the
    name of an attribute to an alternative value to display.

**display_format**
   Additionally to the alternative item to display you can define the *format*
   on how to display the item. This can include some addtional string to
   give some more context information.

**actions**
   You can optionally define some additional actions which should be
   displayed in the breadcrumbs. On default only the create action will
   be show as for all other actions the context is clearly defined by
   the header of the current page. If you define some custom actions for
   a modul it isn't handled by default. So if you call the custom action
   the breadcrumbs will only show the default breadcrumbs. As the last
   entry in the breadcrumbs does not provide a link you might be missing
   a way back to where you come from. To prevent this behaviour you can
   define addtional actions which will be shown.
"""

site_tree_branches = []

# Default ringo sitetree is empty. Other applications can add their part
# of a sitetree into the site_tree_branches global variable.
ringo_site_tree = {}
site_tree_branches.append(ringo_site_tree)


def url(request, item):
    if item:
        return get_open_url(request, item)
    return None


def walk_site_tree(st, el, item, request):
    """Helper method to get the elements from the sitetree.

    :st: Sitetree dictionary
    :el: Current page (key in dictionary)
    :item: currently loaded item (if loaded)
    :request: current request
    :returns: List of element used to render to breadcrumbs.

    """
    path = []
    site = st[el]

    # Get action. Currently using routes the action is always the
    # penultimate element in the URL.
    path_elements = request.path.split("/")
    if len(path_elements) > 1:
        action = site.get("actions", {}).get(path_elements[-2])
    else:
        action = None

    parent_site = site.get("parent_site")
    parent_item_attr = site.get("parent_item")

    # Check if an other item should be displayed as the item defined in the
    # item attribute. Other wise display the item.
    display_item_attr = site.get("display_item")

    if action:
        path.append((action, None))

    if display_item_attr:
        display_item = getattr(item, display_item_attr)
        display_str = site.get("display_format", "%{item}s")
        path.append((display_str.format(item=display_item),
                     url(request, item)))
    else:
        path.append((unicode(item), url(request, item)))

    if parent_site:
        parent_item = getattr(item, parent_item_attr)
        path.extend(walk_site_tree(st, parent_site, parent_item, request))
    return path


def build_breadcrumbs(request, sitetree):
    """Will return a list of breadcrumbs based on the current request
    and the given sitetree.

    :request: Current request
    :sitetree: dictionary of the sitetree
    :returns: List of breadcrumbs.
    """
    # Only build the sitemap if the modul is part of the sitemap and an
    # item is actually selected
    from ringo.views.request import get_item_from_request
    pip = request.path_info_peek()
    if pip in sitetree:
        if request.matchdict:
            item = get_item_from_request(request)
            path = walk_site_tree(sitetree, pip, item, request)
            request.session["breadcrumbs"] = path
            request.session.save()
        else:
            if request.path.find("create") > -1:
                item = get_item_from_request(request)
                modul = get_item_modul(request, item)
                path = request.session.get("breadcrumbs", [])
                return list(reversed(path)) + [(modul.get_label(), None)]
            # Reset the breadcrumbs for any other url. This means the
            # breadcrumbs are reseted every time the user calls an
            # overview page e.g. As the overview pages are usually the
            # entry point for a new working proccess the previous
            # context is lost so the breadcrumbs are.
            request.session["breadcrumbs"] = []
            return []
    else:
        request.session["breadcrumbs"] = []
        return []

    path = list(reversed(path))
    if path:
        path[-1] = (path[-1][0], None)
    return path
