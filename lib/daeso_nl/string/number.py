# -*- coding: utf-8 -*-

# Copyright (C) 2007 by 
# Erwin Marsi and Tilburg University


# This file is part of the DAESO library.

# The DAESO library is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# The DAESO library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Erwin Marsi <e.marsi@gmail.com>"
__credits__ = ""
__copyright__ = "Copyright (C) 2007 by Erwin Marsi and Tilburg University"
__license__ = "GNU General Public License"
__url__ = "http://daeso.uvt.nl"
__date__ = "$Date: 2009-04-19 06:36:18 +0200 (Sun, 19 Apr 2009) $"

__version__ = ""


"""
Spell out numbers
"""

__all__ = [
    "spell_out_number"]



def spell_out_number(n, prefer_hundreds=True):
    """
    spell out a positive integer number in words
    """
    s = str(n)
    
    if len(s) == 4 and s[1] != "0" and prefer_hundreds:    
        # spell out a positive integer number in words using hundreds, where n
        # must have four digits and the second digit cannot be zero:
        # 2001 ==> *twintighonderdeen
        return ( _digit_triple_to_words("0" + s[:2]) +
                 "honderd" +
                 _digit_triple_to_words("0" + s[2:]) )
    
    words = ""
    i = 0
    
    while s:
        triple = s[-3:].rjust(3, "0")
        
        if i == 0 and triple == "000":
            words = "nul"
        elif i == 1 and triple == "001":
            # 1000 ==> *eenduizend
            words = ( _triple_modifiers[i] + 
                      words )
        else:
            # TWEEduizend, ..., negenhondernegenennegentigDUIZEND,
            # EEN miljoen, ...
            words = ( _digit_triple_to_words(triple) + 
                      _triple_modifiers[i] +
                      words )
            
        s = s[:-3]
        i += 1
        
    # strip spaces from words starting/ending with a triple modifier
    return words.strip()





# mapping of triples of digits to words
# for all basic numbers and irregular cases

_triple_to_word = {
    "000": "", # zeros alway remain unexpressed, except in "nul"
    "001": "een",
    "002": "twee",
    "003": "drie",
    "004": "vier",
    "005": "vijf",
    "006": "zes",
    "007": "zeven",
    "008": "acht",
    "009": "negen",
    "010": "tien",
    "011": "elf",
    "012": "twaalf",
    "013": "dertien",
    "014": "veertien",
    "015": "vijftien",
    "016": "zestien",
    "017": "zeventien",
    "018": "achttien",
    "019": "negentien",
    "020": "twintig",
    "030": "dertig",
    "040": "veertig",
    "050": "vijftig",
    "060": "zestig",
    "070": "zeventig",
    "080": "tachtig",
    "090": "negentig"
    }


# modifiers that can be combined with an expanded triple

_triple_modifiers = (
    "",
    "duizend ", # no space preceding duizend
    " miljoen ",
    " miljard ",
    " biljoen ",
    " biljard ",
    " triljoen ",
    " triljard "
    )


def _digit_triple_to_words(digits):
    """
    express a string of three digits in words
    """
    try:
        return _triple_to_word[digits]
    except KeyError:
        pass
    
    d1, d2, d3 = digits
    words = ""
    
    if d1 not in "01":
        # TWEEhonderd, DRIEhonderd, ..., NEGENhonderd
        words += _triple_to_word["00" + d1]
        
    if d1 != "0":
        # HONDERD, tweeHONDERD, ..., negenHONDERD
        words += "honderd"
        return words + _digit_triple_to_words("0" + d2 + d3)
    
    if d3 != "0":
        # EENENtwintig, TWEEENtwintig, ..., NEGENENnegentig
        words += _triple_to_word["00" + d3] + "en"
    
    if d2 != "0": 
        # TWINTIG, eenenTWINTIG, tweeenTWINTIG, ..., negenenNEGENTIG
        words += _triple_to_word["0" + d2 + "0"]
        
    return words


    
             
print spell_out_number(4401)
print spell_out_number(6028)
print spell_out_number(271850)

    
    
    
    
    
    