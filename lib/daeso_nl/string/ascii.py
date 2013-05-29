# -*- coding: utf-8 -*-

"""
encode a unicode string as an ascii byte string with smart replacement

Support for encoding in ascii where iso-88591-1 characters (i.e. those code
points which can be encoded in iso-8859-1 aka latin-1) beyond ascii chars
(i.e. those code points which can be encoded in ascii) are replaced with the
closest ascii equivalant. For example, 'e-accent-grave' is replaced by plain
'e', 'o-umlaut' is replaced by plain 'o', etc. 

Importing this module will register an error handler called "smart_replace"
which can be used in combination with the "encode" method of unicode strings.

Example:

>>> import daeso_nl.string.ascii
>>> utf_8_string = "één"
>>> print utf_8_string.decode("utf-8").encode("ascii", "replace")
??n
>>> print utf_8_string.decode("utf-8").encode("ascii", "smart_replace")
een

"""

from codecs import register_error


# the mapping of iso-8859-1 chars to ascii chars 
# encoded as utf-8
_iso_to_ascii_map = """
128 
129 
130 
131 
132 
133 
134 
135 
136 
137 
138 
139 
140 
141 
142 
143 
144 
145 
146 
147 
148 
149 
150 
151 
152 
153 
154 
155 
156 
157 
158 
159 
160  
161 ¡
162 ¢ 
163 £ 
164 ¤
165 ¥
166 ¦
167 §
168 ¨
169 © c
170 ª
171 « "
172 ¬
173 ­
174 ® r
175 ¯
176 °
177 ±
178 ²
179 ³
180 ´
181 µ u
182 ¶
183 ·
184 ¸
185 ¹
186 º
187 »
188 ¼
189 ½
190 ¾
191 ¿
192 À A
193 Á A
194 Â A
195 Ã A
196 Ä A
197 Å A
198 Æ A
199 Ç C
200 È E
201 É E
202 Ê E
203 Ë E
204 Ì I
205 Í I
206 Î I
207 Ï I
208 Ð D
209 Ñ N
210 Ò O
211 Ó O
212 Ô O
213 Õ O
214 Ö O
215 × x
216 Ø O
217 Ù U
218 Ú U
219 Û U
220 Ü U
221 Ý Y
222 Þ P
223 ß B
224 à a
225 á a
226 â a
227 ã a
228 ä a
229 å a
230 æ a
231 ç c
232 è e
233 é e
234 ê e
235 ë e
236 ì i
237 í i
238 î i
239 ï i
240 ð o
241 ñ n
242 ò o
243 ó o
244 ô o
245 õ o
246 ö o
247 ÷
248 ø o
249 ù u
250 ú u
251 û u
252 ü u
253 ý y
254 þ p
255 ÿ y
"""

# the unicode char that will be subsituted if no translation is available
_unknown = u"?"


def _make_translation_table():
    # create a table mapping unicode points which can be encoded in iso-8859-1
    # to unicode points which can be encoded in ascii
    translation = {}
    
    for l in _iso_to_ascii_map.split("\n"):
        try:
            n, iso_char, ascii_char = l.strip().split()
        except ValueError:
            continue
        
        # this file is utf-8 encoded, so we have to decode
        translation[iso_char.decode("utf-8")] = ascii_char.decode("utf-8")
        
    return translation


def _error_handler(exception):
    assert exception.encoding == "ascii"
    s = "".join([ _translation.get(c, _unknown)
                  for c in exception.object[exception.start:exception.end] ])
    return (s, exception.end)
    

_translation = _make_translation_table() 
register_error("smart_replace", _error_handler)


if __name__ == "__main__":
    for l in _iso_to_ascii_map.split("\n"):
        fields = l.strip().split()
        
        try:
            n, iso_char = fields[:2] 
        except ValueError:
            continue
        
        print n, iso_char, iso_char.decode("utf8").encode("ascii", "smart_replace")
        
    