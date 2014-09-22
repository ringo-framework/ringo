from pyramid.scaffolds import PyramidTemplate

class BasicRingoTemplate(PyramidTemplate):
    _template_dir = 'basic'
    summary = 'Ringo basic project'


class RingoExtensionTemplate(PyramidTemplate):
    _template_dir = 'extension'
    summary = 'Ringo extension'
