Filesystem
**********
Ringo is organised in the following file layout::

        .
        ├── alembic
        ├── docs
        └── ringo
           ├── lib
           ├── locale
           ├── model
           ├── scaffolds
           ├── scripts
           ├── static
           │   ├── bootstrap
           │   ├── css
           │   ├── images
           │   └── js
           ├── templates
           │   ├── auth
           │   ├── default
           │   ├── internal
           │   ├── mails
           │   └── users
           ├── tests
           ├── teens
           └── views
               ├── forms
               └── tables

alembic
   Migration scripts for the database.
docs
   Documentation of ringo. This documentation.
ringo
   The ringo application.
ringo/lib
   Helper libraries. lenderers, validators, security related functions.
ringo/locale
   i18n Internationalisation
ringo/model
   Models for users, usergroups, modules, roles etc.
ringo/scaffolds
   A scaffolds includes the boilerplate code to create a ringo based application.
ringo/scripts
   Administration commands and scripts.
ringo/static
   Static files like images or CSS and JS scripts.
ringo/templates
   Templates for various parts of the application. Templates in the internal
   folder are used internally by customs form or overview renderers. The
   default folder has the templates for default CRUD actions and confirmation dialogs.
ringo/tests
   Unit tests and behaviour driven tests. See :ref:`tests` for more details.
ringo/tweens
   Middleware like code. Used to modify headers in response objects.
ringo/views
   Views with the business logic for the application. 
ringo/views/forms
   Configuration of forms for each modul.
ringo/views/tables
   Configuration of overview tables for each modul.

