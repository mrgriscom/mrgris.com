function life_expectancy(years, gender) {
  actuarial_tables = {
    m: { //US, male, white
      0: 75.9,
      1: 75.4,
      5: 71.5,
      10: 66.5,
      15: 61.6,
      20: 56.8,
      25: 52.2,
      30: 47.5,
      35: 42.8,
      40: 38.1,
      45: 33.6,
      50: 29.2,
      55: 25.0,
      60: 21.0,
      65: 17.3,
      70: 13.7,
      75: 10.6,
      80: 7.9,
      85: 5.7,
      90: 4.1,
      95: 2.9,
      100: 2.0
    },
    f: { //US, female, white
      0: 80.8,
      1: 80.2,
      5: 76.3,
      10: 71.3,
      15: 66.3,
      20: 61.4,
      25: 56.6,
      30: 51.7,
      35: 46.9,
      40: 42.1,
      45: 37.4,
      50: 32.8,
      55: 28.3,
      60: 24,
      65: 19.9,
      70: 16,
      75: 12.4,
      80: 9.3,
      85: 6.8,
      90: 4.8,
      95: 3.3,
      100: 2.2
    }
  }

  var life_exp = actuarial_tables[gender];
  var brackets = [];
  $.each(life_exp, function(age, exp) {
    brackets.push(+age);
  });
  brackets.sort(function(a, b) { return a - b; });
  for (var i = 0; i < brackets.length; i++) {
    if (years < brackets[i]) {
      break;
    }
  }
  i -= 1;
  var a0 = brackets[i];
  if (i + 1 < brackets.length) {
    var a1 = brackets[i + 1];
    var left = (life_exp[a0] * (a1 - years) + life_exp[a1] * (years - a0)) / (a1 - a0);
    var exp = years + left;
  } else {
    var exp = a0 + life_exp[a0];
  }
  return exp;
}

function commaize (numstr) {
  var pointat = numstr.indexOf(".");
  if (pointat == -1)
    pointat = numstr.length;
  
  var outstr = "";
  for (i = (pointat == 0 ? 0 : ((pointat - 1) % 3) - 2); i < pointat - 3; i += 3) {
    outstr = outstr + numstr.substring(Math.max(i, 0), i + 3) + ",";
  }
  outstr = outstr + numstr.substring(pointat - 3);

  return outstr;
}

function format(num, prec, format) {
  format = format || '{{#}}';
  var snum = commaize(num.toFixed(prec));
  return format.replace(/{{#}}/, snum);
}

function run(EPOCH, gender, $e) {
  var secs = (new Date().getTime() / 1000.) - EPOCH;
  var days = secs / 86400.;
  var years = days / 365.2425;
  var life_exp = years / life_expectancy(years, gender);

  $('#' + $e[0]).text(format(secs, 2));
  $('#' + $e[1]).text(format(days, 4));
  $('#' + $e[2]).text(format(years, 5));
  $('#' + $e[3]).text(format(100. * life_exp, 3, '{{#}}%'));
}

