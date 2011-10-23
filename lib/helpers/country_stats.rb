module CountryStatsHelper

  def mk_link(href, content, new=false)
    content = content.split(/<\/?a[^>]*>/).join
    '<a href="%s"%s>%s</a>' % [href, new ? ' target="_blank"' : '', content]
  end

  def wiki_link(place_name, description=nil)
    if not description
      description = place_name
    end
    mk_link('http://en.wikipedia.org/wiki/%s' % place_name, description, true)
  end

  PlaceParseRegex = /!place\{(.*)\}/
  def parse_place(plstr)
    match = plstr.match(PlaceParseRegex)
    match.captures[0].split('|')
  end

  PlaceScanRegex = /(!place\{[^}]+\})/
  def wiki_text(text)
    spl = text.split(PlaceScanRegex)

    out = ''
    spl.each_with_index { |frag, i|
      if i % 2 == 0
        out += frag
      else
        out += wiki_link(*parse_place(frag))
      end
    }
    out
  end

  class Country
    attr_accessor :country, :_country, :sov, :_status,
        :dur, :noteworthy, :comments, :dates, :overnight

    def initialize(raw)
      @country = raw[:country]
      @_country = wiki_link(raw[:country])
      @sov = raw[:sovereign]
      @_status = raw[:status] ? wiki_text(raw[:status]) : nil
      if raw[:date] == 'native'
        @dates = []
      else
        @dates = (raw[:date] ? [raw[:date]] : raw[:dates]).map {|d| parse_visit_date(d)}
      end
      @dur = raw[:duration]
      @overnight = raw[:overnight] == nil ? true : raw[:overnight]
      @noteworthy = (raw[:noteworthies] or []).map {|n| format_place(n)}
      @comments = (raw[:comments] or []).map {|c| wiki_text(c)}

      alt_link = {
        'Kenya' => 'http://www.weebls-stuff.com/songs/kenya/',
        'Poland' => 'http://www.youtube.com/watch?v=mahTGNIk4q4&t=28s',
      }[@country]
      if alt_link
        @_country = mk_link(alt_link, @country, true)
      end
    end

    def format_place(p)
      if p.class == Hash
        args = [p[:name], wiki_text(p[:desc])]
      elsif p.class == String
        args = [p]
      end
      wiki_link(*args)
    end

    def parse_visit_date(d)
      if d.class == Hash
        return [d[:date], d[:type]]
      elsif d.class == String
        return [d, nil]
      end
    end

    def native?
      @dates.empty?
    end

    def complete?
      native? or @dates.last[1] == nil
    end
  end

end
