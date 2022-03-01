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
  var x = document.getElementById('calendar')
  var y = document.getElementById('box')
  if (x.className === 'calendar') {
    x.className += " responsive"
    y.className += " responsive"


  }

  full_date = obj.className.replace(/_/g, ' ')
  document.getElementById("full_date").innerHTML = full_date


}
