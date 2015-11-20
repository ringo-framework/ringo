function formatTime(time) {
    time = time / 10;
    var min = parseInt(time / 6000),
        sec = parseInt(time / 100) - (min * 60),
        hundredths = pad(time - (sec * 100) - (min * 6000), 2);
    if (min >= 3) {
        return min + "min";
    } else {
        return (min > 0 ? pad(min, 2) : "00") + ":" + pad(sec, 2);
    }
}

function pad(number, length) {
    var str = '' + number;
    while (str.length < length) {str = '0' + str;}
    return str;
}

$(function(){
    LogoutTimer=function(){
        var auth_timeout = $("meta[name='auth_timeout']").attr("content") * 1000;
        var auth_warning = $("meta[name='auth_warning']").attr("content") * 1000;
        var keep_alive_url = $("meta[name='auth_keepalive']").attr("content");
        var logout_url = $("meta[name='auth_logout']").attr("content");
        var currentTime = auth_timeout;
        var display_warning = false

        $reset = $("#sessiontimer div.input-group-addon")
        $reset.click(function () {
           resetCountdown();
        });
        $("#logoutWarningOK").click(function () {
            resetCountdown();
        });

        function resetCountdown(){
            currentTime = auth_timeout;
            display_warning = false;
            $.get(keep_alive_url);
            $("#logoutWarning").modal("hide");
        }

        function displayTime(){
            if (currentTime > 0) {
                if (currentTime < auth_warning && !display_warning){
                    display_warning = true;
                    $("#logoutWarning").modal("show");
                }
                $countdown = $("#sessiontimer input");
                $countdown.val(formatTime(currentTime));
                currentTime -=1000;
                setTimeout(displayTime, 1000);
            }

            if (currentTime == 0 ) location.href=logout_url+"?autologout=true";
        }

         if (currentTime > 0 && location.pathname) displayTime();

    }();
})
