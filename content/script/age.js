

// return life expectancy (expected age of death) for person of given gender and # years old
function life_expectancy(years, gender) {
  actuarial_tables = { // 2008 data; source: http://www.census.gov/compendia/statab/2012/tables/12s0104.pdf
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
    var remain = (life_exp[a0] * (a1 - years) + life_exp[a1] * (years - a0)) / (a1 - a0);
    return years + remain;
  } else {
    return Math.max(a0 + life_exp[a0], years);
  }
}

// format a number (as string) with commas
function commaize (numstr) {
  var GROUP = 3;

  var pointat = numstr.indexOf(".");
  if (pointat == -1) {
    pointat = numstr.length;
  }  
  if (pointat == 0) {
    pointat = GROUP; //avoid negative mod ugliness
  }

  var outstr = "";
  for (var i = ((pointat - 1) % GROUP) - (GROUP - 1); i < pointat - GROUP; i += GROUP) {
    outstr += numstr.substring(Math.max(i, 0), i + GROUP) + ",";
  }
  outstr += numstr.substring(pointat - GROUP);
  return outstr;
}

// round a number to 'prec' digits, using rounding mode 'up', 'down', or 'normal' (default)
function round(num, prec, mode) {
  mode = mode || 'normal';
  var func = {
    normal: Math.round,
    up: Math.ceil,
    down: Math.floor
  }[mode];
  var k = Math.pow(0.1, prec);
  return func(num / k) * k;
}

function format(num, prec, roundmode, format) {
  format = format || '{{#}}';
  var snum = commaize(round(num, prec, roundmode).toFixed(prec));
  return format.replace(/{{#}}/, snum);
}

function age_update(EPOCH, gender, elems, clock) {
  clock = clock || new LocalClock();
  var timestamp = clock.clock();
  if (timestamp == null) {
    return;
  }
  
  var secs = timestamp - EPOCH;
  var days = secs / 86400.;
  var years = days / 365.2425;
  var life_exp = years / life_expectancy(years, gender);

  var PREC = [2, 4, 5, 3];
  //var PREC = [2, 7, 9, 9]; //creepy ed.
  var ROUND = 'down';
  $('#' + elems[0]).text(format(secs, PREC[0], ROUND));
  $('#' + elems[1]).text(format(days, PREC[1], ROUND));
  $('#' + elems[2]).text(format(years, PREC[2], ROUND));
  $('#' + elems[3]).text(format(100. * life_exp, PREC[3], ROUND, '{{#}}%'));
}

function register_age_ticker(epoch, gender, elements, clock, tick) {
  tick = tick || 0.01;

  return setInterval(function() {
      age_update(epoch, gender, elements, clock);
    }, 1000 * tick);
}
