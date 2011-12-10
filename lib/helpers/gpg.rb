

module GPGInfo

  def exportkey(id)
    IO::popen('gpg --export --armor %s' % id).read
  end

end

