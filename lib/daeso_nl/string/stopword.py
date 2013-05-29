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

"""
Dutch stopword removal

The notion of stopword is fuzzy and largely domain-dependent.
This list of stopwords is based the combined frequency counts on a
number of large text corpora as provided by the TSTS Centrale,
plus linguistic considerations regarding closed-class words.
Your mileage may vary.
"""

__author__ = "Erwin Marsi <e.marsi@gmail.com>"
__credits__ = ""
__copyright__ = "Copyright (C) 2007 by Erwin Marsi and Tilburg University"
__license__ = "GNU General Public License"
__url__ = "http://daeso.uvt.nl"
__date__ = "$Date: 2009-12-10 11:49:18 +0100 (Thu, 10 Dec 2009) $"

__version__ = ""


from string import punctuation


# note that each string must start with a space,
# otherwise the combined string split will not work properly

determiners = " de het een"

aux_verbs = ( " ben bent is zijn was waren"
              " word wordt worden werd waren"
              " heb hebt heeft hebben had hadden"
              " zal zult zullen zou zouden"
              " kan kunt kunnen kon konden"
              )

preps = ( " in op met voor aan door bij naar uit over"
          " tot onder na tussen af toe van naar" )

pronouns = ( " ik jij u je hij zij ze wij we jullie men"
             " mij me jou je hem haar ons jullie hen" 
             " mijn jouw  uw zijn haar hun" 
             " zelf mezelf zich zichzelf zijn haar" 
             " die dat dit deze")

connectives = " en of als zoals maar omdat dus"

others = " om te er hier daar ook nu dan nog weer wel zo toen"

stopwords = (determiners + aux_verbs + preps + pronouns + connectives + others).split()


def remove_stopwords(tokens, ignore_case=False, remove_punc=False, others=[]):
    """
    Removes stopwords (by default only lower case)from a list of tokens, where
    ignore_case is a boolean indicating whether upper/lower case should be ignored, 
    remove_punc is a boolean indicating whether punctuation is to be removed, and 
    others is a list of additional stopwords.
    Returns filtered list of tokens.
    """
    if remove_punc:
        remove = stopwords + list(punctuation) + others
    else:
        remove = stopwords + others
        
    if ignore_case:
        return [t for t in tokens if t.lower() not in remove]
    else:
        return [t for t in tokens if t not in remove]
    

