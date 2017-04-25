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
 * checks if any form in the DOM is dirty, bypassing form and input tags with
 * the attribute 'no-dirtyable'. Returns true if some change is found
 * (e.g. < form no-dirtyable>...< /form>)
 * (e.g. < input type='checkbox' no-dirtyable />)
 */
function checkDirtyForms () {
    var forms = document.getElementsByTagName('FORM');
    Array.from(forms).forEach(function(form) {
        if (!form.hasAttribute("no-dirtyable")) {
            var childnodes = form.childNodes;
            childnodes.forEach( function(node) {
                if (node.tagName === 'INPUT') {
                    if (!node.hasAttribute("no-dirtyable")) {
                        switch (node.type) {
                            case "checkbox":
                            case "radio":
                                if (node.checked != node.defaultChecked) {
                                    return true;
                                }
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
                else if (node.tagName === 'TEXTAREA') {
                    if (!node.hasAttribute("no-dirtyable")) {
                        if (node.value != node.defaultValue){
                            return true;
                        }
                    }
                }
                else if (node.tagName === 'SELECT') {
                    if (!node.hasAttribute("no-dirtyable")) {
                        if (node.options[node.selectedIndex].defaultSelected){
                            return true;
                        }
                    }
                }
            });
        }
    });
    return false;
}
