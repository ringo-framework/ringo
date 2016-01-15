"""
Extensions are external plugable modules. They are used to add generic
functionallity to the application in a dynamic way.

In contrast to modules, extensions do not implement application specific
stuff, but are generix with functionallity which is usefull for all kind
of applications. An example might be an appointment extensions which
allows to extend the application with an appointment feature.

For more information on how to create and register extensions please
refer to the :ref:`extensions` part of the documentation.

Extension may extend the existing database and adds tables to save data
(e.g appointments and relations of appointments to users.) or they are
lightweight and just provides some functionallity like anonymisation.

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
    name = config.get("name")
    clazzpath = config.get("clazzpath")
    str_repr = config.get("str_repr") or "%s|id"
    display = config.get("display") or "hidden"
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


def _load_modul_by_name(session, modulname):
    try:
        # FIXME:
        # Compatibilty mode. Older versions of Ringo added a 's' to the
        # extensions modul name as Ringo usally uses the plural form.
        # Newer versions use the configured extension name. So there
        # might be a mixture of old and new modul names in the database.
        # This code will handle this. (ti) <2016-01-04 13:50>
        return session.query(ModulItem)\
               .filter(sa.or_(ModulItem.name == modulname,
                              ModulItem.name == modulname + 's'))\
                .one()
    except sa.orm.exc.NoResultFound:
        return None


def register_modul(config, modul_config, actions=None):
    return check_register_modul(config, modul_config, actions)


def check_register_modul(config, modul_config, actions=None):
    """This method is used by extension to register their modul with a
    given config in the application. This function will check if the
    modul is already registered. Registered in this context means that
    the modul has an entry in the modules table

    If it is not registered it will show a warning message. So the
    function really does not register the modul but check if it is
    registered.

    :config: Application config
    :modul_config: Extension configuration as a dictionary
    :actions: List of ActionItems
    :returns: ModulItem or None
    """

    modulname = modul_config.get('name')
    modul = _load_modul_by_name(DBSession, modulname)
    if modul:
        log.info("Extension '%s' OK" % modulname)
    else:
        log.warning("Extension '%s' is missing a entry in DB. "
                    "Missing migration?" % modulname)
    return modul


def check_unregister_modul(modul, extensions):
    """Will check if there is a entry in the moduls table for an
    extension which is not currently added in the application and can
    therefor be deleted. If there is such an entry a warning is logged.
    """
    app_name = modul.clazzpath.split(".")[0]
    if app_name.find("ringo_") > -1 and app_name not in extensions:
        log.warning("Spare entry in DB for Extension '%s'. "
                    "Missing migration?" % modul.name)
