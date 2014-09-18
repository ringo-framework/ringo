import os
from sqlalchemy.ext.declarative import declarative_base
from ringo.lib import helpers

# Define enabled ringo extenstion here. Extensions will be initialised
# on application startup.
extensions = [
]

# Global declarative base class.
Base = declarative_base()

# Dynamically import all model files and extensions here to have the
# model available in the sqlalchemy metadata. This is needed for the
# schema migration with alembic. Otherwise the migration will produce
# many table drops as the tables of the models are not present in the
# metadata
model_dir = os.path.dirname(os.path.realpath(__file__))
modul_files = [f for f in os.listdir(model_dir) if f.split(".")[-1] == "py"]
for model in modul_files:
    helpers.dynamic_import(__name__ + "." + model.split(".")[0])
for extension in extensions:
    helpers.dynamic_import(extension + ".model")
