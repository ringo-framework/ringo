$( document ).ready(function() {
    $('.dialog').modal();
    $('.alert').delay(3 * 1000).fadeOut();
    $('#savequerydialog').modal({
        show: false
    });
    $('.datatable-pageinated').dataTable( {
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

});
