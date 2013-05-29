# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by Erwin Marsi and TST-Centrale
#
# This file is part of the DAESO Framework.
#
# The DAESO Framework is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The DAESO Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Predefined feature sets
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



from daeso_nl.ga.feature import Feat
from daeso_nl.ga.feats.word import *
from daeso_nl.ga.feats.root import *
from daeso_nl.ga.feats.pos import *
from daeso_nl.ga.feats.cornet import *
from daeso_nl.ga.feats.syntax import *
from daeso_nl.ga.feats.phrase import *
from daeso_nl.ga.feats.align import term_align

# Feature set as used in Marsi & Krahmer COLING 2010 paper
# for full tree alignment

coling10_feats = (
    # word
    word_len +
    stopword +
    word_overlap +
    word_uniq + 
    same_words_context +
    
    # root 
    root_morph +

    # pos
    pos +

    # cornet
    cornet_sim_float +

    # syntax
    cat +
    source_parent_cat + target_parent_cat +
    dep_rel +
    same_dep_head_root +

    # phrase
    phrase
    )
    
# feature set for Stevin11 chapter
# adds same_parent_pos, sim_cornet_bool and term_align
stevin11_feats = (
    # word
    word_len +
    stopword +
    word_overlap +
    word_uniq + 
    same_words_context +
    
    # root 
    root_morph +

    # pos
    pos +

    # cornet
    cornet_sim +

    # syntax
    cat +
    parent_cat +
    dep_rel +
    same_dep_head_root +

    # phrase
    phrase +
    
    # alignment
    term_align
    )

# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]
