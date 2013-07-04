$( document ).ready(function() {
    $('.dialog').modal();
    $('.alert').delay(3 * 1000).fadeOut();
    $('#savequerydialog').modal({
      show: false
    });
});
