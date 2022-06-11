function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function next_month(){
  const csrftoken = getCookie('csrftoken');
  var next = $('.table-calendar').last();
  console.log(next.attr('id'));
  $.ajax({
    type: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    mode: 'same-origin',
    url: "/calendar/calendar?month="+next.attr('id'),
    success: function(data){
      $('div.parent').last().append("<div class='calendar' id='calendar'></div>")
      $('.calendar').last().html(data);
    }
  });
  return false;
}

function myFunction(id) {
  var x = document.getElementById(id);
  if (x.className === id) {
    x.className += " responsive";

  } else {
    x.className = id;

  }

}

function switchBlock() {
  myFunction('calendar')
  myFunction('box')

}

function displayBlock(obj, id) {
  var shift = obj.querySelector("#shift").className
  var x = document.getElementById('calendar')
  var y = document.getElementById('box')
  if (x.className === 'calendar' && shift != 'F') {
    x.className += " responsive"
    y.className += " responsive"

  }

  if (shift != 'F') {
    full_date = obj.className.replace(/_/g, ' ')
    document.getElementById("full_date").innerHTML = full_date

  }

  dates = document.getElementsByName('date')
  for (let u = 0; u < dates.length; u++) {
    dates[u].setAttribute('value', full_date)

  }

  forms = document.getElementsByTagName('form')

  if (shift === 'RT' || shift === 'RTT' || shift === 'CT' || shift === 'CTT') {
    var form = 'leave_form'

  } else if (shift != 'F') {
    var form = 'shift_form'

  }

  if (shift != 'F') {
    //Set type=hidden to all children
    for (let i = 0; i < forms.length; i++) {
      forms[i].style.display = "none"

    }

    //Show wished input
    document.getElementById(form).style.display = ""

  }
  hide()


}

function hide() {
  form = document.getElementById("id_request_leave").value
  if (form == "request_leave") {
    document.getElementById("schedule").style.display = "none";

  } else {
    document.getElementById("schedule").style.display = "";

  }

}

function start_now(name) {
  if (document.querySelector('#id_'+name).checked == true) {
    document.getElementById(name).style.display = "";

  } else {
    document.getElementById(name).style.display = "none";

  }

  start = document.getElementById('id_start').checked
  end = document.getElementById('id_end').checked

}

function from_between(name) {
  field1 = document.getElementById('id_' + name + '_hour_1').value
  field2 = document.getElementById('id_' + name + '_hour_2').value
  text = document.getElementById('info_' + name)
  if (field1 && field2) {
    text.innerHTML = 'Entre :'
  } else {
      switch(name) {
        case 'start':
          text.innerHTML = 'Dès :'
          break;
        case 'end':
          text.innerHTML = "Jusqu'à :"
          break;
      }
  }

}

function validate(copyaddress, subject, date1, date2) {
  to = "repartition@sbb.ch"
  cc = copyaddress
  if (date2) {
    subj = subject + " " + date1 + " - " + date2
    msg = "Bonjour, j'échange mon tour du " + date1 + " contre le congé de mon collègue. En échange, je lui donne mon congé du " + date2 + "."

  } else {
    subj = subject + " " + date1
    msg = "Bonjour, j'échange mon tour du " + date1 + " avec celui de mon collègue."

  }

  window.location.href = "mailto:" + to + "?cc=" + cc + "&subject=" + subj + "&body=" + msg;

}
