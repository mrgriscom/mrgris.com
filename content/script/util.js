

function scroll_pin(pin_threshold, $container, $elem) {
  var base_offset = $container.offset().top;
  var pos_type = $elem.css('position');

  return function() {
    var scroll_pos = $(window).scrollTop();
    var elem_pos = base_offset - scroll_pos;
    var pinned = (elem_pos < pin_threshold);
    $elem.css('position', pinned ? 'fixed' : pos_type);
    $elem.css('top', pinned ? pin_threshold + 'px' : 0);
  };
}
  
function set_pin(pin_threshold, $container, $elem) {
  var pinfunc = scroll_pin(pin_threshold, $container, $elem);
  $(window).scroll(pinfunc);
  pinfunc();
}

function preload_images(paths, basepath) {
  $(paths).each(function(i, val) {
    $('<img />').attr('src', (basepath || '') + val).prependTo('body').hide();
  });
}




// local system clock in seconds
function _clock() {
  return (new Date().getTime() / 1000.);
}

function ServerClock() {
  this.CLOCK_URL = '/script/clock.php';

  this.offset = null; // server - local
  this.error = null;

  this.synchronize = function() {
    var request_start = _clock();
    var server_clock = this;
    $.post(this.CLOCK_URL, function(resp) {
        if (!resp) {
          return;
        }

        var request_end = _clock();
        var server_time = resp;

        var est_local_time = (request_end + request_start) / 2.;
        server_clock.error = (request_end - request_start) / 2.;
        server_clock.offset = server_time - est_local_time;
      }, 'json');
  }

  this.clock = function() {
    return (this.offset != null ? _clock() + this.offset : null);
  }

  //clocks should be self-managing
  this.synchronize();
}

function LocalClock() {
  this.clock = _clock;
}
