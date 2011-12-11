

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
