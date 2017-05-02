<%def name="render_default_xxx()">
  <input id="${table_id}_casesensitive" type="checkbox" value="1"/><label for="${table_id}_casesensitive">${_('Case sensitive')}</label>
</%def>

function on${table_id}TableRendered(settings, json) {
  var api = $.fn.dataTable.Api(settings);
  onDTTableRendered();
  % for fltr in tableconfig.get_filters():
  <% id = table_id + "_" + fltr.field %>
  $('.search-filters').append('<div class="checkbox searchfilter" style="position:relative;top:8px;"><label><input class="checkobx" style="position:relative;top:1px;" id="${id}_${_(fltr.expr)}" type="checkbox" value="${_(fltr.expr)}" name="${id}" ${fltr.active and 'checked="checked"'}>${_(fltr.label)}</label></div>');
  % endfor
  % for fltr in tableconfig.get_filters():
    % if tableconfig.is_bundled() and len(bundled_actions) > 0:
    var column_${tableconfig.get_column_index(fltr.field)} = api.column(${tableconfig.get_column_index(fltr.field)+1});
    % else:
    var column_${tableconfig.get_column_index(fltr.field)} = api.column(${tableconfig.get_column_index(fltr.field)});
    % endif
  % if fltr.type == "checkbox":
  $('#${table_id}_${fltr.field}_${fltr.expr}').change(function() {
    filter_${table_id}_${fltr.field}(this);
  });
  function filter_${table_id}_${fltr.field}(field) {
    var filters = new Array();
    $('input[name="${table_id}_${fltr.field}"]').each( function() {
      if ($(this).is(':checked')) {
        filters.push( $(this).val() );
      }
    } )
    column_${tableconfig.get_column_index(fltr.field)}
    .search(filters.join('|'), ${fltr.regex}, ${fltr.smart}, ${fltr.caseinsensitive})
    .draw();
  };
  filter_${table_id}_${fltr.field}($('#${table_id}_${fltr.field}'));

  % endif
  % endfor
}  


$( document ).ready(function() {
  var ${table_id} = $('#${table_id}').DataTable( {
    "oLanguage": {
    "sUrl":  getApplicationPath() \
             + "/ringo-static/js/datatables/i18n/" \
             + getDTLanguage(getLanguageFromBrowser()) \
             + ".json"
    },

    ## Render pagination settings
    % if tableconfig.is_paginated():
      "bPaginate": true,
      "bLengthChange": false,
    % else:
      "bPaginate": false,
    % endif

    ## Render sorting settings
    % if tableconfig.is_sortable():
      "bSort": true,
      % if tableconfig.is_bundled() and len(bundled_actions) > 0:
        "order": [[${tableconfig.get_column_index(tableconfig.get_default_sort_column())+1}, "${tableconfig.get_default_sort_order()}"]],
      % else:
        "order": [[${tableconfig.get_column_index(tableconfig.get_default_sort_column())}, "${tableconfig.get_default_sort_order()}"]],
      % endif
    % else:
      "bSort": false,
    % endif

    ## Render filter settings
    % if tableconfig.is_searchable():
      "bFilter": true,
    % else:
      "bFilter": false,
    % endif

    ## Render info field
    % if tableconfig.get_settings().get("show-info", True):
      "bInfo": true,
    % else:
      "bInfo": false,
    % endif

   "bAutoWidth": false,
   "fnInitComplete":on${table_id}TableRendered,
   "dom":
   '<"search-widget hidden-print"<"row"<"col-md-12 search-filters"f>>><"row"<"col-md-12"<"pull-right"i>>>',
   "columns": [
      % if bundled_actions:
        {
          "visible": true,
          "searchable": false
        },
      % endif
      % for field in tableconfig.get_columns(request.user):
        {
          "visible":  
            % if field.get('visible', True):
              true,
            % else:
              false,
            % endif
          "searchable":  
            % if field.get('searchable', True):
              true
            % else:
              false
            % endif
        },
      % endfor
   ]
  });
});

