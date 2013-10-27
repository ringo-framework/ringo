$( document ).ready(function() {
    $('.dialog').modal();
    $('.alert').delay(3 * 1000).fadeOut();
    $('#savequerydialog').modal({
      show: false
    });
     $('.datatable-simple').dataTable(
        {
           "bPaginate": false,
           "bLengthChange": false,
           "bFilter": true,
           "bSort": true,
           "bInfo": false,
           "bAutoWidth": false
        }
     );
     $('.datatable-blank').dataTable(
        {
           "bPaginate": false,
           "bLengthChange": false,
           "bFilter": false,
           "bSort": true,
           "bInfo": false,
           "bAutoWidth": false
        }
     );
     // Add form-controll class to search fields, needed for BS3
     $('.dataTables_filter input').addClass("form-control");
     $('.dataTables_filter input').addClass("form-control");

     // Make the formbar navigation sticky when the user scrolls down.
     $('.formbar-outline').affix({
        offset: {
        //top: $('header').height()
        top: 185 }
     });
});
