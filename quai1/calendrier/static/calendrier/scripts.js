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
      forms[i].style.visibility = "hidden"

    }

    //Show wished input
    document.getElementById(form).style.visibility = "visible"

  }

}
