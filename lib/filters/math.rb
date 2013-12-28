module Nanoc3::Filters
  class MathTex < Nanoc3::Filter
    identifiers :mathtex
    
    def run(content, params={})
      image_dir = "output/img/math/"
      ext = "png"
      if (!File.exists?(image_dir))
        system("mkdir -p " + image_dir)
      end
      content = content.gsub(/\$\$(.+?)\$\$/) { |m|
        command = "texvc /tmp " + image_dir + " '" + m[2..-3] + "' utf8"
        digest = `#{command}`.split(/\n/)[0][1..-1]
        "<span class='equation'><img src='/img/math/" + digest + "." + ext + "' /></span>"
      }
      content = content.gsub(/##(.+?)##/) { |m|
        quant = m[2..-3]

        "<span class='quantity'>" + quant + "</span>"
      }
      content
    end
  end
end

