$('document').ready(function () {
    if (verify === 'True') {
        $('#otp-input').modal('show');

        let email = $('#emailid').val();
        var h_email = email.replace(/(\w{3})[\w.-]+@([\w.]+\w)/, "$1***@$2");
        document.getElementById("hide_email").innerHTML = h_email;

        let sec = 0;
        let minute = 0;
        let timer = document.getElementById("timer");

        if (countdown === 'True') {
            minute = 2;
            sec = 00;

        } else {
            if (window.sessionStorage.getItem("minute") && window.sessionStorage.getItem("sec")) {
                minute = parseInt(window.sessionStorage.getItem("minute"));
                sec = parseInt(window.sessionStorage.getItem("sec"));
            } else {
                timer.innerHTML = "OTP ALREADY EXPIRED";
            }
        }
        setInterval(function () {
            timer.innerHTML = minute + ":" + sec;
            if (minute <= 0 && sec <= 0) {
                window.sessionStorage.removeItem("minute");
                window.sessionStorage.removeItem("sec");
                timer.innerHTML = "OTP ALREADY EXPIRED";
            }
            else if (sec <= 0) {
                minute--;
                sec = 60;
            }
            sec--;
            window.sessionStorage.setItem("minute", minute);
            window.sessionStorage.setItem("sec", sec);
        }, 1000)

        $('#resend').click(function () {
            var msg_show = document.getElementById("msgs");
            msg_show.innerHTML = 'Sending New OTP...'
            $.ajax({
                type: 'POST',
                url: '', // Get URL from Django
                data: {'req': 'resend_otp', 'csrfmiddlewaretoken': csrf_token,}, // Data to send to view
                success: function (response) {
                    var sts = JSON.parse(response)['status'];
                    var msg = JSON.parse(response)['msg'];
                    if (sts === 'success') {
                        minute = 2;
                        sec = 00;
                        timer.innerHTML = minute + ":" + sec;
                        window.sessionStorage.setItem("minute", minute);
                        window.sessionStorage.setItem("sec", sec);
                    }
                    msg_show.innerHTML = msg;
                }
            });
        });
    } else {
        $('#otp-input').modal('hide');
    }
});

document.addEventListener("DOMContentLoaded", function (event) {
    function OTPInput() {
        const inputs = document.querySelectorAll('#otp > *[id]');
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].addEventListener('keydown', function (event) {
                if (event.key === "Backspace") {
                    inputs[i].value = '';
                    if (i !== 0) inputs[i - 1].focus();
                } else {
                    if (i === inputs.length - 1 && inputs[i].value !== '') {
                        return true;
                    } else if (event.keyCode > 47 && event.keyCode < 58) {
                        inputs[i].value = event.key;
                        if (i !== inputs.length - 1) inputs[i + 1].focus();
                        event.preventDefault();
                    } else if (event.keyCode > 64 && event.keyCode < 91) {
                        inputs[i].value = String.fromCharCode(event.keyCode);
                        if (i !== inputs.length - 1) inputs[i + 1].focus();
                        event.preventDefault();
                    }
                }
            });
        }
    }

    OTPInput();
});

function join_otp() {
    var otp = '';
    var f_otp = document.getElementById("otp_val");
    const inputs = document.querySelectorAll('#otp > *[id]');
    for (let i = 0; i < inputs.length; i++) {
        otp += inputs[i].value;
    }
    f_otp.value = otp;
}