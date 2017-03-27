## Only render the button if the URL does contain any sensefull content. '#'
## is the default value if no URL can be generated because of missing
## permissions e.g.
% if url and url != '#':
<a href="${url}" class="btn btn-default btn-block formbar-linkfield ${field.renderer.css}" target="${field.renderer.target or '' }" ${field.renderer.openmodal == 'true' and 'modalform'}">${_(link_text)}</a>
% endif
