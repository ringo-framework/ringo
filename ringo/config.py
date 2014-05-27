import os
import pkg_resources

base_dir = pkg_resources.get_distribution("ringo").location
template_dir = os.path.join(base_dir, 'ringo', 'templates')
static_dir = os.path.join(base_dir, 'ringo', 'static')

# Directory with templates to generate views and models
modul_template_dir = os.path.join(base_dir, 'ringo', 'scripts', 'templates')
