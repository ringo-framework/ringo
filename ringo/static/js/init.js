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
});
