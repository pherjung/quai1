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
  var next = $('table').last();
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

function printForms(element, obj) {
  var shift = obj.querySelector("#shift");
  var class_div = shift.closest('div').className;
  var table = shift.closest('table');
  var index = shift.closest('tr').rowIndex+1;
  var row = table.insertRow(index);
  row.setAttribute('class', 'info');
  var col = document.createElement('td');
  col.setAttribute('colspan', '7');
  row.appendChild(col);
  element.className += " responsive";
  var box = document.getElementById('box');
  col.appendChild(box);
  // Get the full date
  if (shift.className != 'F') {
    full_date = obj.className.replace(/_/g, ' ');
    document.getElementById("full_date").innerHTML = full_date;
  }

  var dates = document.getElementsByName('date');
  for (let u = 0; u < dates.length; u++) {
    dates[u].setAttribute('value', full_date);
  }

  // Choose right form
  forms = document.getElementsByTagName('form');
  const leaves = ['RT', 'CT', 'CTT', 'RTT', 'CTS'];
  if (leaves.includes(shift.className)) {
    var form = 'leave_form';
  } else if (shift.className != 'F') {
    var form = 'shift_form';
  }

  if (shift.className != 'F') {
    //Set type=hidden to all children
    for (let i = 0; i < forms.length; i++) {
      forms[i].style.display = "none";
    }
    //Show wished input
    document.getElementById(form).style.display = ""
  }

  hide()
}

function switchResponsive(id, obj) {
  var element = document.getElementById(id);
  if (element.className === id) {
    printForms(element, obj)
  } else {
    element.className = id;
    var box_index = element.closest('tr').rowIndex;
    var parent = document.getElementById('parent');
    parent.append(element);
    $('.info').remove();
    if (obj.localName === 'td') {
      printForms(element, obj);
    }
  }

}

function exchanges(date, url) {
  const csrftoken = getCookie('csrftoken');
  var index = $('#box').parents('tr');
  $.ajax({
    type: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    mode: 'same-origin',
    data: JSON.stringify(date),
    url: url,
    success: function(data){
      index.after("<tr id='info' class='info'></tr>");
      $('#info').last().replaceWith(data);
    }
  })
  return false;

}

function displayBlock(obj, id) {
  var shift = obj.querySelector("#shift");
  var class_div = shift.closest('div').className;
  var shift_name = shift.className;
  const quit = ['None', 'wish_accepted']
  if (shift_name === 'F' || quit.includes(class_div)) return;
  switchResponsive('box', obj);
  gifted = shift.closest('td').querySelector('i');
  if (gifted?.className === 'fa-solid fa-gift') {
    exchanges(full_date, '/calendar/gifts/');
  }
  var swap = shift.closest('td').querySelector('#exchange');
  if (class_div === 'wish') {
    exchanges(full_date, '/calendar/wishes/');
  }
  if (swap.className === 'swap') {
    exchanges(full_date, '/calendar/exchanges');
  }

  var validate = shift.closest('td').querySelector('.date > i');
  if (validate.className === 'fa-solid fa-envelope') {
    exchanges(full_date, '/calendar/to_accept_leave');
    exchanges(full_date, '/calendar/to_accept_shift');
  }
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
