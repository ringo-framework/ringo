/* Method to get the preferred user language. As there is no reliable
 * way to get this information accross all browsers the language is set
 * by the server in a meta variable in the html header */
function getLanguageFromBrowser() {
    return $("meta[name='client_language']").attr("content");
}

function getApplicationPath() {
    return $("meta[name='application_path']").attr("content");
}

function getDTLanguage(language) {
    /* Helper method to translate the language setting of the browser into
    the equivalent option needed for the data tables plugin to load the
    correct language setting. */
    if (language.indexOf("de") >= 0) {
        return "german"
    } else {
        return "default";
    }
}

/**
 * checks if any formbar-form is dirty, bypassing form and input tags with
 * the attribute 'no-dirtyable'. Returns true if some change is found
 * (e.g. < form no-dirtyable>...< /form>)
 * (e.g. < input type='checkbox' no-dirtyable />)
 */
function checkDirtyForms () {
    var forms = $("div.formbar-form").find("form");
    var forms_as_arr = Array.from(forms);
    for (var i = 0; i < forms_as_arr.length; i++){
        form = forms_as_arr[i];
        if (!form.hasAttribute("no-dirtyable") && !form.hasClass("no-dirtyable")) {
            var elements = form.getElementsByTagName('INPUT');
            var elements_as_arr = Array.from(elements);
            for (var j = 0; j < elements_as_arr.length; j++) {
                var node = elements_as_arr[j];
                if (!node.hasAttribute("no-dirtyable")) {
                    switch (node.type) {
                        case "checkbox":
                        case "radio":
                            if (node.checked != node.defaultChecked) {
                                return true;
                            }
                            break;
                        case "search":
                            // search buttons aren't usually submittable
                            break;
                        default:
                            //TODO check if all other input types are
                            // covered (even html5 ones)
                            if (node.value != node.defaultValue){
                                return true;
                            }
                    }
                }
            }
            elements = form.getElementsByTagName('TEXTAREA');
            elements_as_arr = Array.from(elements);
            for (var j = 0; j < elements_as_arr.length; j++) {
                var node = elements_as_arr[j];
                if (!node.hasAttribute("no-dirtyable")) {
                    if (node.value != node.defaultValue){
                        return true;
                    }
                }
            }
            elements = form.getElementsByTagName('SELECT');
            elements_as_arr = Array.from(elements);
            for (var j = 0; j < elements_as_arr.length; j++) {
                var node = elements_as_arr[j];
                if (!node.hasAttribute("no-dirtyable")){
                    try {
                        if (!node.options[node.selectedIndex].defaultSelected){
                            return true;
                        }
                    }
                    catch (err) {
                        //there may be no options at all, or nothing selected
                        //TODO: check if there are cases this could mean "dirty form"
                    }
                }
            }
        }
    };
    return false;
}
