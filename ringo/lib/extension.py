"""
Extensions are external pluggable modules and a option to add generic
functionallity to the application in a dynamic way.

In contrast to modules, extensions are generic and should not implement
application specific stuff. Extensions should be used to create
pluggable modules with generic functionallity which can be usefull for
all kind of applications. An example might be an appointment extensions
which allows the user to extend the application with an appointment
feature.

Extension can be Registered to an application by adding the extentions
in the `extensions` list located in the `modul/__init__.py` file. As
soon as the application is started the extension will be registered.
To unregister a extension simply remove the extension from the
`extentions` list.

.. note::
    For extensions which modifies the datamodel of the application a
    seperate model migration is needed on registration and
    unregistration of the extension. (See alembic and ringo-admin
    documentation).

For more information on how to create and register extensions please
refer to the :ref:`development` part of the documentation.

"""
import logging
import sqlalchemy as sa
import transaction
from ringo.lib.sql.db import DBSession
from ringo.model.modul import ModulItem, ACTIONS

log = logging.getLogger(name=__name__)


def _configure_actions(modul, config, actions, dbsession):
    """Will configure the configured actions of the modul in the
    database. The function will create and delete actions depending of
    the current modul configuration.

    :modul: Modul item of the extension
    :config: Extension configuration as a dictionary
    :actions: List of ActionItems
    :dbsession: Database session
    """
    # Add custom actions to the global ACTION dictionary
    if actions is None:
        actions = []
    for action in actions:
        ACTIONS[action.name.lower()] = action

    new_actions = config.get("actions") or []
    old_actions = [action.name.lower() for action in modul.actions]
    delete_actions = (set(old_actions) - set(new_actions))
    add_actions = (set(new_actions) - set(old_actions))
    for name in delete_actions:
        log.debug("Deleting action %s from modul %s" % (name, modul))
        action = modul.get_action(name)
        if action:
            modul.actions.remove(action)
    for name in add_actions:
        log.debug("Adding action %s to modul %s" % (name, modul))
        action = ACTIONS.get(name)
        if action:
            modul.actions.append(action)
        else:
            log.error("Action %s is not known!" % (name))
    return modul


def _add_modul(config, actions, dbsession):
    """Method to add the modul entries for the extension in the
    database. This includes a entry in the modules table and the
    configured actions.

    :config: Extension configuration as a dictionary
    :actions: List of ActionItems
    :dbsession: Database session
    """
    # Set defaults
    name = config.get("name") + "s"
    clazzpath = config.get("clazzpath")
    str_repr = config.get("str_repr") or "%s|id"
    display = config.get("str_repr") or "hidden"
    label = config.get("label") or name
    label_plural = config.get("label_plural") or label

    # Add modul
    modul = ModulItem(name=name)
    modul.clazzpath = clazzpath
    modul.label = label
    modul.str_repr = str_repr
    modul.label_plural = label_plural
    modul.display = display
    # Configure actions
    modul = _configure_actions(modul, config, actions, dbsession)
    dbsession.add(modul)
    dbsession.flush()
    transaction.commit()
    log.debug("Adding new modul '%s'" % name)
    return modul


def register_modul(config, modul_config, actions=None):
    """Will register the given modul if it is not already present. This
    function gets called from  the inititialisation code in the
    extension.

    :config: Application config
    :modul_config: Extension configuration as a dictionary
    :actions: List of ActionItems
    """
    name = modul_config.get("name") + "s"
    # Load the modul
    try:
        modul = DBSession.query(ModulItem).filter(ModulItem.name == name).one()
    except sa.orm.exc.NoResultFound:
        modul = None
    if modul:
        log.info("Modul '%s' already registered" % modul_config.get('name'))
    else:
        modul = _add_modul(modul_config, actions, DBSession)
        log.info("Registered modul '%s'" % modul_config.get('name'))
    return modul


def unregister_modul(modul):
    """Will unregister the given modul. This means deleting the modul
    entry and all related actions. Note, that you will need to delete
    further datastructures on your own.
    """
    DBSession.delete(modul)
    transaction.commit()
    log.info("Unregistered modul '%s'" % modul.name)
