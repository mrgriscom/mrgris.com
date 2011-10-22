require 'yaml'

module MP3Info

  def mp3loadinfo(path)
    YAML::load(IO::popen('python lib/helpers/mp3info.py "%s"' % path))
  end

  def mp3info(item)
    data = mp3loadinfo(item[:path])
    data.each { |track|
      if not track['system']
        track['system'] = system_name(track['game'], item[:systems])
      end
    }
    data
  end

  def system_name(game, meta)
    match = meta[:override].find {|ov| game.downcase.include? (ov[:tag].downcase) }
    match ? match[:system] : meta[:default]
  end

  def fmt_length(s)
    s = s.round
    '%d:%02d' % [s / 60, s % 60]
  end

end
