module Nanoc::Filters
  class MathTex < Nanoc::Filter
    identifiers :mathtex
    
    def run(content, params={})
      # latex equations now handled with mathjax js
      
      # process numerical quantities
      content = content.gsub(/##(.+?)##/) { |m|
        quant = m[2..-3]
        data = quant.match(/(?<num>[-+]?\d*\.?\d*)([Ee](?<exp>[-+]?\d+))?(?<suffix>.*)/)
        num = data['num']
        exp = data['exp']
        suffix = data['suffix']

        num = num.gsub(/-/) { |m| '&minus;' }
        num = num.sub(/^[^\d.]*\d+/) { |m| m.sub(/\d+/) { |m| 
          m.reverse.gsub(/(\d{3})(?=\d)/, '\\1,').reverse  # add commas
        }}
        s = num

        if exp
          exp = exp.gsub(/-/) { |m| '&minus;' }
          s += '&times;10<sup>' + exp + '</sup>'
        end

        suffix = suffix.gsub('*', '&middot;')
        suffix = suffix.gsub(/\^\w+/) { |m| '<sup>' + m[1..-1] + '</sup>' }
        s += suffix

        "<span class='quantity'>" + s + "</span>"
      }
      content
    end
  end
end

