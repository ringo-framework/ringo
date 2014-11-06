$( document ).ready(function() {
    $('.dialog').modal();
    $('.fade.out').delay(3 * 1000).fadeOut();
    $('#savequerydialog').modal({
        show: false
    });
    $('#logoutWarning').modal({
        show: false
    });
    $('.datatable-pageinated').dataTable( {
           "oLanguage": {
                "sUrl": "/static/js/datatables/i18n/"+getLanguageFromBrowser()+".json"
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
                "sUrl": "/static/js/datatables/i18n/"+getLanguageFromBrowser()+".json"
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
               "sUrl": "/static/js/datatables/i18n/"+getLanguageFromBrowser()+".json"
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
    $('#pageination-size-selector').change(function() {
        var value = $(this).val();
        var url = $(this).attr('url') + "?pageination_size=" + value;
        window.open(url,"_self");
    });
    $("a.modalform").click(openModalForm);
        $("a.modalform").click(function(event) {
            event.preventDefault();
            return false;
    });
    $("td.modalform").click(openModalForm);
        $("td.modalform").click(function(event) {
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
  var target = $(element).attr("href");
  var url = null;
  if (target.indexOf("?") >= 0) {
    url = target + "&backurl=" + window.location;
  } else {
    url = target + "?backurl=" + window.location;
  }
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
