# -*- coding: UTF-8 -*-
##
#
#   Regex
#   @version: 1.0.0
#
#   A simple & generic Regular Expression Analyzer & Composer for PHP, Python, Node/XPCOM/JS, Java, C/C++, ActionScript
#   https://github.com/foo123/Analyzer
#
##
import random, math, re, copy


def is_array(x):
    return isinstance(x,(list,tuple))
    
def is_string(x):
    return isinstance(x,str)
    
TYPE_REGEXP = None
def is_regexp(x):
    global TYPE_REGEXP
    if TYPE_REGEXP is None: TYPE_REGEXP = type(re.compile(r'[a-z]'))
    return isinstance(x,TYPE_REGEXP)
    
def array( x ):
    return x if is_array(x) else [x]

def is_nan(v):
    return math.isnan(v)
    
def rnd(a, b):
    return random.randint(a, b)

def esc_re( s, esc, chargroup=False ):
    es = ''
    l = len(s)
    i=0
    #escaped_re = /([.*+?^${}()|[\]\/\\\-])/g
    if chargroup:
        while i < l:
            c = s[i]
            i += 1
            es += (esc if ('-' == c) or ('^' == c) or ('$' == c) or ('|' == c) or ('{' == c) or ('}' == c) or ('(' == c) or (')' == c) or ('[' == c) or (']' == c) or ('/' == c) or (esc == c) else '') + c
    else:
        while i < l:
            c = s[i]
            i += 1
            es += (esc if ('?' == c) or ('*' == c) or ('+' == c) or ('.' == c) or ('^' == c) or ('$' == c) or ('|' == c) or ('{' == c) or ('}' == c) or ('(' == c) or (')' == c) or ('[' == c) or (']' == c) or ('/' == c) or (esc == c) else '') + c
    return es

def pad( s, n, z='0' ):
    ps = str(s)
    while len(ps) < n: ps = z + ps
    return ps

def char_code( c ):
    return ord(c[0])
    
def char_code_range( s ):
    return [ord(s[0]), ord(s[-1])]
    
def concat( p1, p2=None ):
    if p2:
        if is_array(p2):
            for p in p2: p1[ p ] = 1
        else:
            for p in p2:  p1[ p ] = 1;
    return p1

def character_range( first=None, last=None ):
    if first and is_array(first):
        last = first[1]
        first = first[0]
    
    start = ord(first[0]) 
    end = ord(last[0])
    
    if end == start: return [ chr( start ) ]
    
    chars = []
    for ch in range(start, end+1, 1):
        chars.append(chr( ch ))
    
    return chars

BSPACES = ["\r","\n"]
SPACES = [" ","\t","\v"]
PUNCTS = ["~","!","@","#","$","%","^","&","*","(",")","-","+","=","[","]","{","}","\\","|",";",":",",",".","/","<",">","?"]
DIGITS = ["0","1","2","3","4","5","6","7","8","9"]
DIGITS_RANGE = char_code_range(DIGITS)
HEXDIGITS_RANGES = [DIGITS_RANGE, [char_code("a"), char_code("f")], [char_code("A"), char_code("F")]]
ALPHAS = ["_"]+character_range("a", "z")+character_range("A", "Z")
ALL = SPACES+PUNCTS+DIGITS+ALPHAS

T_SEQUENCE = 1
T_ALTERNATION = 2
T_GROUP = 4
T_CHARGROUP = 8
T_QUANTIFIER = 16
T_UNICODECHAR = 32
T_HEXCHAR = 64
T_SPECIAL = 128
T_CHARS = 256
T_CHARRANGE = 512
T_STRING = 1024
T_COMMENT = 2048
ESC = '\\'

class _G():
    specialChars = {
        "." : "MatchAnyChar",
        "|" : "MatchEither",
        "?" : "MatchZeroOrOne",
        "*" : "MatchZeroOrMore",
        "+" : "MatchOneOrMore",
        "^" : "MatchStart",
        "$" : "MatchEnd",
        "{" : "StartRepeats",
        "}" : "EndRepeats",
        "(" : "StartGroup",
        ")" : "EndGroup",
        "[" : "StartCharGroup",
        "]" : "EndCharGroup"
    }
    specialCharsEscaped = {
        "\\" : "ESC",
        "/" : "/",
        "0" : "NULChar",
        "f" : "FormFeed",
        "n" : "LineFeed",
        "r" : "CarriageReturn",
        "t" : "HorizontalTab",
        "v" : "VerticalTab",
        "b" : "MatchWordBoundary",
        "B" : "MatchNonWordBoundary",
        "s" : "MatchSpaceChar",
        "S" : "MatchNonSpaceChar",
        "w" : "MatchWordChar",
        "W" : "MatchNonWordChar",
        "d" : "MatchDigitChar",
        "D" : "MatchNonDigitChar"
    }
    BSPACES = BSPACES
    SPACES = SPACES
    PUNCTS = PUNCTS
    DIGITS = DIGITS
    DIGITS_RANGE = DIGITS_RANGE
    HEXDIGITS_RANGES = HEXDIGITS_RANGES
    ALPHAS = ALPHAS
    ALL = ALL

class RE_OBJ():
    def __init__(self, regex):
        self.re = regex
        self.len = len(regex)
        self.pos = 0
        self.index = 0
        self.groupIndex = 0
        self.group = {}
        self.inGroup = 0
    
    def dispose(self):
        self.re = None
        self.len = None
        self.pos = None
        self.index = None
        self.groupIndex = None
        self.group = None
        self.inGroup = None
    
    def __del__(self):
        self.dispose()
 

class Node():
    def toObjectStatic( v ):
        if isinstance(v,Node):
            return {
                'type': v.typeName,
                'value': Node.toObjectStatic(v.val),
                'flags': v.flags
            } if v.flags and len(v.flags) else {
                'type': v.typeName,
                'value': Node.toObjectStatic(v.val)
            }
        elif is_array(v):
            return list(map(Node.toObjectStatic, v))
        return v
    
    def __init__(self, type, value, flags=None):
        self.type = type
        self.val = value
        self.flags = flags if flags else {}
        if T_SEQUENCE == type: 
            self.typeName = "Sequence"
        elif T_ALTERNATION == type: 
            self.typeName = "Alternation"
        elif T_GROUP == type: 
            self.typeName = "Group"
        elif T_CHARGROUP == type: 
            self.typeName = "CharacterGroup"
        elif T_CHARS == type: 
            self.typeName = "Characters"
        elif T_CHARRANGE == type: 
            self.typeName = "CharacterRange"
        elif T_STRING == type: 
            self.typeName = "String"
        elif T_QUANTIFIER == type: 
            self.typeName = "Quantifier"
        elif T_UNICODECHAR == type: 
            self.typeName = "UnicodeChar"
        elif T_HEXCHAR == type: 
            self.typeName = "HexChar"
        elif T_SPECIAL == type: 
            self.typeName = "Special"
        elif T_COMMENT == type: 
            self.typeName = "Comment"
        else: self.typeName = "unspecified"
    
    def __del__(self):
        self.dispose()
        
    def dispose(self):
        self.val = None
        self.flags = None
        self.type = None
        self.typeName = None
        return self
    
    def toObject(self):
        return Node.toObjectStatic(self)


def match_chars( CHARS, s, pos=0, minlen=1, maxlen=100 ):
    #if maxlen < 0: maxlen = float("inf")
    lp = pos
    l = 0
    sl = len(s)
    while (lp < sl) and (l <= maxlen) and (s[lp] in CHARS): 
        lp+=1
        l+=1
    return l if l >= minlen else False

def match_char_range( RANGE, s, pos=0, minlen=1, maxlen=100 ):
    #if maxlen < 0: maxlen = float("inf")
    lp = pos
    l = 0
    sl = len(s)
    found = True
    while (lp < sl) and (l <= maxlen) and found:
        ch = ord(s[lp])
        if ch >= RANGE[0] and ch <= RANGE[1]:
            lp+=1 
            l+=1
        else: found = False
    
    return l if l >= minlen else False

def match_char_ranges( RANGES, s, pos=0, minlen=1, maxlen=100 ):
    #if maxlen < 0: maxlen = float("inf")
    lp = pos
    l = 0
    sl = len(s)
    found = True
    while (lp < sl) and (l <= maxlen) and found:
        ch = ord(s[lp])
        found = False
        for RANGE in RANGES:
            if ch >= RANGE[0] and ch <= RANGE[1]:
                lp+=1 
                l+=1 
                found = True
                break
            
            
    return l if l >= minlen else False

def punct( ):
    global _G
    return _G.PUNCTS[rnd(0, len(_G.PUNCTS)-1)] 

def space( positive=True ):
    global _G
    if positive is not False:
        return _G.SPACES[rnd(0, len(_G.SPACES)-1)] 
    else:
        return [punct(),digit(),alpha()][rnd(0,2)]

def digit( positive=True ):
    global _G
    if positive is not False:
        return _G.DIGITS[rnd(0, len(_G.DIGITS)-1)] 
    else:
        return [punct(),space(),alpha()][rnd(0,2)]

def alpha( positive=True ):
    global _G
    if positive is not False:
        return _G.ALPHAS[rnd(0, len(_G.ALPHAS)-1)] 
    else:
        return [punct(),space(),digit()][rnd(0,2)]

def word( positive=True ):
    global _G
    if positive is not False:
        s = _G.ALPHAS+_G.DIGITS
        return s[rnd(0, len(s)-1)] 
    else:
        return [punct(),space()][rnd(0,1)]

def any( ):
    global _G
    return _G.ALL[rnd(0, len(_G.ALL)-1)]

def character( chars, positive=True ):
    global _G
    if positive is not False:
        l = len(chars)
        return chars[rnd(0, l-1)] if l else ''
    else:
        choices = []
        for choice in _G.ALL:
            if choice not in chars: choices.append(choice)
        l = len(choices)
        return choices[rnd(0, l-1)] if l else ''

def random_upper_or_lower( c ): 
    return str(c).lower() if rnd(0,1) else str(c).upper()

def case_insensitive( chars, asArray=False ):
    if asArray:
    
        if isinstance(chars, str): chars = chars.split('')
        chars = list(map( random_upper_or_lower, chars ))
        return chars
    
    else:
        return random_upper_or_lower( chars )
    
def walk( ret, node, state ):
    if (node is None) or (not state): return ret
    
    type = node.type if isinstance(node, Node) else None
    
    # walk the tree
    if type is None:
        # custom, let reduce handle it
        ret = state['reduce']( ret, node, state )
        
    elif state['IGNORE'] & type:
        # nothing
        pass
    
    elif state['MAP'] & type:
        r = state['map']( ret, node, state )
        if ('ret' in state) and (state['ret'] is not None):
            ret = state['reduce']( ret, node, state )
            state['ret'] = None
        
        elif r is not None:
            r = array(r)
            for ri in r:
                state['node'] = node
                ret = walk( ret, ri, state )
                if ('stop' in state) and state['stop']:
                    state['stop'] = None
                    return ret
    
    elif state['REDUCE'] & type:
        ret = state['reduce']( ret, node, state )
    
    state['node'] = None
    return ret

def map_src( ret, node, state ):
    type = node.type
    if T_ALTERNATION == type:
        r = []
        l = len(node.val)-1
        for i in range(l):
            r.append(node.val[i])
            r.append('|')
        r.append(node.val[l])
        return r
    
    elif T_CHARGROUP == type:
        return ['['+('^' if 'NegativeMatch' in node.flags else '')] + array(node.val) + [']']
    
    elif T_QUANTIFIER == type:
        q = ''
        if 'MatchZeroOrOne' in node.flags: q = '?'
        elif 'MatchZeroOrMore' in node.flags: q = '*'
        elif 'MatchOneOrMore' in node.flags: q = '+'
        else: q = ('{'+str(node.flags['min'])+'}') if node.flags['min'] == node.flags['max'] else ('{'+str(node.flags['min'])+','+('' if -1==node.flags['max'] else str(node.flags['max']))+'}')
        if (node.flags['min'] != node.flags['max']) and not node.flags['isGreedy']: q += '?'
        return array(node.val) + [q]
    
    elif T_GROUP == type:
        g = None
        if 'NotCaptured' in node.flags:
            g = ['(?:'] + array(node.val) + [')']
        
        elif 'LookAhead' in node.flags:
            g = ['(?='] + array(node.val) + [')']
        
        elif 'NegativeLookAhead' in node.flags:
            g = ['(?!'] + array(node.val) + [')']
        
        elif 'LookBehind' in node.flags:
            g = ['(?<='] + array(node.val) + [')']
        
        elif 'NegativeLookBehind' in node.flags:
            g = ['(?<!'] + array(node.val) + [')']
        
        else:
            g = ['('] + array(node.val) + [')']
        if 'GroupIndex' in node.flags:
            ret['group'][str(node.flags['GroupIndex'])] = node.flags['GroupIndex']
            if 'GroupName' in node.flags: ret['group'][node.flags['GroupName']] = node.flags['GroupIndex']
        return g
    
    return node.val

def map_any( ret, node, state ):
    type = node.type
    if (T_ALTERNATION == type) or (T_CHARGROUP == type):
        return node.val[rnd(0, len(node.val)-1)] if len(node.val) else None
    
    elif T_QUANTIFIER == type:
        if len(ret) >= state['maxLength']:
            numrepeats = node.flags['min']
        
        else:
            mmin = node.flags['min']
            mmax = (mmin+1+2*state['maxLength']) if -1==node.flags['max'] else node.flags['max']
            numrepeats = rnd(mmin, mmax)
        return [node.val] * numrepeats if numrepeats else None
    
    elif (T_GROUP == type) and ('GroupIndex' in node.flags):
        sample = walk('', node.val, state)
        state['group'][str(node.flags['GroupIndex'])] = sample
        state['ret'] = sample
        return None
    
    else:
        return node.val

def map_min( ret, node, state ):
    type = node.type
    if T_ALTERNATION == type:
        l = len(node.val)
        min = walk(0, node.val[0], state) if l else 0
        i = 1
        while i < l:
            cur = walk(0, node.val[i], state)
            if cur < min: min = cur
            i += 1
        if l: state['ret'] = min
        return None
    
    elif T_CHARGROUP == type:
        return node.val[0] if len(node.val) else None
    
    elif T_QUANTIFIER == type:
        if 0==node.flags['min']: return None
        return [node.val] * node.flags['min']
    
    elif (T_GROUP == type) and ('GroupIndex' in node.flags):
        min = walk(0, node.val, state)
        state['group'][str(node.flags['GroupIndex'])] = min
        state['ret'] = min
        return None
    
    else:
        return node.val

def map_max( ret, node, state ):
    type = node.type
    if T_ALTERNATION == type:
        l = len(node.val)
        max = walk(0, node.val[0], state) if l else 0
        if -1 != max:
            i = 1
            while i<l:
                cur = walk(0, node.val[i], state)
                if -1 == cur:
                    max = -1
                    break
                elif cur > max:
                    max = cur
                i += 1
        if l: state['ret'] = max
        return None
    
    elif T_CHARGROUP == type:
        return node.val[0] if len(node.val) else None
    
    elif T_QUANTIFIER == type:
        max = walk(0, node.val, state)
        if -1 == max:
            state['ret'] = -1
        elif 0 < max:
            if -1 == node.flags['max']:
                state['ret'] = -1
            elif 0 < node.flags['max']:
                state['ret'] = node.flags['max']*max
            else:
                state['ret'] = max
        return None
    
    elif (T_GROUP == type) and ('GroupIndex' in node.flags):
        max = walk(0, node.val, state)
        state['group'][str(node.flags['GroupIndex'])] = max
        state['ret'] = max
        return None
    
    else:
        return node.val
    
def map_1st( ret, node, state ):
    type = node.type
    if T_SEQUENCE == type:
        seq = []
        for n in node.val:
            seq.append( n )
            if (T_QUANTIFIER == n.type) and (0 == n.flags['min']):
                continue
            elif (T_SPECIAL == n.type) and (('MatchStart' in n.flags) or ('MatchEnd' in n.flags)):
                continue
            break
        return seq if len(seq) else None
    
    else:
        return node.val

def reduce_len( ret, node, state ):
    if ('ret' in state) and state['ret'] is not None:
        if -1 == state['ret']: ret = -1
        else: ret += state['ret']
        return ret
    if -1 == ret: return ret
    
    if isinstance(node, int):
        ret += node
        return ret
        
    if (T_SPECIAL == node.type) and ('MatchEnd' in node.flags):
        state['stop'] = 1
        return ret
        
    type = node.type;
    if (T_CHARS == type) or (T_CHARRANGE == type) or (T_UNICODECHAR == type) or (T_HEXCHAR == type) or ((T_SPECIAL == type) and ('MatchStart' not in node.flags) and ('MatchEnd' not in node.flags)):
        ret += (state['group'][node.val] if node.val in state['group'] else 0) if 'BackReference' in node.flags else 1
    
    elif T_STRING == type:
        ret += len(node.val)
    
    return ret

def reduce_str( ret, node, state ):
    if ('ret' in state) and state['ret'] is not None:
        ret += str(state['ret'])
        return ret
    
    if is_string(node):
        ret += node
        return ret
        
    if (T_SPECIAL == node.type) and ('MatchEnd' in node.flags):
        state['stop'] = 1
        return ret
        
    type = node.type
    sample = None
    
    if T_CHARS == type:
        sample = node.val
    elif T_CHARRANGE == type:
        range = [node.val[0],node.val[1]]
        if isinstance(range[0],Node) and (T_UNICODECHAR == range[0].type or T_HEXCHAR == range[0].type): range[0] = range[0].flags['Char']
        if isinstance(range[1],Node) and (T_UNICODECHAR == range[1].type or T_HEXCHAR == range[1].type): range[1] = range[1].flags['Char']
        sample = character_range(range)
    elif (T_UNICODECHAR == type) or (T_HEXCHAR == type):
        sample = [node.flags['Char']]
    elif (T_SPECIAL == type) and ('MatchStart' not in node.flags) and ('MatchEnd' not in node.flags):
        part = node.val
        if 'BackReference' in node.flags:
            ret += state['group'][part] if part in state['group'] else ''
            return ret
        elif 'D' == part: sample = [digit( False )]
        elif 'W' == part: sample = [word( False )]
        elif 'S' == part: sample = [space( False )]
        elif 'd' == part: sample = [digit( )]
        elif 'w' == part: sample = [word( )]
        elif 's' == part: sample = [space( )]
        elif ('.' == part) and ('MatchAnyChar' in node.flags): sample = [any( )]
        else: sample = [ESC + part]
    elif T_STRING == type:
        sample = node.val
    
    if sample is not None:
        ret += (case_insensitive(sample) if state['isCaseInsensitive'] else sample) if T_STRING == type else character(case_insensitive(sample, True) if state['isCaseInsensitive'] else sample, ('node' not in state) or ('NegativeMatch' not in state['node'].flags))
    
    return ret

def reduce_src( ret, node, state ):
    if ('ret' in state) and state['ret'] is not None:
        if 'src' in statep['ret']: ret['src'] += state['ret']['src']
        if 'group' in state['ret']: ret['group'].update(state['ret']['group'])
        return ret
    
    if is_string(node):
        ret['src'] += node
        return ret
    
    type = node.type
    if T_CHARS == type:
        ret['src'] += esc_re(''.join(node.val), ESC, 1) if state['escaped'] else ''.join(node.val)
    elif T_CHARRANGE == type:
        range = [node.val[0],node.val[1]]
        if state['escaped']:
            if isinstance(range[0],Node) and T_UNICODECHAR == range[0].type: range[0] = ESC+'u'+pad(range[0].flags['Code'],4)
            elif isinstance(range[0],Node) and T_HEXCHAR == range[0].type: range[0] = ESC+'x'+pad(range[0].flags['Code'],2)
            else: range[0] = esc_re(range[0], ESC, 1)
            if isinstance(range[1],Node) and T_UNICODECHAR == range[1].type: range[1] = ESC+'u'+pad(range[1].flags['Code'],4)
            elif isinstance(range[1],Node) and T_HEXCHAR == range[1].type: range[1] = ESC+'x'+pad(range[1].flags['Code'],2)
            else: range[1] = esc_re(range[1], ESC, 1)
        else:
            if isinstance(range[0],Node) and (T_UNICODECHAR == range[0].type or T_HEXCHAR == range[0].type): range[0] = range[0].flags['Char']
            if isinstance(range[0],Node) and (T_UNICODECHAR == range[1].type or T_HEXCHAR == range[1].type): range[1] = range[1].flags['Char']
        ret['src'] += range[0]+'-'+range[1]
    elif T_UNICODECHAR == type:
        ret['src'] += ESC+'u'+pad(node.flags['Code'],4) if state['escaped'] else node.flags['Char']
    elif T_HEXCHAR == type:
        ret['src'] += ESC+'x'+pad(node.flags['Code'],2) if state['escaped'] else node.flags['Char']
    elif T_SPECIAL == type:
        if 'BackReference' in node.flags:
            ret['src'] += ESC+node.val
        else:
            ret['src'] += ESC+node.val if ('MatchStart' not in node.flags) and ('MatchEnd' not in node.flags) else( ''+node.val)
    elif T_STRING == type:
        ret['src'] += esc_re(node.val, ESC) if state['escaped'] else node.val
    
    return ret

def reduce_peek( ret, node, state ):
    if ('ret' in state) and state['ret'] is not None:
        ret['positive'] = concat( ret['positive'], state['ret']['positive'] )
        ret['negative'] = concat( ret['negative'], state['ret']['negative'] )
        return ret
    if (T_SPECIAL == node.type) and ('MatchEnd' not in node.flags):
        state['stop'] = 1
        return ret
        
    type = node.type
    inCharGroup = ('node' in state) and (T_CHARGROUP == state['node'].type)
    inNegativeCharGroup = inCharGroup and ('NotMatch' in state['node'].flags)
    peek = "negative" if inNegativeCharGroup else "positive"
    
    if T_CHARS == type:
        ret[peek] = concat( ret[peek], node.val )
    elif T_CHARRANGE == type:
        range = [node.val[0],node.val[1]]
        if isinstance(range[0],Node) and (T_UNICODECHAR == range[0].type or T_HEXCHAR == range[0].type): range[0] = range[0].flags['Char']
        if isinstance(range[1],Node) and (T_UNICODECHAR == range[1].type or T_HEXCHAR == range[1].type): range[1] = range[1].flags['Char']
        ret[peek] = concat( ret[peek], character_range(range) )
    elif (T_UNICODECHAR == type) or (T_HEXCHAR == type):
        ret[peek][node.flags['Char']] = 1
    elif (T_SPECIAL == type) and ('BackReference' not in node.flags)  and ('MatchStart' not in node.flags) and ('MatchEnd' not in node.flags):
        part = node.val
        if 'D' == part:
            ret["positive" if inNegativeCharGroup else "negative"][ '\\d' ] = 1
        elif 'W' == part:
            ret["positive" if inNegativeCharGroup else "negative"][ '\\w' ] = 1
        elif 'S' == part:
            ret["positive" if inNegativeCharGroup else "negative"][ '\\s' ] = 1
        else:
            ret[peek][ESC + part] = 1
    elif T_STRING == type:
        ret["positive"][node.val[0]] = 1
    
    return ret


def match_hex( s ):
    global _G
    m = False
    if (len(s) > 2) and ('x' == s[0]):
    
        if match_char_ranges(_G.HEXDIGITS_RANGES, s, 1, 2, 2): 
            m=s[0:3]
            return [m, m[1:]]
    
    return False

def match_unicode( s ):
    global _G
    m = False
    if (len(s) > 4) and ('u' == s[0]):
    
        if match_char_ranges(_G.HEXDIGITS_RANGES, s, 1, 4, 4): 
            m=s[0:5]
            return [m, m[1:]]
    
    return False

def match_repeats( s ):
    global _G
    pos = 0 
    m = False
    hasComma = False
    sl = len(s);
    if (sl > 2) and ('{' == s[pos]):
    
        m = ['', '', None]
        pos+=1
        l=match_chars(_G.SPACES, s, pos)
        if l: pos += l
        l=match_char_range(_G.DIGITS_RANGE, s, pos)
        if l:
            m[1] = s[pos:pos+l]
            pos += l
        else:
            return False
        l=match_chars(_G.SPACES, s, pos)
        if l: pos += l
        if (pos<sl) and (',' == s[pos]):
            pos += 1
            hasComma = True
        l=match_chars(_G.SPACES, s, pos)
        if l: pos += l
        l=match_char_range(_G.DIGITS_RANGE, s, pos)
        if l:
            m[2] = s[pos:pos+l]
            pos += l
        l=match_chars(_G.SPACES, s, pos)
        if l: pos += l
        if (pos<sl) and ('}' == s[pos]):
            pos+=1
            m[0] = s[0:pos]
            if not hasComma: m[2] = m[1]
            return m
        else:
            return False
    
    return False


def chargroup( re_obj ):
    global _G
    sequence = []
    allchars = []
    chars = []
    flags = {}
    isRange = False
    escaped = False
    ch = ''
    
    if '^' == re_obj.re[re_obj.pos]:
    
        flags[ "NegativeMatch" ] = 1
        re_obj.pos+=1
    
    lre = re_obj.len
    while re_obj.pos < lre:
    
        isUnicode = False
        isHex = False
        prevch = ch
        ch = re_obj.re[re_obj.pos]
        re_obj.pos+=1
        
        escaped = True if ESC == ch else False
        if escaped:  
            ch = re_obj.re[re_obj.pos]
            re_obj.pos+=1
        
        if escaped:
        
            # unicode character
            if 'u' == ch:
            
                m = match_unicode( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                ch = Node(T_UNICODECHAR, m[0], {"Char": chr(int(m[1], 16)), "Code": m[1]})
                isUnicode = True
                isHex = False
            
            
            # hex character
            elif 'x' == ch:
            
                m = match_hex( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                ch = Node(T_HEXCHAR, m[0], {"Char": chr(int(m[1], 16)), "Code": m[1]})
                isUnicode = True
                isHex = True
        
        
        if isRange:
        
            if len(chars):
            
                allchars = allchars + chars
                chars = []
            
            range[1] = ch
            isRange = False
            sequence.append( Node(T_CHARRANGE, range) )
        
        else:
        
            if escaped:
            
                if isUnicode:
                    
                    if len(chars):
                    
                        allchars = allchars + chars
                        chars = []
            
                    sequence.append( ch )
                
                elif (ch in _G.specialCharsEscaped) and ('/' != ch):
                
                    if len(chars):
                    
                        allchars = allchars + chars
                        chars = []
            
                    flag = {}
                    flag[ _G.specialCharsEscaped[ch] ] = 1
                    sequence.append( Node(T_SPECIAL, ch, flag) )
                
                
                else:
                
                    chars.append( ch )
                
            
            
            else:
            
                # end of char group
                if ']' == ch:
                
                    if len(chars):
                    
                        allchars = allchars + chars
                        chars = []
                    
                    # map all chars into one node
                    if len(allchars): sequence.append( Node(T_CHARS, allchars) )
                    return Node(T_CHARGROUP, sequence, flags)
                
                
                elif '-' == ch:
                
                    range = [prevch, '']
                    if isinstance(prevch,Node): sequence.pop()
                    else: chars.pop()
                    isRange = True
                
                
                else:
                
                    chars.append( ch )
                
            
        
    
    if len(chars):
    
        allchars = allchars + chars
        chars = []
    
    # map all chars into one node
    if len(allchars): sequence.append( Node(T_CHARS, allchars) )
    return Node(T_CHARGROUP, sequence, flags)


def analyze_re( re_obj ):
    global _G
    word = ''
    wordlen = 0
    alternation = []
    sequence = []
    flags = {}
    escaped = False
    ch = ''
    
    if re_obj.inGroup > 0:
        pre = re_obj.re[re_obj.pos:re_obj.pos+2]
        pre3 = re_obj.re[re_obj.pos:re_obj.pos+3]
        captured = 1
        
        if "?P=" == pre3:
            
            flags[ "BackReference" ] = 1
            flags[ "GroupName" ] = ''
            re_obj.pos += 3
            lre = re_obj.len
            while re_obj.pos < lre:
                ch = re_obj.re[ re_obj.pos ]
                re_obj.pos += 1
                if ")" == ch: break
                flags[ "GroupName" ] += ch
            flags[ "GroupIndex" ] = re_obj.group[flags[ "GroupName" ]] if flags[ "GroupName" ] in re_obj.group else None
            return Node(T_SPECIAL, str(flags[ "GroupIndex" ]), flags)
        
        elif "?#" == pre:
            
            re_obj.pos += 2
            word = ''
            lre = re_obj.len
            while re_obj.pos < lre:
                ch = re_obj.re[ re_obj.pos ]
                re_obj.pos += 1
                if ")" == ch: break
                word += ch
            return Node(T_COMMENT, word)
        
        elif "?:" == pre:
        
            flags[ "NotCaptured" ] = 1
            re_obj.pos += 2
            captured = 0
        
        
        elif "?=" == pre:
        
            flags[ "LookAhead" ] = 1
            re_obj.pos += 2
            captured = 0
        
        
        elif "?!" == pre:
        
            flags[ "NegativeLookAhead" ] = 1
            re_obj.pos += 2
            captured = 0
        
        
        elif "?<=" == pre3:
        
            flags[ "LookBehind" ] = 1
            re_obj.pos += 3
            captured = 0
        
        
        elif "?<!" == pre3:
        
            flags[ "NegativeLookBehind" ] = 1
            re_obj.pos += 3
            captured = 0
        
        
        elif ("?<" == pre) or ("?P<" == pre3):
        
            flags[ "NamedGroup" ] = 1
            flags[ "GroupName" ] = ''
            re_obj.pos += 2 if "?<" == pre else 3
            lre = re_obj.len
            while re_obj.pos < lre:
                ch = re_obj.re[ re_obj.pos ]
                re_obj.pos += 1
                if ">" == ch: break
                flags[ "GroupName" ] += ch

        re_obj.index+=1
        if captured:
            re_obj.groupIndex+=1
            flags[ "GroupIndex" ] = re_obj.groupIndex
            re_obj.group[str(flags[ "GroupIndex" ])] = flags[ "GroupIndex" ]
            if "GroupName" in flags: re_obj.group[flags[ "GroupName" ]] = flags[ "GroupIndex" ]
    
    lre = re_obj.len
    while re_obj.pos < lre:
    
        ch = re_obj.re[re_obj.pos]
        re_obj.pos+=1
        
        #   \\abc
        escaped = True if ESC == ch else False
        if escaped:  
            ch = re_obj.re[re_obj.pos]
            re_obj.pos+=1
        
        if escaped:
        
            # unicode character
            if 'u' == ch:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                m = match_unicode( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                sequence.append( Node(T_UNICODECHAR, m[0], {"Char": chr(int(m[1], 16)), "Code": m[1]}) )
            
            
            # hex character
            elif 'x' == ch:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                m = match_hex( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                sequence.append( Node(T_HEXCHAR, m[0], {"Char": chr(int(m[1], 16)), "Code": m[1]}) )
            
            
            elif (ch in _G.specialCharsEscaped) and ('/' != ch):
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                flag = {}
                flag[ _G.specialCharsEscaped[ch] ] = 1
                sequence.append( Node(T_SPECIAL, ch, flag) )
            
            
            elif ('1' <= ch) and ('9' >= ch):
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                word = ch
                while re_obj.pos < lre:
                    ch = re_obj.re[ re_obj.pos ]
                    if ('0' <= ch) and ('9' >= ch):
                        word += ch
                        re_obj.pos += 1
                    else: break
                
                flag = {}
                flag[ 'BackReference' ] = 1
                flag[ 'GroupIndex' ] = int(word, 10)
                sequence.append( Node(T_SPECIAL, word, flag) )
                word = ''
            
            else:
            
                word += ch
                wordlen += 1
            
        
        
        else:
        
            # group end
            if (re_obj.inGroup > 0) and (')' == ch):
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                if len(alternation):
                
                    alternation.append( Node(T_SEQUENCE, sequence) )
                    sequence = []
                    flag = {}
                    flag[ _G.specialChars['|'] ] = 1
                    return Node(T_GROUP, Node(T_ALTERNATION, alternation, flag), flags)
                
                else:
                
                    return Node(T_GROUP, Node(T_SEQUENCE, sequence), flags)
                
            
            
            # parse alternation
            elif '|' == ch:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                alternation.append( Node(T_SEQUENCE, sequence) )
                sequence = []
            
            
            # parse character group
            elif '[' == ch:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                sequence.append( chargroup( re_obj ) )
            
            
            # parse sub-group
            elif '(' == ch:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                re_obj.inGroup+=1
                sequence.append( analyze_re( re_obj ) )
                re_obj.inGroup-=1
            
            
            # parse num repeats
            elif '{' == ch:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                m = match_repeats( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                flag = { 'val': m[0], "MatchMinimum": m[1], "MatchMaximum": m[2] if m[2] else "unlimited", 'min': int(m[1],10), 'max': int(m[2],10) if m[2] else -1}
                flag[ _G.specialChars[ch] ] = 1
                if (re_obj.pos<lre) and ('?' == re_obj.re[re_obj.pos]):
                
                    flag[ "isGreedy" ] = 0
                    re_obj.pos+=1
                
                else:
                    
                    flag[ "isGreedy" ] = 1
                
                prev = sequence.pop()
                if T_STRING == prev.type and len(prev.val) > 1:
                
                    sequence.append( Node(T_STRING, prev.val[0:-1]) )
                    prev.val = prev.val[-1]
                
                sequence.append( Node(T_QUANTIFIER, prev, flag) )
            
            
            # quantifiers
            elif ('*' == ch) or ('+' == ch) or ('?' == ch):
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                flag['min'] = 1 if '+' == ch else 0
                flag['max'] = 1 if '?' == ch else -1
                if (re_obj.pos<lre) and ('?' == re_obj.re[re_obj.pos]):
                
                    flag[ "isGreedy" ] = 0
                    re_obj.pos+=1
                
                else:
                
                    flag[ "isGreedy" ] = 1
                
                prev = sequence.pop()
                if T_STRING == prev.type and len(prev.val) > 1:
                
                    sequence.append( Node(T_STRING, prev.val[0:-1]) )
                    prev.val = prev.val[-1]
                
                sequence.append( Node(T_QUANTIFIER, prev, flag) )
            
        
            # special characters like ^, $, ., etc..
            elif ch in _G.specialChars:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                sequence.append( Node(T_SPECIAL, ch, flag) )
            
        
            elif ('1' <= ch) and ('9' >= ch):
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                word = ch
                while re_obj.pos < lre:
                    ch = re_obj.re[ re_obj.pos ]
                    if ('0' <= ch) and ('9' >= ch):
                        word += ch
                        re_obj.pos += 1
                    else: break
                
                flag = {}
                flag[ 'BackReference' ] = 1
                flag[ 'GroupIndex' ] = int(word, 10)
                sequence.append( Node(T_SPECIAL, word, flag) )
                word = ''
            
        
            else:
            
                word += ch
                wordlen += 1
            
        
    
    
    if wordlen:
    
        sequence.append( Node(T_STRING, word) )
        word = ''
        wordlen = 0
                
    
    if len(alternation):
    
        alternation.append( Node(T_SEQUENCE, sequence) )
        sequence = []
        flag = {}
        flag[ _G.specialChars['|'] ] = 1
        return Node(T_ALTERNATION, alternation, flag)
    
    return Node(T_SEQUENCE, sequence)
    



# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
# https://docs.python.org/3/library/re.html
# http://php.net/manual/en/reference.pcre.pattern.syntax.php
# A simple regular expression analyzer
class Analyzer:
    VERSION = "1.0.0"
    
    def __init__(self, re=None, delim='/'):
        self.ast = None
        self.re = None
        self.fl = None
        self.src = None
        self.grp = None
        self.min = None
        self.max = None
        self.ch = None
       
        if re is not None:   
            self.input(re, delim)
            
            
    def __del__(self):
        self.dispose()
        
    def dispose( self ):
        self.ast = None
        self.re = None
        self.fl = None
        self.src = None
        self.grp = None
        self.min = None
        self.max = None
        self.ch = None
        return self
    
    def reset(self):
        self.ast = None
        self.src = None
        self.grp = None
        self.min = None
        self.max = None
        self.ch = None
        return self
    
    # alias
    def set(self, re, delim='/'):
        return self.input(re,delim)
        
    def input(self, *args):
        lenargs = len(args)
        if not lenargs: return self.re
        re = args[0] if lenargs > 0 else None
        delim = args[1] if lenargs > 1 else None
        
        if re:
            
            if delim is False: delim = False
            elif not delim: delim = '/'
            re = str(re.pattern if is_regexp(re) else re)
            fl = {}
            l = len(re)
            
            # parse re flags, if any
            if delim:
                while 0 < l:
                    ch = re[l-1]
                    if delim == ch:
                        break
                    else:
                        fl[ ch ] = 1
                        l -= 1
                
                if 0 < l:
                    # remove re delimiters
                    if delim == re[0] and delim == re[l-1]: re = re[1:l-1]
                    else: re = re[0:l]
                else:
                    re = ''
            
            # re is different, reset the ast, etc
            if self.re != re: self.reset()
            self.re = re 
            self.fl = fl
        
        return self
        
    def analyze( self ):
        if self.re and (self.ast is None):
            re = RE_OBJ(self.re)
            self.ast = analyze_re( re )
            re.dispose()
        return self
    
    def synthesize( self, escaped=True ):
        if None == self.re: return self
        if self.ast is None:
            self.analyze( )
            self.src = None
            self.grp = None
            
        if self.src is None:
            state = {
                'MAP'                 : T_SEQUENCE|T_ALTERNATION|T_GROUP|T_CHARGROUP|T_QUANTIFIER,
                'REDUCE'              : T_UNICODECHAR|T_HEXCHAR|T_SPECIAL|T_CHARS|T_CHARRANGE|T_STRING,
                'IGNORE'              : T_COMMENT,
                'map'                 : map_src,
                'reduce'              : reduce_src,
                'escaped'             : escaped is not False,
                'group'               : {}
            }
            re = walk({'src':'','group':{}}, self.ast, state)
            self.src = re['src']
            self.grp = re['group']
        return self
    
    def source( self ):
        if not self.re: return None
        if self.src is None: self.synthesize()
        return self.src
    
    def groups( self, raw=False ):
        if not self.re: return None
        if self.grp is None: self.synthesize()
        return sel.grp if raw is True else self.grp.copy()
    
    def compile( self, flags=None ):
        if not self.re: return None
        flags = (self.fl if self.fl else {}) if not flags else flags
        return re.compile(self.source(), (re.I if ('i' in flags) or ('I' in flags) else 0) | (re.M if ('m' in flags) or ('M' in flags) else 0) | (re.S if ('s' in flags) or ('S' in flags) else 0))
    
    def tree( self, flat=False ):
        if not self.re: return None
        if self.ast is None: self.analyze( )
        return self.ast.toObject() if flat is True else self.ast
    
    # experimental feature
    def sample( self, maxlen=1, numsamples=1 ):
        if not self.re: return None
        if self.ast is None: self.analyze( )
        state = {
            'MAP'               : T_SEQUENCE|T_ALTERNATION|T_GROUP|T_CHARGROUP|T_QUANTIFIER,
            'REDUCE'            : T_UNICODECHAR|T_HEXCHAR|T_SPECIAL|T_CHARS|T_CHARRANGE|T_STRING,
            'IGNORE'            : T_COMMENT,
            'map'               : map_any,
            'reduce'            : reduce_str,
            'maxLength'         : maxlen if maxlen else 1,
            'isCaseInsensitive' : ('i' in self.fl),
            'group'             : {}
        }
        if 1 < numsamples:
            return [walk('', self.ast, state) for i in range(numsamples)]
        return walk('', self.ast, state)
    
    # experimental feature
    def minimum( self ):
        if not self.re: return 0
        if self.ast is None:
            self.analyze( )
            self.min = None
        if self.min is None:
            state = {
                'MAP'               : T_SEQUENCE|T_ALTERNATION|T_GROUP|T_CHARGROUP|T_QUANTIFIER,
                'REDUCE'            : T_UNICODECHAR|T_HEXCHAR|T_SPECIAL|T_CHARS|T_CHARRANGE|T_STRING,
                'IGNORE'            : T_COMMENT,
                'map'               : map_min,
                'reduce'            : reduce_len,
                'group'             : {}
            }
            self.min = walk(0, self.ast, state)
        return self.min
    
    # experimental feature
    def maximum( self ):
        if not self.re: return 0
        if self.ast is None:
            self.analyze( )
            self.max = None
        if self.max is None:
            state = {
                'MAP'               : T_SEQUENCE|T_ALTERNATION|T_GROUP|T_CHARGROUP|T_QUANTIFIER,
                'REDUCE'            : T_UNICODECHAR|T_HEXCHAR|T_SPECIAL|T_CHARS|T_CHARRANGE|T_STRING,
                'IGNORE'            : T_COMMENT,
                'map'               : map_max,
                'reduce'            : reduce_len,
                'group'             : {}
            }
            self.max = walk(0, self.ast, state)
        return self.max
    
    # experimental feature
    def peek( self ):
        if not self.re: return None
        if self.ast is None:
            self.analyze( )
            self.ch = None
        if self.ch is None:
            state = {
                'MAP'               : T_SEQUENCE|T_ALTERNATION|T_GROUP|T_CHARGROUP|T_QUANTIFIER,
                'REDUCE'            : T_UNICODECHAR|T_HEXCHAR|T_SPECIAL|T_CHARS|T_CHARRANGE|T_STRING,
                'IGNORE'            : T_COMMENT,
                'map'               : map_1st,
                'reduce'            : reduce_peek,
                'group'             : {}
            }
            self.ch = walk({'positive':{},'negative':{}}, self.ast, state)
        peek = {'positive':copy.copy(self.ch['positive']), 'negative':copy.copy(self.ch['negative'])}
        isCaseInsensitive = 'i' in self.fl
        for n,p in peek.items():
        
            cases = {}
            
            # either positive or negative
            for c in p.keys():
            
                if '\\d' == c:
                
                    del p[c]
                    cases = concat(cases, character_range('0', '9'))
                
                
                elif '\\s' == c:
                
                    del p[c]
                    cases = concat(cases, ['\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029'])
                
                
                elif '\\w' == c:
                
                    del p[c]
                    cases = concat(cases, ['_'] + character_range('0', '9') + character_range('a', 'z') + character_range('A', 'Z'))
                
                
                elif '\\.' == c:
                
                    del p[c]
                    cases[ _G.specialChars['.'] ] = 1
                
                
                elif (ESC != c[0]) and isCaseInsensitive:
                
                    cases[ c.lower() ] = 1
                    cases[ c.upper() ] = 1
                
                
                elif ESC == c[0]:
                
                    del p[c]
                
            
            peek[n] = concat(p, cases)
        
        return peek

def flatten( a ):
    r = []
    while len(a):
        if isinstance(a[0],(list,tuple)):
            a = list(a[0]) + a[1:]
        else:
            r.append(a[0])
            a = a[1:]
    return r

def getArgs( args ):
    return flatten(args)
    
# A simple regular expression composer
class Composer:
    VERSION = "1.0.0"
    
    def __init__( self ):
        self.re = None
        self.g = 0
        self.grp = None
        self.level = 0
        self.ast = None
        self.reset( )

    def __del__( self ):
        self.dispose( )
    
    def dispose( self ):
        self.re = None
        self.g = None
        self.grp = None
        self.level = None
        self.ast = None
        return self
    
    def reset( self ):
        self.g = 0
        self.grp = {}
        self.level = 0
        self.ast = [{'node': [], 'type': T_SEQUENCE, 'flag': ''}]
        return self

    def compose( self, flags=0 ):
        src = ''.join(self.ast[0]['node'])
        self.re = {
            'source'  : src,
            'flags'   : flags,
            'groups'  : self.grp,
            'pattern' : re.compile(src, flags)
        }
        self.reset( )
        return self.re

    def partial( self, reset=True ):
        re = ''.join(self.ast[0]['node'])
        if reset is not False: self.reset( )
        return re

    def token( self, token, escaped=False ):
        if token:
            self.ast[self.level]['node'].append(esc_re(str(token), ESC) if escaped is True else str(token))
        return self
    
    def match( self, token, escaped=False ):
        return self.token(token, escaped)
    
    def literal( self, literal ):
        return self.token(literal, True)
    
    def regexp( self, re ):
        return self.token(str(re), False)
    
    def SOL( self ):
        self.ast[self.level]['node'].append('^')
        return self
    
    def SOF( self ):
        return self.SOL( )
    
    def EOL( self ):
        self.ast[self.level]['node'].append('$')
        return self
    
    def EOF( self ):
        return self.EOL( )
    
    def LF( self ):
        self.ast[self.level]['node'].append(ESC+'n')
        return self
    
    def CR( self ):
        self.ast[self.level]['node'].append(ESC+'r')
        return self
    
    def TAB( self ):
        self.ast[self.level]['node'].append(ESC+'t')
        return self
    
    def CTRL( self, code='0' ):
        self.ast[self.level]['node'].append(ESC+'c'+str(code))
        return self
    
    def HEX( self, code='0' ):
        self.ast[self.level]['node'].append(ESC+'x'+pad(code, 2))
        return self
    
    def UNICODE( self, code='0' ):
        self.ast[self.level]['node'].append(ESC+'u'+pad(code, 4))
        return self
    
    def backSpace( self ):
        self.ast[self.level]['node'].append('['+ESC+'b]')
        return self
    
    def any( self, multiline=False ):
        self.ast[self.level]['node'].append('['+ESC+'s'+ESC+'S]' if multiline is True else '.')
        return self
    
    def space( self, positive=True ):
        self.ast[self.level]['node'].append(ESC+'S' if positive is False else ESC+'s')
        return self
    
    def digit( self, positive=True ):
        self.ast[self.level]['node'].append(ESC+'D' if positive is False else ESC+'d')
        return self
    
    def word( self, positive=True ):
        self.ast[self.level]['node'].append(ESC+'W' if positive is False else ESC+'w')
        return self
    
    def boundary( self, positive=True ):
        self.ast[self.level]['node'].append(ESC+'B' if positive is False else ESC+'b')
        return self
    
    def characters( self, *args ):
        if T_CHARGROUP == self.ast[self.level]['type']:
            self.ast[self.level]['node'].append( ''.join( list(map(lambda s: esc_re(str(s), ESC, 1), getArgs(args))) ) )
        return self
    
    def chars( self, *args ):
        if T_CHARGROUP == self.ast[self.level]['type']:
            self.ast[self.level]['node'].append( ''.join( list(map(lambda s: esc_re(str(s), ESC, 1), getArgs(args))) ) )
        return self
    
    def range( self, start, end ):
        if T_CHARGROUP == self.ast[self.level]['type']:
            self.ast[self.level]['node'].append(esc_re(str(start), ESC, 1)+'-'+esc_re(str(end), ESC, 1))
        return self
    
    def backReference( self, n ):
        n = str(n)
        self.ast[self.level]['node'].append(ESC+str(self.grp[n] if n in self.grp else n))
        return self
    
    def repeat( self, min, max=None, greedy=True ):
        repeat = ('{'+str(min)+'}' if max is None or max == min else '{'+str(min)+','+str(max)+'}') + ('?' if greedy is False else '')
        self.ast[self.level]['node'][len(self.ast[self.level]['node'])-1] += repeat
        return self
    
    def zeroOrOne( self, greedy=True ):
        self.ast[self.level]['node'][len(self.ast[self.level]['node'])-1] += ('??' if greedy is False else '?')
        return self
    
    def zeroOrMore( self, greedy=True ):
        self.ast[self.level]['node'][len(self.ast[self.level]['node'])-1] += ('*?' if greedy is False else '*')
        return self
    
    def oneOrMore( self, greedy=True ):
        self.ast[self.level]['node'][len(self.ast[self.level]['node'])-1] += ('+?' if greedy is False else '+')
        return self
    
    def alternate( self ):
        self.level += 1
        self.ast.append({'node': [], 'type': T_ALTERNATION, 'flag': ''})
        return self
    
    def either( self ):
        return self.alternate()
    
    def group( self, opts=dict() ):
        type = T_GROUP
        fl = ''
        if ('name' in opts) and len(str(opts['name'])):
            self.g += 1
            self.grp[str(self.g)] = self.g
            self.grp[str(opts['name'])] = self.g
        elif ('lookahead' in opts) and ((opts['lookahead'] is True) or (opts['lookahead'] is False)):
            fl = '?!' if opts['lookahead'] is False else '?='
        elif ('lookbehind' in opts) and ((opts['lookbehind'] is True) or (opts['lookbehind'] is False)):
            fl = '?<!' if opts['lookbehind'] is False else '?<='
        elif ('nocapture' in opts) and (opts['nocapture'] is True):
            fl = '?:';
        elif ('characters' in opts) and ((opts['characters'] is True) or (opts['characters'] is False)):
            type = T_CHARGROUP
            fl = '^' if opts['characters'] is False else ''
        else:
            self.g += 1
            self.grp[str(self.g)] = self.g
        self.level += 1
        self.ast.append({'node': [], 'type': type, 'flag': fl})
        return self
    
    def subGroup( self, opts=dict() ):
        return self.group( opts )
    
    def characterGroup( self, positive=True ):
        return self.group({'characters':positive is not False})
    
    def charGroup( self, positive=True ):
        return self.group({'characters':positive is not False})
    
    def namedGroup( self, name ):
        return self.group({'name':name})
    
    def nonCaptureGroup( self ):
        return self.group({'nocapture':True})
    
    def lookAheadGroup( self, positive=True ):
        return self.group({'lookahead':positive is not False})
    
    def lookBehindGroup( self, positive=True ):
        return self.group({'lookbehind':positive is not False})
    
    def end( self, n=1 ):
        # support ending multiple blocks at once
        if not isinstance(n, int): n = int(n, 10)
        if 0 >= n: n = 1
        while n :
            n -= 1
            prev = self.ast.pop(-1) if len(self.ast) else None
            type = prev['type'] if prev else 0
            flag = prev['flag'] if prev else ''
            part = prev['node'] if prev else []
            if 0 < self.level:
                self.level -= 1
                if T_ALTERNATION == type:
                    self.ast[self.level]['node'].append('|'.join(part))
                elif T_GROUP == type:
                    self.ast[self.level]['node'].append('('+flag+''.join(part)+')')
                elif T_CHARGROUP == type:
                    self.ast[self.level]['node'].append('['+flag+''.join(part)+']')
                else:
                    self.ast[self.level]['node'].append(''.join(part))
        return self
    
    def startOfLine( self ):
        return self.SOL( )

    def startOfInput( self ):
        return self.SOF( )

    def endOfLine( self ):
        return self.EOL( )

    def endOfInput( self ):
        return self.EOF( )


class Regex:
    """
    Regular Expressipn Analyzer and Composer for Python
    https://github.com/foo123/Analyzer
    """
    VERSION = "1.0.0"
    Node = Node
    Analyzer = Analyzer
    Composer = Composer


# if used with 'import *'
__all__ = ['Regex']
