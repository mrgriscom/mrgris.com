
function LocationManager($curloc, _update_localtime) {
  this.LOC_URL = '/script/pos.php';

  this.$curloc = $curloc;
  this._update_localtime = _update_localtime;

  this.refresh = function() {
    var locmgr = this;
    $.get(this.LOC_URL, function(resp) {
        if (!resp) {
          return;
        }
        
        locmgr.lat = resp.lat;
        locmgr.lon = resp.lon;
        locmgr.tz_offset = resp.tz_offset;
        locmgr.update();
      }, 'json');
  }

  this.update = function() {
    update_pos(this.$curloc, this.lat, this.lon);
    this.update_localtime();
  }

  this.update_localtime = function() {
    this._update_localtime(this.tz_offset);
  }

  this.start = function(interval) {
    var locmgr = this;
    this.refresh_timer = setInterval(function() {
        locmgr.refresh();
      }, 1000 * interval);
    this.refresh();
  }
}

function register_pos_watcher($curloc, $localtime, clock) {
  var POS_UPDATE_INTERVAL = 60.;
  var TIME_UPDATE_INTERVAL = 1.;

  var locmgr = new LocationManager($curloc, function(tz_offset) {
      update_localtime($localtime, tz_offset, clock);
    });
  locmgr.start(POS_UPDATE_INTERVAL);
  setInterval(function() {
      locmgr.update_localtime();
    }, 1000 * TIME_UPDATE_INTERVAL);
}

function update_pos($e, lat, lon) {
  if (lat != null && lon != null) {
    $e.attr('href', pos_link(lat, lon));
    $e.html(format_pos(lat, lon));
  } else {
    $e.removeAttr('href');
    $e.html('&mdash;');
  }
}

function update_localtime($e, tz_offset, clock) {
  var sloc = format_localtime(clock.clock(), tz_offset);
  $e.html(sloc ? sloc : '&mdash;');
  $e.attr('title', format_tzoffset(tz_offset));
}

function pos_link(lat, lon) {
  var pos = lat + ',' + lon;
  return 'http://maps.google.com/?q=' + pos + '&ll=' + pos + '&z=11&t=h';
}

function format_localtime(secs, offset, include_secs) {
  if (secs == null || offset == null) {
    return null;
  }

  secs += offset * 60.;

  var dow = (Math.floor(secs / 86400.) + 4) % 7;
  var h = Math.floor(secs / 3600.) % 24;
  var m = Math.floor(secs / 60.) % 60;
  var s = Math.floor(secs) % 60;

  var sdow = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'][dow];
  var sh = ((h + 24 - 1) % 12) + 1;
  var sm = n_pad(m, 2);
  var ss = n_pad(s, 2);
  var ap = (h < 12 ? 'a' : 'p');

  return sdow + ' ' + sh + ':' + sm + (include_secs ? ':' + ss : '') + ap;
}

function format_tzoffset(offset) {
  if (offset == null) {
    return null;
  }

  var s = 'UTC';
  if (offset != 0) {
    s += ' ' + (offset > 0 ? '+' : '\u2212');
    offset = Math.abs(offset);
    var h = Math.floor(offset / 60);
    var m = offset % 60;
    s += h;
    if (m != 0) {
      if (m % 15 == 0) {
        s += {1: '\xbc', 2: '\xbd', 3: '\xbe'}[m / 15];
      } else {
        s += ':' + n_pad(m, 2);
      }
    }
  }
  return s;
}

function format_pos(lat, lon) {
  var pattern = '<span class="dir">{{dir}}</span>{{val}}&deg;';
  return format_coord(lat, 'lat', pattern) + '&nbsp;&nbsp;' + format_coord(lon, 'lon', pattern);
}

function format_coord(val, axis, pattern) {
  var sign = (val >= 0);
  var dir = {
    lat: ['N', 'S'],
    lon: ['E', 'W'],
  }[axis][sign ? 0 : 1];
  var s = decimal_pad(Math.abs(val), axis == 'lat' ? 2 : 3, 1);

  pattern = pattern.replace('{{dir}}', dir);
  pattern = pattern.replace('{{val}}', s);
  return pattern;
}

function decimal_pad(num, before, after) {
  var s = num.toFixed(after);
  var target_length = before + (after > 0 ? after + 1 : 0);
  return n_pad(s, target_length);
}

function n_pad(num, len) {
  num = '' + num;
  while (num.length < len) {
    num = '0' + num;
  }
  return num;

}