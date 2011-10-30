
module Footnote

  def symbol(i)
    ['*', '&dagger;', '&#x2021;', '&sect;'][i - 1]
  end

  def footinline(i)
    '<span class="foot"><a href="#foot%d">%s</a></span>' % [i, symbol(i)]
  end

end
