# -*- coding: utf-8 -*-
"""
#.##..###.#....#...####.#.
Created on Wed Jun 20 22:08:18 2018
@author: TLapP
Description: Script that lets you test the MyHTMLParser class.
"""

from parserToUse import MyHTMLParser

# Exemple d'utilisation
# =====================

parser = MyHTMLParser()
html_code = """<a href="htlj"></a><pre><code class="language-html"><script>e</script> </code><code class="language-html"><script>e</script></code></pre>"""

#print(parser.balise_enter_a_balise)
#print("Not Safe ?", parser.check_error(s))

errors = parser.check_error(html_code)

if errors:
    print("\nError")
    print("="*5)
    for error in errors:
        print(error)
else:
    print("No error")

print(parser.change_codeHtmlbetween_code())