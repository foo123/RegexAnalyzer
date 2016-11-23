# -*- coding: UTF-8 -*-
##
#
#   RegexAnalyzer
#   @version: 0.5.1
#
#   A simple Regular Expression Analyzer for PHP, Python, Node/XPCOM/JS, ActionScript
#   https://github.com/foo123/RegexAnalyzer
#
##
import random, math, re, copy

def is_nan(v):
    return math.isnan(v)
    
def rnd(a, b):
    return random.randint(a, b)

def char_code( c ):
    return ord(c[0])
    
def char_code_range( s ):
    return [ord(s[0]), ord(s[-1])]
    
def concat( p1, p2=None ):
    if p2:
        if isinstance(p2, (list, tuple)):
            for p in p2: p1[ p ] = 1
        else:
            for p in p2:  p1[ p ] = 1;
    return p1

def character_range( first=None, last=None ):
    if first and isinstance(first, (list, tuple)):
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
T_GROUP = 3
T_QUANTIFIER = 4
T_UNICODECHAR = 5
T_HEXCHAR = 6
T_SPECIAL = 7
T_CHARGROUP = 8
T_CHARS = 9
T_CHARRANGE = 10
T_STRING = 11

class _G():
    escapeChar = '\\'
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
        "\\" : "EscapeChar",
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
        self.groupIndex = 0
        self.inGroup = 0
        
 

class Node():
    def toObjectStatic( v ):
        if isinstance(v,Node):
            return {
                'type': v.typeName,
                'value': Node.toObjectStatic(v.val),
                'flags': v.flags
            } 
        elif isinstance(v,(list,tuple)):
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
    if not node or not state: return ret
    
    type = node.type
    
    # walk the tree
    if T_ALTERNATION == type or T_SEQUENCE == type or T_CHARGROUP == type or T_GROUP == type or T_QUANTIFIER == type:
        r = state['map']( ret, node, state )
        if ('ret' in state) and (state['ret'] is not None):
            ret = state['reduce']( ret, node, state )
            state['ret'] = None
        
        elif r is not None:
            if not isinstance(r, (list,tuple)): r = [r]
            for ri in r:
                state['node'] = node
                ret = walk( ret, ri, state )
                if ('stop' in state) and state['stop']:
                    state['stop'] = None
                    return ret
    
    elif T_CHARS == type or T_CHARRANGE == type or T_UNICODECHAR == type or T_HEXCHAR == type or T_SPECIAL == type or T_STRING == type:
        ret = state['reduce']( ret, node, state )
    
    state['node'] = None
    return ret

def map_any( ret, node, state ):
    type = node.type
    if T_ALTERNATION == type or T_CHARGROUP == type:
        return node.val[rnd(0, len(node.val)-1)] if len(node.val) else None
    
    elif T_QUANTIFIER == type:
        if len(ret) >= state['maxLength']:
            numrepeats = 0 if ('MatchZeroOrMore' in node.flags) or ('MatchZeroOrOne' in node.flags) else (1 if ('MatchOneOrMore' in node.flags) else int(node.flags['MatchMinimum'], 10))
        
        else:
            if ('MatchZeroOrMore' in node.flags) and node.flags['MatchZeroOrMore']:
                numrepeats = rnd(0, 1+2*state['maxLength'])
            elif ('MatchZeroOrOne' in node.flags) and node.flags['MatchZeroOrOne']:
                numrepeats = rnd(0, 1)
            elif ('MatchOneOrMore' in node.flags) and node.flags['MatchOneOrMore']:
                numrepeats = rnd(1, 1+2*state['maxLength'])
            else:
                mmin = int(node.flags['MatchMinimum'], 10)
                mmax = (mmin+1+2*state['maxLength']) if 'unlimited'==node.flags['MatchMaximum'] else int(node.flags['MatchMaximum'], 10)
                numrepeats = rnd(mmin, mmax)
        return [node.val] * numrepeats if numrepeats else None
    
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
        if ('MatchMinimum' in node.flags):
            if "0"==node.flags['MatchMinimum']: return None
            return [node.val] * int(node.flags['MatchMinimum'],10)
        return node.val if ('MatchOneOrMore' in node.flags) and node.flags['MatchOneOrMore'] else None
    
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
            if ('MatchZeroOrMore' in node.flags) or ('MatchOneOrMore' in node.flags) or (('MatchMaximum' in node.flags) and ("unlimited" == node.flags['MatchMaximum'])):
                state['ret'] = -1
            elif 'MatchMaximum' in node.flags:
                state['ret'] = int(node.flags['MatchMaximum'],10)*max
            else:
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
            if (T_QUANTIFIER == n.type) and (('MatchZeroOrMore' in n.flags) or ('MatchZeroOrOne' in n.flags) or (('MatchMinimum' in n.flags) and "0" == n.flags['MatchMinimum'])):
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
    if T_SPECIAL == node.type and ('MatchEnd' not in node.flags):
        state['stop'] = 1
        return ret
        
    type = node.type;
    if T_CHARS == type or T_CHARRANGE == type or T_UNICODECHAR == type or T_HEXCHAR == type or (T_SPECIAL == type and ('MatchStart' not in node.flags) and ('MatchEnd' not in node.flags)):
        ret += 1
    
    elif T_STRING == type:
        ret += len(node.val)
    
    return ret

def reduce_str( ret, node, state ):
    if ('ret' in state) and state['ret'] is not None:
        ret += str(state['ret'])
        return ret
    if T_SPECIAL == node.type and ('MatchEnd' not in node.flags):
        state['stop'] = 1
        return ret
        
    type = node.type
    sample = None
    
    if T_CHARS == type:
        sample = node.val
    elif T_CHARRANGE == type:
        sample = character_range(node.val)
    elif T_UNICODECHAR == type or T_HEXCHAR == type:
        sample = [node.flags['Char']]
    elif T_SPECIAL == type and ('MatchStart' not in node.flags) and ('MatchEnd' not in node.flags):
        part = node.val
        if 'D' == part: sample = [digit( False )]
        elif 'W' == part: sample = [word( False )]
        elif 'S' == part: sample = [space( False )]
        elif 'd' == part: sample = [digit( )]
        elif 'w' == part: sample = [word( )]
        elif 's' == part: sample = [space( )]
        elif ('.' == part) and ('MatchAnyChar' in node.flags): sample = [any( )]
        else: sample = ['\\' + part]
    elif T_STRING == type:
        sample = node.val
    
    if sample is not None:
        ret += (case_insensitive(sample) if state['isCaseInsensitive'] else sample) if T_STRING == type else character(case_insensitive(sample, True) if state['isCaseInsensitive'] else sample, ('node' not in state) or ('NotMatch' not in state['node'].flags))
    
    return ret

def reduce_peek( ret, node, state ):
    if ('ret' in state) and state['ret'] is not None:
        ret['positive'] = concat( ret['positive'], state['ret']['positive'] )
        ret['negative'] = concat( ret['negative'], state['ret']['negative'] )
        return ret
    if T_SPECIAL == node.type and ('MatchEnd' not in node.flags):
        state['stop'] = 1
        return ret
        
    type = node.type
    inCharGroup = ('node' in state) and (T_CHARGROUP == state['node'].type)
    inNegativeCharGroup = inCharGroup and ('NotMatch' in state['node'].flags)
    peek = "negative" if inNegativeCharGroup else "positive"
    
    if T_CHARS == type:
        ret[peek] = concat( ret[peek], node.val )
    elif T_CHARRANGE == type:
        ret[peek] = concat( ret[peek], character_range(node.val) )
    elif T_UNICODECHAR == type or T_HEXCHAR == type:
        ret[peek][node.flags['Char']] = 1
    elif T_SPECIAL == type and ('MatchStart' not in node.flags) and ('MatchEnd' not in node.flags):
        part = node.val
        if 'D' == part:
            ret["positive" if inNegativeCharGroup else "negative"][ '\\d' ] = 1
        elif 'W' == part:
            ret["positive" if inNegativeCharGroup else "negative"][ '\\w' ] = 1
        elif 'S' == part:
            ret["positive" if inNegativeCharGroup else "negative"][ '\\s' ] = 1
        else:
            ret[peek]['\\' + part] = 1
    elif T_STRING == type:
        ret["positive"][node.val[0]] = 1
    
    return ret


def match_hex( s ):
    global _G
    m = False
    if len(s) > 2 and 'x' == s[0]:
    
        if match_char_ranges(_G.HEXDIGITS_RANGES, s, 1, 2, 2): 
            m=s[0:3]
            return [m, m[1:]]
    
    return False

def match_unicode( s ):
    global _G
    m = False
    if len(s) > 4 and 'u' == s[0]:
    
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
    if sl > 2 and '{' == s[pos]:
    
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
        if pos<sl and ',' == s[pos]:
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
        if pos<sl and '}' == s[pos]:
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
    chars = []
    flags = {}
    isRange = False
    escaped = False
    ch = ''
    
    if '^' == re_obj.re[re_obj.pos]:
    
        flags[ "NotMatch" ] = 1
        re_obj.pos+=1
    
    lre = re_obj.len
    while re_obj.pos < lre:
    
        isUnicode = False
        prevch = ch
        ch = re_obj.re[re_obj.pos]
        re_obj.pos+=1
        
        escaped = True if (_G.escapeChar == ch) else False
        if escaped:  
            ch = re_obj.re[re_obj.pos]
            re_obj.pos+=1
        
        if escaped:
        
            # unicode character
            if 'u' == ch:
            
                m = match_unicode( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                ch = chr(int(m[1], 16))
                isUnicode = True
            
            
            # hex character
            elif 'x' == ch:
            
                m = match_hex( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                ch = chr(int(m[1], 16))
                isUnicode = True
            
        
        
        if isRange:
        
            if len(chars):
            
                sequence.append( Node(T_CHARS, chars) )
                chars = []
            
            range[1] = ch
            isRange = False
            sequence.append( Node(T_CHARRANGE, range) )
        
        else:
        
            if escaped:
            
                if (not isUnicode) and (ch in _G.specialCharsEscaped) and ('/' != ch):
                
                    if len(chars):
                    
                        sequence.append( Node(T_CHARS, chars) )
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
                    
                        sequence.append( Node(T_CHARS, chars) )
                        chars = []
                    
                    return Node(T_CHARGROUP, sequence, flags)
                
                
                elif '-' == ch:
                
                    range = [prevch, '']
                    chars.pop()
                    isRange = True
                
                
                else:
                
                    chars.append( ch )
                
            
        
    
    if len(chars):
    
        sequence.append( Node(T_CHARS, chars) )
        chars = []
    
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
        
        if "?:" == pre:
        
            flags[ "NotCaptured" ] = 1
            re_obj.pos += 2
        
        
        elif "?=" == pre:
        
            flags[ "LookAhead" ] = 1
            re_obj.pos += 2
        
        
        elif "?!" == pre:
        
            flags[ "NegativeLookAhead" ] = 1
            re_obj.pos += 2
        
        
        re_obj.groupIndex+=1
        flags[ "GroupIndex" ] = re_obj.groupIndex
    
    lre = re_obj.len
    while re_obj.pos < lre:
    
        ch = re_obj.re[re_obj.pos]
        re_obj.pos+=1
        
        #   \\abc
        escaped = True if (_G.escapeChar == ch) else False
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
            
            
            else:
            
                word += ch
                wordlen += 1
            
        
        
        else:
        
            # group end
            if re_obj.inGroup > 0 and ')' == ch:
            
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
                flag = { 'val': m[0], "MatchMinimum": m[1], "MatchMaximum": m[2] if m[2] else "unlimited" }
                flag[ _G.specialChars[ch] ] = 1
                if re_obj.pos<lre and '?' == re_obj.re[re_obj.pos]:
                
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
            elif '*' == ch or '+' == ch or '?' == ch:
            
                if wordlen:
                
                    sequence.append( Node(T_STRING, word) )
                    word = ''
                    wordlen = 0
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                if re_obj.pos<lre and '?' == re_obj.re[re_obj.pos]:
                
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
    



class RegexAnalyzer:
    
    VERSION = "0.5.1"
    
    Node = Node
    
    # A simple (js-flavored) regular expression analyzer
    def __init__(self, re=None, delim=None):
        self.ast = None
        self.re = None
        self.fl = None
        self.min = None
        self.max = None
        self.ch = None
       
        if re is not None:   
            self.set(re, delim)
            
            
    def dispose( self ):
        self.ast = None
        self.re = None
        self.fl = None
        self.min = None
        self.max = None
        self.ch = None
        return self
    
    def reset(self):
        self.ast = None
        self.min = None
        self.max = None
        self.ch = None
        return self
    
    def set(self, re, delim=None):
        if re:
            
            if not delim: delim = '/'
            re = str(re)
            fl = {}
            l = len(re)
            
            # parse re flags, if any
            while 0 < l:
                ch = re[l-1]
                if delim == ch:
                    break
                else:
                    fl[ ch ] = 1
                    l -= 1
            
            if 0 < l:
                # remove re delimiters
                if delim == re[0] and delim == re[l-1]:  re = re[1:l-1]
                else: re = re[0:l]
            else:
                re = ''
            
            # re is different, reset the ast, etc
            if self.re != re: self.reset()
            self.re = re 
            self.fl = fl
        
        return self
        
    def analyze( self ):
        if self.re and (self.ast is None): self.ast = analyze_re( RE_OBJ(self.re) )
        return self
    
    def compile( self, flags=None ):
        if not self.re: return None
        flags = (self.fl if self.fl else {}) if not flags else flags
        return re.compile(self.re, re.I if 'i' in flags else None)
    
    def tree( self, flat=False ):
        if not self.re: return None
        if self.ast is None: self.analyze( )
        return self.ast.toObject() if flat is True else self.ast
    
    # experimental feature
    def sample( self, maxlen=1, numsamples=1 ):
        if not self.re: return None
        if self.ast is None: self.analyze( )
        state = {
            'map'               : map_any,
            'reduce'            : reduce_str,
            'maxLength'         : maxlen if maxlen else 1,
            'isCaseInsensitive' : ('i' in self.fl)
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
                'map'               : map_min,
                'reduce'            : reduce_len
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
                'map'               : map_max,
                'reduce'            : reduce_len
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
                'map'               : map_1st,
                'reduce'            : reduce_peek
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
                
                
                elif '\\' != c[0] and isCaseInsensitive:
                
                    cases[ c.lower() ] = 1
                    cases[ c.upper() ] = 1
                
                
                elif '\\' == c[0]:
                
                    del p[c]
                
            
            peek[n] = concat(p, cases)
        
        return peek
    
    
    
# if used with 'import *'
__all__ = ['RegexAnalyzer']
