

include CountryStatsHelper
include MP3Info
include Footnote
include GPGInfo

def geolink(lat, lon, span, name=nil)
  name ||= 'loc:%s,%s' % [lat, lon]
  'http://maps.google.com/?q=%{name}&ll=%{lat},%{lon}&spn=%{span},%{span}&t=h' % {:name => name, :lat => lat, :lon => lon, :span => span}
end
