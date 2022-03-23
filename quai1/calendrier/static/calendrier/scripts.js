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
  form = document.getElementById("id_ask_rest").value
  if (form == "ask_rest") {
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
    text.innerHTML = 'Dès :'

  }

}
