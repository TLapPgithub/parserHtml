# -*- coding: utf-8 -*-
"""
#.##..###.#....#...####.#.
Created on Wed Jun 20 22:08:18 2018
@author: TLapP
Description: Script that provides a class that can analyze the html code and process it.
"""
from html.parser import HTMLParser
import re
from re import finditer


class MyHTMLParser(HTMLParser):
    """
    Parser html that detect if there are script tags.
    """
    pre_tag_start_record_ref = "pre"
    tag_start_record_ref = "code"
    tag_count_ref = "script"
    tag_allow = ["h4", "h5", "h6", "p", "script", "a", "b", "i", "br", "strong", "pre", "code", "ul", "li", "ol"] #"h1", "h2", "h3", 
    tag_with_attributs_allow = {"a":["href"], "code":["class"]}

    def __init__(self):
        super(MyHTMLParser, self).__init__()
        self.balise_enter_a_balise = [] #All the balise between the balise set in tag_start_record_ref
        self.pre_start_record = False ## State of the prerecording. Start when the pre_tag_start_record_ref is encontred and close when it is encontred as end_tag
        self.start_record = False # State of the recording. Start when the tag_start_record_ref is encontred and close when it is encontred as end_tag
        self.tag_count = 0 # Count the time that tag_count_ref is incontred between the start and the end of tag_start_record_ref

        self.tag_opened = [] # All the tag are saved here, and there are deleted when the close tag corresponding is encontred
        self.has_error = [] # All the errors are saved here
        self.pos_code_html = [] # All the tag code with language html
        self.pos_code_html_ref = [] # Ref of all the tag code with language html
        self.pos_endcode_html = [] # All the end tag code with language html
        self.pos_endcode_html_ref = [] # Ref all the end tag code with language html

        self.html_code = ""
        self.fin_start_code_html = [] #por memoriser ou les balise code dont language est html commence

    def feed(self, data):        
        """
        Feed data to the parser.
        Call this as often as you want, with as little or as much text
        as you want (may include '\n').
        """
        self.rawdata = self.rawdata + data
        self.text_enter = self.rawdata
        self.goahead(0)
    
    def handle_starttag(self, tag, attrs):
        """
        Detect the html tag opening and treat it.
        """
        print("Encountered a start tag:", tag)
        if self.start_record == True:
            self.balise_enter_a_balise.append(tag)

            for attr in attrs:
                print("     attr:", attr)
                try:
                    len(re.findall(self.tag_count_ref, attr[1]))
                except:
                    self.has_error.append("This tag ({}) has a problem".format(tag))
        else:
            if tag not in self.tag_allow:
                self.has_error.append("This tag ({}) is not allow".format(tag))

            if tag == self.tag_count_ref:
                self.has_error.append("There is a tag script not between {} and {}".format(self.pre_tag_start_record_ref, self.tag_start_record_ref))
            
            if attrs and tag in self.tag_with_attributs_allow:
                for attr in attrs:
                    print("     attr:", attr)
                    for attribut_allow in self.tag_with_attributs_allow[tag]:
                        if attr[0] == attribut_allow:
                            try:
                                if len(re.findall(self.tag_count_ref, attr[1])) != 0:
                                    self.has_error.append("There is script injection in this tag ({})".format(tag))
                                if len(attr[1])==0:
                                    self.has_error.append("Please don't use this attribut ({}) in this tag ({}) if you don't use it)".format(attr[0], tag))
                                elif tag == "code" and attr[0] == "class":
                                    attribut_class = attr[1].replace(" ", "")
                                    attribut_class = attribut_class.replace(";", "")
                                    attribut_class = attribut_class.replace(",", "")
                                    if attribut_class[:9] != "language-":
                                        self.has_error.append("The atttribut ({}) for the tag ({}) allow only 'language-XXXXXXX'".format(attr[0], tag))
                                    if len(re.findall(">", attr[1])) != 0:
                                        self.has_error.append("Please do not use > in the atttribut ({}) for the tag ({})".format(attr[0], tag))
                                    elif len(re.findall("<", attr[1])) != 0:
                                        self.has_error.append("Please do not use < in the atttribut ({}) for the tag ({})".format(attr[0], tag))
                                    if attribut_class == "language-html":
                                        self.pos_code_html.append(self.getpos())
                                        self.pos_code_html_ref.append(self.getpos())
                                        
                            except:
                                self.has_error.append("This tag ({}) has a problem".format(tag))
                        else:
                            self.has_error.append("The attribut ({}) is not allow for the tag ({})".format(attr[0], tag))
            elif attrs:
                self.has_error.append("The tag ({}) is not allow to have attributs".format(tag))
                    
        self.tag_opened.append(tag)

        if tag == self.pre_tag_start_record_ref:
            self.pre_start_record = True

        if self.pre_start_record and tag == self.tag_start_record_ref:
            self.start_record = True
        elif tag == self.tag_start_record_ref:
            self.has_error.append("This tag ({}) is not between the tag ({})".format(tag, self.pre_tag_start_record_ref))

    def handle_endtag(self, tag):
        """
        Detect the html tag closing and treat it.
        """
        if str(self.tag_opened[-1:]).strip('[]').strip("''") != tag:
            self.has_error.append("This tag ({}) has a not been opened".format(tag))
        del self.tag_opened[-1:]
        
        if tag == self.tag_start_record_ref:
            self.start_record = False

            if self.pos_code_html_ref:
                self.pos_endcode_html_ref.append(self.getpos())
                del self.pos_code_html_ref[-1:]

        if tag == self.pre_tag_start_record_ref:
            if self.start_record != False:
                self.has_error.append("You must close the tag ({}) before close the tag ({})".format(self.tag_start_record_ref, self.pre_tag_start_record_ref))
            else:
                self.pre_start_record = False
            
        if self.start_record == True:
            self.balise_enter_a_balise.append(tag)
        print("Encountered an end tag :", tag)

    def change_codeHtmlbetween_code(self):
        """
        Allows you to modify the transmitted code so that it can be correctly interpreted by the prism plugin that highlights the syntax, or just not to be interpreted by the web browser.
        This function does not remove script tags.
        """
        html_code_bon = self.html_code

        if self.pos_code_html:
            for start_code_html in self.pos_code_html:
                this_cod_html_closed = False
                for match in finditer(">", self.html_code):
                    if int(start_code_html[1]) - int(match.span()[0]) <=0 and not this_cod_html_closed:
                        self.fin_start_code_html.append([int(match.span()[0]), "start"])
                        this_cod_html_closed = True

            for start_code_html in self.pos_endcode_html_ref:
                self.fin_start_code_html.append([start_code_html[1], "end"])

            strChange = list(html_code_bon)

            self.fin_start_code_html = sorted(self.fin_start_code_html, reverse=False)

            all_the_sentence = []

            all_the_sentence += strChange[0:self.fin_start_code_html[0][0]+1]
            end_the_sentence = strChange[self.fin_start_code_html[-1:][0][0]:]
            print(self.fin_start_code_html)

            while len(self.fin_start_code_html)>1:
                someHtmlCode = strChange[self.fin_start_code_html[0][0]+1:self.fin_start_code_html[1][0]]
                if len(self.fin_start_code_html)>=3:
                    sentence_between = strChange[self.fin_start_code_html[1][0]:self.fin_start_code_html[2][0]+1]
                else:
                    sentence_between = ""
                del(self.fin_start_code_html[0])
                del(self.fin_start_code_html[0])

                indexOfPos = 0
                for character in someHtmlCode:
                    if character == "<":
                        someHtmlCode[indexOfPos] = "&lt;"
                    elif character == ">":
                        someHtmlCode[indexOfPos] = "&gt;"
                    indexOfPos +=1

                all_the_sentence += someHtmlCode
                all_the_sentence += sentence_between

            all_the_sentence +=end_the_sentence 
            
            return "".join(all_the_sentence)
        else:
            return html_code_bon

    def check_error(self, html_code):
        """
        Function that analyzes the html code.
        Detects script tags that are misplaced.
        Also detects if some tags are not closed or just html code errors.
        """
        self.html_code = html_code
        #html_code = html_code.replace("&", "&amp;")
        html_code = html_code.replace("&lt;", "<")
        html_code = html_code.replace("&gt;", ">")

        if len(re.findall("<  ", html_code)) != 0:
               self.has_error.append("Your '<' must touche the tag html")
               
        html_code = html_code.replace("< ", "<")
        self.feed(html_code)
        
        if self.tag_opened:
            self.has_error.append("All tags had not been closed")

        if self.pos_code_html_ref:
            self.has_error.append("All tags code with attributs html had not been closed")

        if self.has_error:
            return self.has_error
        else:
            return False
