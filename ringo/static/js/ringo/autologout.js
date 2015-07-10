// This global variable will be used to indicate if the logout warning is show in
// other scripts.
var logout_warning = false;
var logout_warning_timer = null;
var logout_call_timer = null;

function logoutCountdown(time, url) {
    logout_warning = false;
    if (logout_warning_timer == null) {
        // Warning
        logout_warning_timer = $.timer(function() {
            showLogoutWarning();
        });
        logout_warning_timer.set({ time : time/100*95*1000, autostart : true });
        // Call of logout page
        logout_call_timer = $.timer(function() {
            callLogoutPage(url)
        });
        logout_call_timer.set({ time : time*1000-500, autostart : true });
    } else {
        logout_warning_timer.reset(); 
        logout_call_timer.reset(); 
    }
}

function showLogoutWarning() {
    logout_warning = true;
    $("#logoutWarning").modal("show");
}

function callLogoutPage(url) {
    logout_warning = false;
    location.href=url;
}

$(document).ajaxComplete(function(event,request, settings){
    if (logout_warning_timer != null) {
        logout_warning_timer.reset();
        logout_call_timer.reset();
    }
});
