var language = getLanguageFromBrowser();

function getDTLanguage() {
    if (language.indexOf("de") >= 0) {
        return "german"
    } else {
        return "default";
    }
}
var opts = {
  lines: 9, // The number of lines to draw
  length: 21, // The length of each line
  width: 3, // The line thickness
  radius: 3, // The radius of the inner circle
  corners: 0, // Corner roundness (0..1)
  rotate: 30, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb or array of colors
  speed: 0.8, // Rounds per second
  trail: 54, // Afterglow percentage
  shadow: true, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'spinner', // The CSS class to assign to the spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: '50%', // Top position relative to parent
  left: '50%' // Left position relative to parent
};
var spinner = new Spinner(opts).spin();
$( document ).ready(function() {
    $('.dialog').modal({
        backdrop: "static"
    });
    $('.fade.out').delay(3 * 1000).fadeOut();
    $('#savequerydialog').modal({
        show: false,
        backdrop: "static"
    });
    $('#logoutWarning').modal({
        show: false,
        backdrop: "static"
    });
    $('.datatable-paginated').dataTable( {
           "oLanguage": {
                "sUrl": "/static/js/datatables/i18n/"+getDTLanguage()+".json"
           },
           "bPaginate": true,
           "sPaginationType": "full_numbers",
           "bLengthChange": true,
           "bFilter": true,
           "bSort": true,
           /* Disable initial sort */
           "aaSorting": [],
           "bInfo": true,
           "bAutoWidth": true
     });
    $('.datatable-simple').dataTable( {
           "oLanguage": {
                "sUrl": "/static/js/datatables/i18n/"+getDTLanguage()+".json"
           },
           "bPaginate": false,
           "bLengthChange": false,
           "bFilter": true,
           "bSort": true,
           /* Disable initial sort */
           "aaSorting": [],
           "bInfo": false,
           "bAutoWidth": false
    });
    $('.datatable-blank').dataTable({
          "oLanguage": {
               "sUrl": "/static/js/datatables/i18n/"+getDTLanguage()+".json"
          },
          "bPaginate": false,
          "bLengthChange": false,
          "bFilter": false,
          "bSort": true,
          /* Disable initial sort */
          "aaSorting": [],
          "bInfo": false,
          "bAutoWidth": false
    });
    // Add form-controll class to search fields, needed for BS3
    $('.dataTables_filter input').addClass("form-control");
    $('.dataTables_length select').addClass("form-control");
    // Make the formbar navigation sticky when the user scrolls down.
    var width = $( document ).width();
    if ( width > 768 ) {
        $('.formbar-outline').affix({
           offset: {
           //top: $('header').height()
           top: 140 }
        });
    }
    // Enable tooltips on the text elements in datatables 
    //$('#data-table td a').tooltip(
    //   {
    //       delay: { show: 50, hide: 500 }
    //   }
    //);
    // First hide all main panes
    $('#context-menu-options a').click(function() {
       var pane = $(this).attr('href').split('#')[1];
       $('.main-pane').hide();
       $('#'+pane).show();
    });
    $('#pagination-size-selector').change(function() {
        var value = $(this).val();
        var url = $(this).attr('url') + "?pagination_size=" + value;
        window.open(url,"_self");
    });
    $("a.modalform").click(openModalForm);
        $("a.modalform").click(function(event) {
            event.preventDefault();
            return false;
    });

});

function logoutCountdown(time, url) {
    var warning = $.timer(function() {
      $("#logoutWarning").modal("show");
    });
    warning.set({ time : time/100*95*1000, autostart : true });
    var logout = $.timer(function() {
        location.href=url;
    });
    logout.set({ time : time*1000-500, autostart : true });
}

function openModalForm(event) {
  var element = event.target;
  console.log(element);
  var url = $(element).attr("href");
  console.log(url);
  // Load page
  var page = $.ajax({
      url: url,
      async: false
  });
  // now strip the content
  var title = $("h1", page.responseText).text();
  var content = $("#form", page.responseText);
  // Better leave url and attach some kind of javascript action to load the
  // result of the POST into the popup.
  $("form", content).attr("action", url);
  // Set title and body of the popup
  $("#modalform .modal-title").text(title);
  $("#modalform .modal-body").html(content);
  // Show the popup
  $("#modalform").modal("toggle");
}
