function checkAll(checkId) {
  var inputs = document.getElementsByTagName("input");
  for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].type == "checkbox" && inputs[i].name == checkId) {
          if(inputs[i].checked == true) {
              inputs[i].checked = false ;
          } else if (inputs[i].checked == false ) {
              inputs[i].checked = true ;
          }
      }
  }
  check(checkId);
}

function checkOne(checkId, element) {
  var inputs = document.getElementsByTagName("input");
  for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].type == "checkbox" && inputs[i].name == checkId && inputs[i].value != element.value) {
        inputs[i].checked = false;
      }
  }
  check(checkId);
}

function check(checkId, element) {
  $(element).attr('checked', !$(element).attr('checked'));
  /* Will add a hidden checkbox with no value in case no other checkbox is
   * selected. This is needed to items with no selection, as in this case html
   * does not submit the checkbox field at all. So this is a hack to simulate
   * an empty selection */
  var inputs = $("input[type='checkbox'][name="+checkId+"]");
  var selected = inputs.filter(":checked");
  if (selected.length == 0 && inputs.length > 0) {
    $(inputs[0]).after('<input id="'+checkId+'-empty" style="display:none" type="checkbox" value="" name="'+checkId+'" checked="checked"/>');
  } else {
    $("#"+checkId+"-empty").remove();
  }
}
