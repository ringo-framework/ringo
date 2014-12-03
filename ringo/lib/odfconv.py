from tempfile import NamedTemporaryFile
import logging
from py3o.renderers.pyuno.main import Convertor
from ringo.lib.cache import CACHE_MISC

log = logging.getLogger(__name__)


def setup(config):
    #  TODO: Load configuration for the python path which is needed for
    #  pyuno () <2014-12-03 20:32>
    pythonpath = None
    CACHE_MISC.set("converter", Converter(python=pythonpath))

def get_converter():
    return CACHE_MISC.get("converter")

class Converter(object):

    """Converter to convert ODF documents into other formats like pdf,
    xls, doc."""

    def __init__(self, python=None):
        self._converter = Convertor(python=python)
        try:
            self._converter._init_server()
            self._available = True
            log.info("Office Server for document conversation started.")
        except:
            log.warning("Office not started. Converter is not"
                        "available. Forgot to install Libreoffice?")
            self._available = False

    def is_available(self):
        return self._available

    def _get_infile(self, data):
        infile = NamedTemporaryFile()
        infile.write(data)
        infile.seek(0)
        return infile

    def convert(self, data, format="ods", update=True):
        """Returns the infile into the given format.

        :data: Loaded data from the source file
        :format: String of the output format
        :returns: Converted data.

        """
        infile = self._get_infile(data)
        outfile = NamedTemporaryFile()
        self._converter.convert(infile.name, outfile.name, format, update)
        result = outfile.read()
        infile.close()
        outfile.close()
        return result
