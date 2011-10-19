module CountryStatsHelper

  def wiki_link(place_name)
    '<a href="http://en.wikipedia.org/wiki/%s">%s</a>' % [place_name, place_name]
  end

end
