function switchResponsive(id) {
    var element = document.getElementById(id);
    if (element.className === id) {
        element.className += " responsive";
    } else {
        element.className = id;
    }
}

function switchBlock() {
    switchResponsive('calendar');
    switchResponsive('box');
}

function displayBlock(obj) {
    var shift = obj.querySelector("#shift").className;
    var calendar = document.getElementById('calendar');
    var box = document.getElementById('box');
    if (calendar.className === 'calendar' && shift != 'F') {
        calendar.className += " responsive";
        box.className += " responsive";
    }
    
    var full_date;

    if (shift != 'F') {
        full_date = obj.className.replace(/_/g, ' ');
        document.getElementById("full_date").innerHTML = full_date;
    }

    var dates = document.getElementsByName('date');
    for (let i = 0; i < dates.length; i++) {
        dates[i].setAttribute('value', full_date);
    }

    var forms = document.getElementsByTagName('form')
    var form;

    if (shift === 'RT' || shift === 'RTT' || shift === 'CT' || shift === 'CTT') {
        form = 'leave_form';
    } else if (shift != 'F') {
        form = 'shift_form';
    }

    if (shift != 'F') {
        // Set type=hidden to all children
        for (let i = 0; i < forms.length; i++) {
            forms[i].style.display = "none";
        }

        // Show wished input
        document.getElementById(form).style.display = "";
    }
    hide();
}

function hide() {
    var form = document.getElementById("id_request_leave").value;
    if (form == "request_leave") {
        document.getElementById("schedule").style.display = "none";
    } else {
        document.getElementById("schedule").style.display = "";
    }
}

function start_now(name) {
    if (document.querySelector('#id_' + name).checked == true) {
        document.getElementById(name).style.display = "";
    } else {
        document.getElementById(name).style.display = "none";
    }
    // To delete ? :
    // start = document.getElementById('id_start').checked
    // end = document.getElementById('id_end').checked
}

function from_between(name) {
    var field1 = document.getElementById('id_' + name + '_hour_1').value;
    var field2 = document.getElementById('id_' + name + '_hour_2').value;
    var text = document.getElementById('info_' + name);
    if (field1 && field2) {
        text.innerHTML = 'Entre :';
    } else {
        switch (name) {
            case 'start':
                text.innerHTML = 'Dès :';
                break;
            case 'end':
                text.innerHTML = "Jusqu'à :";
                break;
        }
    }
}

function validate(copyaddress, subject, date1, date2) {
    var to = "repartition@sbb.ch";
    var cc = copyaddress;
    var subj, msg;
    if (date2) {
        subj = subject + " " + date1 + " - " + date2;
        msg = "Bonjour, j'échange mon tour du " + date1 + " contre le congé de mon collègue. En échange, je lui donne mon congé du " + date2 + ".";
    } else {
        subj = subject + " " + date1;
        msg = "Bonjour, j'échange mon tour du " + date1 + " avec celui de mon collègue.";
    }
    window.location.href = "mailto:" + to + "?cc=" + cc + "&subject=" + subj + "&body=" + msg;
}
