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
var timer;
var spinner = new Spinner(opts);
var spinner_timer = 800; //threshold in ms after spinner starts

$( document ).ready(function() {
    $(':button').not('[data-toggle="dropdown"], [type="reset"], [target="_blank"]').click(function () {
        var hide_spinner = $(this).hasClass("nospinner") == true;
        if (hide_spinner == false) {
            startSpinner(spinner_timer);
        }
    });
    $('[data-toggle="tooltip"]').tooltip();
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

    /* Datatable initialisation */
    var application_path = getApplicationPath();
    var language = getDTLanguage(getLanguageFromBrowser());
    if (language == 'german') {
        // https://datatables.net/blog/2014-12-18 using moment.js
        $.fn.dataTable.moment( 'DD.MM.YYYY' );
        $.fn.dataTable.moment( 'DD.MM.YY' );
    }
    $('.datatable-paginated').dataTable( {
           "oLanguage": {
                "sUrl":  application_path + "/ringo-static/js/datatables/i18n/"+language+".json"
           },
           "bPaginate": true,
           "sPaginationType": "full_numbers",
           "bLengthChange": true,
           "bFilter": true,
           "bSort": true,
           /* Disable initial sort */
           "aaSorting": [],
           "bInfo": true,
           "bAutoWidth": true,
           "fnInitComplete":onDTTableRendered
     });
    // This overview is used for the simple overview page!
    $('.datatable-simple').dataTable( {
           "oLanguage": {
                "sUrl": application_path + "/ringo-static/js/datatables/i18n/"+language+".json"
           },
           "bPaginate": false,
           "bLengthChange": false,
           "bFilter": true,
           "bSort": true,
           /* Disable initial sort */
           "aaSorting": [],
           "bInfo": true,
           "bAutoWidth": false,
           "fnInitComplete":onDTTableRendered,
           "dom": '<"search-widget"<"row"<"col-md-6"f><"col-md-6"<"pull-right"i>>>>'
    });
    $('.datatable-blank').dataTable({
          "oLanguage": {
               "sUrl": application_path + "/ringo-static/js/datatables/i18n/"+language+".json"
          },
          "bPaginate": false,
          "bLengthChange": false,
          "bFilter": false,
          "bSort": true,
          /* Disable initial sort */
          "aaSorting": [],
          "bInfo": false,
          "bAutoWidth": false,
          "fnInitComplete":onDTTableRendered
    });
    // Make the formbar navigation sticky when the user scrolls down.
    var width = $( document ).width();
    if( width > 992) {
      $('.formbar-outline').affix({
        offset: {top: 208 }
      });
    } else if (width > 768 ){
      $('.formbar-outline').affix({
        offset: {top: 236 }
      });
    } else {} 
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
        startSpinner(spinner_timer);
        window.open(url,"_self");
    });
    $("a.modalform").click(openModalForm);
        $("a.modalform").click(function(event) {
            event.preventDefault();
            return false;
    });

    // Check the initial values of the form and warn the user if the leaves
    // the page without saving the form.
    var DirtyFormWarningOpen = false;
    $('form').each(function() {
        $(this).data('initialValue', $(this).serialize());
    });
    function openDirtyDialog(url, hide_spinner, event) {
        isDirty = false;
        $('form').each(function () {
            if($(this).data('initialValue') != $(this).serialize()){
                isDirty = true;
            }
        });
        if((isDirty == true) && (DirtyFormWarningOpen == false)) {
            var dialog = $("#DirtyFormWarning");
            $('#DirtyFormWarningProceedButton').attr("href", url);
            // If the URL does not begin with "#" then show the dialog.
            if (url && url.indexOf("#") != 0) {
                $(dialog).modal("show");
                DirtyFormWarningOpen = true;
		event.preventDefault();
                return false;
            }
            return true;
        }
        hash_i = url.indexOf("#");
        has_hash = (hash_i  == -1) == false;
        if (((location.pathname != url) && url != "") && (has_hash == false) && (hide_spinner == false)) {
            startSpinner(spinner_timer);
        }
    }
    $('a').not('[href^="mailto:"], [target="_blank"]').click(function(event) {
        var element = event.target;
        var url = $(element).attr("href");
        var hide_spinner = $(element).hasClass("nospinner") == true;
        openDirtyDialog(url, hide_spinner, event);
        
    });
    $('.link').not('a').click(function(event) {
        var element = event.target;
        var parentWithUrl = $(element).parents('[data-link]');
        var url = parentWithUrl.data('link');
        var hide_spinner = $(element).hasClass("nospinner") == true;
        openDirtyDialog(url, hide_spinner, event);
    });
    $('#DirtyFormWarningCancelButton').click(function(event) {
            var dialog = $("#DirtyFormWarning");
            $(dialog).modal("hide");
            DirtyFormWarningOpen = false;
            event.preventDefault();
            return false;
    });
    $('tbody').on("click", "tr", function(elem){
        var link=$(elem.currentTarget).data("link");
        if(link && elem.target.tagName!=="INPUT" && (typeof isDirty === "undefined" || isDirty == false)) {
           location.href=link;
        }
    });
});

function onDTTableRendered() {
    // Add form-controll class to search fields, needed for BS3
    $('.dataTables_filter input').addClass("form-control");
    $('.dataTables_length select').addClass("form-control");
}

$( window ).unload(function() {
    stopSpinner();
});


function stopSpinner() {
    if ($('#spinner').data('spinner') != undefined){
        $('#spinner').data('spinner').stop();
    }
    clearTimeout(timer);
}

function startSpinner(x) {
    stopSpinner();
    timer = setTimeout(function(){
            $('#spinner').spin(spinner.el);
    }, x);
}

function openModalForm(event) {
  var element = event.target;
  var url = $(element).attr("href");
  // Load page
  var page = $.ajax({
      url: url,
      async: false
  });
  // now strip the content
  var title = $("h1", page.responseText).text();
  var content = $(".formbar-form", page.responseText);
  // Better leave url and attach some kind of javascript action to load the
  // result of the POST into the popup.
  $("form", content).attr("action", url);
  // Set title and body of the popup
  $("#modalform .modal-title").text(title);
  $("#modalform .modal-body").html(content);
  // Show the popup
  $("#modalform").modal("toggle");
}
