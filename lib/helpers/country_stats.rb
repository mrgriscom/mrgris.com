module CountryStatsHelper

  def wiki_link(place_name, description=nil)
    if not description
      description = place_name
    end
    '<a href="http://en.wikipedia.org/wiki/%s">%s</a>' % [place_name, description]
  end

  def parse_place(pltext)
    pltext =~ /#place\[(.*)\]/
    content = $1.split('|')
  end

  def wiki_text(text)
    re = /#place\[[^\]]+\]/
    fragments = text.split(re)
    places = text.scan(re)

    out = ''
    for i in 0..[fragments.length, places.length].max-1
      if i < fragments.length
        out += fragments[i]
      end
      if i < places.length
        out += wiki_link(*parse_place(places[i]))
      end
    end
    out
  end

  class Country
    attr_accessor :country, :_country, :sov, :_status,
        :dur, :noteworthy

    def initialize(raw)
      @country = raw[:country]
      @_country = wiki_link(raw[:country])
      @sov = raw[:sovereign]
      @_status = raw[:status] ? wiki_text(raw[:status]) : nil
      @dur = raw[:duration]
      @noteworthy = (raw[:noteworthies] or []).map {|n| parse_place(n)}
    end

    def parse_place(p)
      begin
        args = [p[:name], p[:desc]]
      rescue
        args = [p]
      end
      wiki_link(*args)
    end
  end

end
