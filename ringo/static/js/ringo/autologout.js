function formatTime(time) {
    time = time / 10;
    var min = parseInt(time / 6000),
        sec = parseInt(time / 100) - (min * 60),
        hundredths = pad(time - (sec * 100) - (min * 6000), 2);
    return (min > 0 ? pad(min, 2) : "00") + ":" + pad(sec, 2);
}

function pad(number, length) {
    var str = '' + number;
    while (str.length < length) {str = '0' + str;}
    return str;
}

var Countdown = new (function() {

    var $countdown;
    var incrementTime = 70;
    // Get session time
    var auth_timeout = $("meta[name='auth_timeout']").attr("content") * 1000;
    var auth_warning = $("meta[name='auth_warning']").attr("content") * 1000;
    var keep_alive_url = $("meta[name='auth_keepalive']").attr("content");
    var logout_url = $("meta[name='auth_logout']").attr("content");
    var currentTime = auth_timeout;

    $(function() {
        // Setup the timer
        $countdown = $("#sessiontimer input");
        $reset = $("#sessiontimer div.input-group-addon")
        $reset.click(function () {
            Countdown.resetCountdown();
        });
        $("#logoutWarningOK").click(function () {
            Countdown.resetCountdown();
        });

        if ($("meta[name='auth_user']").attr("content") != 'None') {
            Countdown.Timer = $.timer(updateTimer, incrementTime, true);
            // Listener to AJAX Requests. On each AJAX Request we will reset
            // the logout timer.
            //$(document).ajaxComplete(function(event,request, settings){
            //    Countdown.resetCountdown();
            //});
            console.log("Initialising the Session timer with " + currentTime + " seconds");
        };
    });

    function updateTimer() {
        // Output timer position
        var timeString = formatTime(currentTime);
        $countdown.val(timeString);

        if (currentTime < auth_warning) {
            console.log('Session is going to expire in ' + auth_timeout/1000 + ' seconds. Show warning.');
            $("#logoutWarning").modal("show");
        }

        // If timer is complete, trigger alert
        if (currentTime == 0) {
            Countdown.Timer.stop();
            console.log('Session expired. Logging out.');
            location.href=logout_url;
        }

        // Increment timer position
        currentTime -= incrementTime;
        if (currentTime < 0) currentTime = 0;
    }

    this.resetCountdown = function() {
        // Stop and reset timer
        Countdown.Timer.stop().once();
        currentTime = auth_timeout;
        Countdown.Timer.play(true);

        $.get(keep_alive_url);
        $("#logoutWarning").modal("hide");
        console.log("Refreshing timer");
    };

});
