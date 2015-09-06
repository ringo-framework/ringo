// This global variable will be used to indicate if the logout warning is show in
// other scripts.
var logout_warning = false;
var logout_warning_timer = null;

var LogoutTimer = function (time, url, warning) {
    // The logout timer will call the logout url after the given amount of
    // seconds. A warning dialog for the upcomming logout will be shown a
    // configured time before the actual logout (warning_offset)
    this.warning_offset = warning;
    this.time = time-this.warning_offset;
    this.url = url;
    this.timer1 = null;
    this.timer2 = null;
};

LogoutTimer.prototype.start = function() {
    this.timer1 = setTimeout(showLogoutWarning, this.time*1000);
}

LogoutTimer.prototype.reset = function() {
    clearTimeout(this.timer1);
    clearTimeout(this.timer2);
    this.start();
};

function showLogoutWarning() {
    $("#logoutWarning").modal("show");
    logout_warning = true;
    // Automatically logout the user 30 seconds after the warning is shown.
    logout_warning_timer.timer2 = setTimeout(
            function() {
                callLogoutPage(logout_warning_timer.url)
            },
            logout_warning_timer.warning_offset*1000);
}

function callLogoutPage(url) {
    logout_warning = false;
    logout_warning_timer = null;
    location.href=url;
}

function logoutCountdown(time, url, warning) {
    logout_warning = false;
    logout_warning_timer = new LogoutTimer(time, url, warning);
    logout_warning_timer.start();
}

function hideLogoutWarning(event) {
  // Call the index page to reset the serverside logout counter. This will
  // also reset the client side counter as it is a AJAX request which gets
  // listened to.
  event.preventDefault();
  var keep_alive_url = this.attributes["href"].value;
  $.get(keep_alive_url);
  $("#logoutWarning").modal("hide");
  logout_warning = false;
  return false;
}

// Listener to AJAX Requests. On each AJAX Request we will reset the logout
// timer.
$(document).ajaxComplete(function(event,request, settings){
    if (logout_warning_timer != null) {
        logout_warning_timer.reset();
    }
});
