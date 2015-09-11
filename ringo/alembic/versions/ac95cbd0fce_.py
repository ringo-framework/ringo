"""Inserting initial data

Revision ID: ac95cbd0fce
Revises: 99fda072ff9
Create Date: 2015-09-05 20:06:19.814067

"""

# revision identifiers, used by Alembic.
revision = 'ac95cbd0fce'
down_revision = '99fda072ff9'

from alembic import op
import sqlalchemy as sa


UPGRADE = """
INSERT INTO usergroups (name, description) VALUES ('admins', '');
INSERT INTO usergroups (name, description) VALUES ('users', '');
INSERT INTO modules (id, name, clazzpath, label, label_plural, description, str_repr, display, default_gid) VALUES (1,'modules','ringo.model.modul.ModulItem','Modul','Modules','','%s|name','admin-menu',NULL);
INSERT INTO modules (id, name, clazzpath, label, label_plural, description, str_repr, display, default_gid) VALUES (2,'actions','ringo.model.modul.ActionItem','Action','Actions','','%s (%s/%s)|name,modul,url','hidden',NULL);
INSERT INTO modules (id, name, clazzpath, label, label_plural, description, str_repr, display, default_gid) VALUES (3,'users','ringo.model.user.User','User','Users','','%s|login','admin-menu',NULL);
INSERT INTO modules (id, name, clazzpath, label, label_plural, description, str_repr, display, default_gid) VALUES (4,'usergroups','ringo.model.user.Usergroup','Usergroup','Usergroups','','%s|name','admin-menu',NULL);
INSERT INTO modules (id, name, clazzpath, label, label_plural, description, str_repr, display, default_gid) VALUES (5,'roles','ringo.model.user.Role','Role','Roles','','%s|name','admin-menu',NULL);
INSERT INTO modules (id, name, clazzpath, label, label_plural, description, str_repr, display, default_gid) VALUES (6,'profiles','ringo.model.user.Profile','Profile','Profiles','','%s %s|first_name,last_name','admin-menu',NULL);
INSERT INTO modules (id, name, clazzpath, label, label_plural, description, str_repr, display, default_gid) VALUES (14,'forms','ringo.model.form.Form','Form','Forms','','%s|title','admin-menu',NULL);
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (1, 1, 'List', 'list', 'icon-list-alt', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (2, 1, 'Read', 'read/{id}', 'icon-eye-open', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (3, 1, 'Update', 'update/{id}', 'icon-edit', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (4, 3, 'List', 'list', 'icon-list-alt', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (5, 3, 'Create', 'create', ' icon-plus', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (6, 3, 'Read', 'read/{id}', 'icon-eye-open', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (7, 3, 'Update', 'update/{id}', 'icon-edit', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (8, 3, 'Delete', 'delete/{id}', 'icon-trash', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (9, 4, 'List', 'list', 'icon-list-alt', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (10, 4, 'Create', 'create', ' icon-plus', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (11, 4, 'Read', 'read/{id}', 'icon-eye-open', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (12, 4, 'Update', 'update/{id}', 'icon-edit', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (13, 4, 'Delete', 'delete/{id}', 'icon-trash', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (14, 5, 'List', 'list', 'icon-list-alt', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (15, 5, 'Create', 'create', ' icon-plus', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (16, 5, 'Read', 'read/{id}', 'icon-eye-open', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (17, 5, 'Update', 'update/{id}', 'icon-edit', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (18, 5, 'Delete', 'delete/{id}', 'icon-trash', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (19, 6, 'List', 'list', 'icon-list-alt', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (20, 6, 'Read', 'read/{id}', 'icon-eye-open', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (21, 6, 'Update', 'update/{id}', 'icon-edit', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (22, 2, 'Export', 'export/{id}', 'icon-export', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (23, 2, 'Import', 'import', 'icon-import', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (24, 3, 'Export', 'export/{id}', 'icon-export', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (25, 3, 'Import', 'import', 'icon-import', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (26, 4, 'Export', 'export/{id}', 'icon-export', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (27, 4, 'Import', 'import', 'icon-import', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (28, 5, 'Export', 'export/{id}', 'icon-export', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (29, 5, 'Import', 'import', 'icon-import', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (30, 14, 'List', 'list', 'icon-list-alt', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (31, 14, 'Create', 'create', ' icon-plus', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (32, 14, 'Read', 'read/{id}', 'icon-eye-open', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (33, 14, 'Update', 'update/{id}', 'icon-edit', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (34, 14, 'Delete', 'delete/{id}', 'icon-trash', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (35, 14, 'Import', 'import', 'icon-import', '', false, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (36, 14, 'Export', 'export/{id}', 'icon-export', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (37, 6, 'Export', 'export/{id}', 'icon-export', '', true, 'primary', '');
INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) VALUES (38, 6, 'Import', 'import', 'icon-import', '', false, 'primary', '');
INSERT INTO roles (id, label, name, description, admin, gid, uid) VALUES (1, 'Users', 'user', '', false, NULL, NULL);
INSERT INTO roles (id, label, name, description, admin, gid, uid) VALUES (2, 'Administration', 'admin', '', true, NULL, NULL);
INSERT INTO nm_action_roles (aid, rid) VALUES (20, 1);
INSERT INTO nm_action_roles (aid, rid) VALUES (21, 1);
INSERT INTO user_settings (id, settings) VALUES (1, '{}');
INSERT INTO users (id, login, password, activated, activation_token, sid, last_login, default_gid, gid, uid) VALUES (1, 'admin', '5ebe2294ecd0e0f08eab7690d2a6ee69', true, '', 1, '2015-09-05 18:43:06.178858', NULL, NULL, NULL);
INSERT INTO profiles (id, first_name, last_name, gender, birthday, address, phone, email, web, uid, gid) VALUES (1, '', '', NULL, NULL, '', '', '', '', 1, NULL);
INSERT INTO nm_user_roles (uid, rid) VALUES (1, 2);
UPDATE roles SET uid = 1;
UPDATE roles SET gid = 1;
UPDATE usergroups SET uid = 1;
UPDATE usergroups SET gid = 1;
UPDATE users SET uid = 1;
UPDATE users SET gid = 1;
"""
DOWNGRADE = """
DELETE FROM profiles;
DELETE FROM users;
DELETE FROM nm_action_roles;
DELETE FROM actions;
DELETE FROM modules;
DELETE FROM usergroups;
"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###
    iter_statements(UPGRADE)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###
    iter_statements(DOWNGRADE)
