require 'yaml'

module MP3Info

  def mp3info(path)
    YAML::load(IO::popen('python lib/helpers/mp3info.py "%s"' % path))
  end

end
