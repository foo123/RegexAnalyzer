# -*- coding: UTF-8 -*-
##
#
#   RegexAnalyzer
#   @version: 0.4.4
#
#   A simple Regular Expression Analyzer for PHP, Python, Node/JS, ActionScript
#   https://github.com/foo123/RegexAnalyzer
#
##
import random, math, re

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
        chars = map( random_upper_or_lower, chars )
        return chars
    
    else:
        return random_upper_or_lower( chars )
    

def generate( part, isCaseInsensitive=False ):
    sample = ''

    type = part['type']
    # walk the sequence
    if T_ALTERNATION == type:
    
        sample += generate( part['part'][rnd(0, len(part['part'])-1)], isCaseInsensitive )
    

    elif T_GROUP == type:
    
        sample += generate( part['part'], isCaseInsensitive )
    

    elif T_SEQUENCE == type:
    
        for p in part['part']:
        
            if not p: continue
            repeat = 1
            if T_QUANTIFIER == p['type']:
            
                if 'MatchZeroOrMore' in p['flags']: repeat = rnd(0, 10)
                elif 'MatchZeroOrOne' in p['flags']: repeat = rnd(0, 1)
                elif 'MatchOneOrMore' in p['flags']: repeat = rnd(1, 11)
                else: 
                
                    mmin = int(p['flags']['MatchMinimum'], 10)
                    mmax = int(p['flags']['MatchMaximum'], 10)
                    repeat = rnd(mmin, (mmin+10) if is_nan(mmax) else mmax)
                
                while repeat > 0:
                
                    repeat-=1
                    sample += generate( p['part'], isCaseInsensitive )
                
            
            elif T_SPECIAL == p['type']:
            
                if 'MatchAnyChar' in p['flags']: sample += any( )
            
            else:
            
                sample += generate( p, isCaseInsensitive )
            
        
    

    elif T_CHARGROUP == type:
    
        chars = []
        #l = len(part['part']);
        for p in part['part']:
        
            ptype = p['type']
            if T_CHARS == ptype:
            
                if isCaseInsensitive: chars = chars + list(case_insensitive( list(p['part']), True ))
                else: chars = chars + list(p['part'])
            
            
            elif T_CHARRANGE == ptype:
            
                if isCaseInsensitive: chars = chars + list(case_insensitive( character_range(list(p['part'])), True ))
                else: chars = chars + list(character_range(list(p['part'])))
            
            
            elif T_UNICODECHAR == ptype or T_HEXCHAR == ptype:
            
                chars.append( case_insensitive( p['flags']['Char'] ) if isCaseInsensitive else p['flags']['Char'] )
            
            
            elif T_SPECIAL == ptype:
            
                p_part = p['part']
                if 'D' == p_part:
                
                    chars.append( digit( False ) )
                
                elif 'W' == p_part:
                
                    chars.append( word( False ) )
                
                elif 'S' == p_part:
                
                    chars.appemd( space( False ) )
                
                elif 'd' == p_part:
                
                    chars.append( digit( ) )
                
                elif 'w' == p_part:
                
                    chars.append( word( ) )
                
                elif 's' == p_part:
                
                    chars.append( space( ) )
                
                else:
                
                    chars.append( '\\' + p_part )
                
            
        
        sample += character(chars, not ('NotMatch' in part['flags']))
    

    elif T_STRING == type:
    
        sample += case_insensitive( part['part'] ) if isCaseInsensitive else part['part']
    

    elif T_SPECIAL == type and not('MatchStart' in part['flags']) and not('MatchEnd' in part['flags']):
    
        p_part = part.part
        if 'D' == p_part:
        
            sample += digit( False )
        
        elif 'W' == p_part:
        
            sample += word( False )
        
        elif 'S' == p_part:
        
            sample += space( False )
        
        elif 'd' == p_part:
        
            sample += digit( )
        
        elif 'w' == p_part:
        
            sample += word( )
        
        elif 's' == p_part:
        
            sample += space( )
        
        elif '.' == p_part:
        
            sample += any( )
        
        else:
        
            sample += '\\' + p_part
        
    
            
    elif T_UNICODECHAR == type or T_HEXCHAR == type:
    
        sample +=  case_insensitive( part['flags']['Char'] ) if isCaseInsensitive else part['flags']['Char']
    

    return sample


def peek_characters( part ):
    peek = {}
    negativepeek = {}
    
    if not part: return { 'peek': peek, 'negativepeek': negativepeek }
    
    type = part['type']
    # walk the sequence
    if T_ALTERNATION == type:
        for p in part['part']:
            tmp = peek_characters( p )
            peek = concat( peek, tmp['peek'] )
            negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif T_GROUP == type:
        tmp = peek_characters( part['part'] )
        peek = concat( peek, tmp['peek'] )
        negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif T_SEQUENCE == type:
        i = 0
        l = len(part['part'])
        p = part['part'][i]
        done = ( 
            i >= l or not(p) or T_QUANTIFIER != p['type'] or 
            ((('MatchZeroOrMore' not in p['flags']) and ('MatchZeroOrOne' not in p['flags']) and ('MatchMinimum' not in p['flags'])) or "0" != p['flags']['MatchMinimum'])
        )
        while not done:
            tmp = peek_characters( p['part'] )
            peek = concat( peek, tmp['peek'] )
            negativepeek = concat( negativepeek, tmp['negativepeek'] )
            
            i += 1
            p = part['part'][i]
            
            done = ( 
                i >= l or not(p) or T_QUANTIFIER != p['type'] or 
                ((('MatchZeroOrMore' not in p['flags']) and ('MatchZeroOrOne' not in p['flags']) and ('MatchMinimum' not in p['flags'])) or "0" != p['flags']['MatchMinimum'])
            )
        
        if i < l:
            p = part['part'][i]
            
            if T_SPECIAL == p['type'] and ('^'==p['part'] or '$'==p['part']):
                p = part['part'][i+1] if (i+1 < l) else None
            
            if p and T_QUANTIFIER == p['type']:
                p = p['part']
            
            if p:
                tmp = peek_characters( p )
                peek = concat( peek, tmp['peek'] )
                negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif T_CHARGROUP == type:
        if 'NotMatch' in part['flags']:
            current = negativepeek
        else:
            current = peek
        
        for p in part['part']:
            ptype = p['type']
            if T_CHARS == ptype:
                current = concat( current, p['part'] )
            
            elif T_CHARRANGE == ptype:
                current = concat( current, character_range(p['part']) )
            
            elif T_UNICODECHAR == ptype or T_HEXCHAR == ptype:
                current[p['flags']['Char']] = 1
            
            elif T_SPECIAL == ptype:
                if 'D' == p['part']:
                    if 'NotMatch' in part['flags']:
                        peek[ '\\d' ] = 1
                    else:
                        negativepeek[ '\\d' ] = 1
                elif 'W' == p['part']:
                    if 'NotMatch' in part['flags']:
                        peek[ '\\w' ] = 1
                    else:
                        negativepeek[ '\\W' ] = 1
                elif 'S' == p['part']:
                    if 'NotMatch' in part['flags']:
                        peek[ '\\s' ] = 1
                    else:
                        negativepeek[ '\\s' ] = 1
                else:
                    current['\\' + p['part']] = 1
    
    elif T_STRING == type:
        peek[part['part'][0]] = 1
    
    elif T_SPECIAL == type and ('MatchStart' not in part['flags']) and ('MatchEnd' not in part['flags']['MatchEnd']):
        if 'D' == part['part']:
            negativepeek[ '\\d' ] = 1
        elif 'W' == part['part']:
            negativepeek[ '\\W' ] = 1
        elif 'S' == part['part']:
            negativepeek[ '\\s' ] = 1
        else:
            peek['\\' + part['part']] = 1
            
    elif T_UNICODECHAR == type or T_HEXCHAR == type:
        peek[part['flags']['Char']] = 1
    
    return {'peek': peek, 'negativepeek': negativepeek}

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
        if pos<sl and ',' == s[pos]: pos += 1
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
            return m
        else:
            return False
    
    return False


class RE_OBJ():
    def __init__(self, regex):
        self.re = regex
        self.len = len(regex)
        self.pos = 0
        self.groupIndex = 0
        self.inGroup = 0
        
 

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
            
                sequence.append( { 'part': chars, 'flags': {}, 'typeName': "Chars", 'type': T_CHARS } )
                chars = []
            
            range[1] = ch
            isRange = False
            sequence.append( { 'part': range, 'flags': {}, 'typeName': "CharRange", 'type': T_CHARRANGE } )
        
        else:
        
            if escaped:
            
                if (not isUnicode) and (ch in _G.specialCharsEscaped) and ('/' != ch):
                
                    if len(chars):
                    
                        sequence.append( { 'part': chars, 'flags': {}, 'typeName': "Chars", 'type': T_CHARS } )
                        chars = []
            
                    flag = {}
                    flag[ _G.specialCharsEscaped[ch] ] = 1
                    sequence.append( { 'part': ch, 'flags': flag, 'typeName': "Special", 'type': T_SPECIAL} )
                
                
                else:
                
                    chars.append( ch )
                
            
            
            else:
            
                # end of char group
                if ']' == ch:
                
                    if len(chars):
                    
                        sequence.append( { 'part': chars, 'flags': {}, 'typeName': "Chars", 'type': T_CHARS } )
                        chars = []
                    
                    return { 'part': sequence, 'flags': flags, 'typeName': "CharGroup", 'type': T_CHARGROUP }
                
                
                elif '-' == ch:
                
                    range = [prevch, '']
                    chars.pop()
                    isRange = True
                
                
                else:
                
                    chars.append( ch )
                
            
        
    
    if len(chars):
    
        sequence.append( { 'part': chars, 'flags': {}, 'typeName': "Chars", 'type': T_CHARS } )
        chars = []
    
    return { 'part': sequence, 'flags': flags, 'typeName': "CharGroup", 'type': T_CHARGROUP }


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
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                m = match_unicode( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                sequence.append( { 'part': m[0], 'flags': { "Char": chr(int(m[1], 16)), "Code": m[1] }, 'typeName': "UnicodeChar", 'type': T_UNICODECHAR } )
            
            
            # hex character
            elif 'x' == ch:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                m = match_hex( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                sequence.append( { 'part': m[0], 'flags': { "Char": chr(int(m[1], 16)), "Code": m[1] }, 'typeName': "HexChar", 'type': T_HEXCHAR } )
            
            
            elif (ch in _G.specialCharsEscaped) and ('/' != ch):
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                flag = {}
                flag[ _G.specialCharsEscaped[ch] ] = 1
                sequence.append( { 'part': ch, 'flags': flag, 'typeName': "Special", 'type': T_SPECIAL } )
            
            
            else:
            
                word += ch
                wordlen += 1
            
        
        
        else:
        
            # group end
            if re_obj.inGroup > 0 and ')' == ch:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                if len(alternation):
                
                    alternation.append( { 'part': sequence, 'flags': {}, 'typeName': "Sequence", 'type': T_SEQUENCE } )
                    sequence = []
                    flag = {}
                    flag[ _G.specialChars['|'] ] = 1
                    return { 'part': { 'part': alternation, 'flags': flag, 'typeName': "Alternation", 'type': T_ALTERNATION }, 'flags': flags, 'typeName': "Group", 'type': T_GROUP }
                
                else:
                
                    return { 'part': { 'part': sequence, 'flags': {}, 'typeName': "Sequence", 'type': T_SEQUENCE }, 'flags': flags, 'typeName': "Group", 'type': T_GROUP }
                
            
            
            # parse alternation
            elif '|' == ch:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                alternation.append( { 'part': sequence, 'flags': {}, 'typeName': "Sequence", 'type': T_SEQUENCE } )
                sequence = []
            
            
            # parse character group
            elif '[' == ch:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                sequence.append( chargroup( re_obj ) )
            
            
            # parse sub-group
            elif '(' == ch:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                re_obj.inGroup+=1
                sequence.append( analyze_re( re_obj ) )
                re_obj.inGroup-=1
            
            
            # parse num repeats
            elif '{' == ch:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                m = match_repeats( re_obj.re[re_obj.pos-1:] )
                re_obj.pos += len(m[0])-1
                flag = { 'part': m[0], "MatchMinimum": m[1], "MatchMaximum": m[2] if m[2] else "unlimited" }
                flag[ _G.specialChars[ch] ] = 1
                if re_obj.pos<lre and '?' == re_obj.re[re_obj.pos]:
                
                    flag[ "isGreedy" ] = 0
                    re_obj.pos+=1
                
                else:
                
                    flag[ "isGreedy" ] = 1
                
                prev = sequence.pop()
                if T_STRING == prev['type'] and len(prev['part']) > 1:
                
                    sequence.append( { 'part': prev['part'][0:-1], 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    prev['part'] = prev['part'][-1]
                
                sequence.append( { 'part': prev, 'flags': flag, 'typeName': "Quantifier", 'type': T_QUANTIFIER } )
            
            
            # quantifiers
            elif '*' == ch or '+' == ch or '?' == ch:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
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
                if T_STRING == prev['type'] and len(prev['part']) > 1:
                
                    sequence.append( { 'part': prev['part'][0:-1], 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    prev['part'] = prev['part'][-1]
                
                sequence.append( { 'part': prev, 'flags': flag, 'typeName': "Quantifier", 'type': T_QUANTIFIER } )
            
        
            # special characters like ^, $, ., etc..
            elif ch in _G.specialChars:
            
                if wordlen:
                
                    sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
                    word = ''
                    wordlen = 0
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                sequence.append( { 'part': ch, 'flags': flag, 'typeName': "Special", 'type': T_SPECIAL } )
            
        
            else:
            
                word += ch
                wordlen += 1
            
        
    
    
    if wordlen:
    
        sequence.append( { 'part': word, 'flags': {}, 'typeName': "String", 'type': T_STRING } )
        word = ''
        wordlen = 0
                
    
    if len(alternation):
    
        alternation.append( { 'part': sequence, 'flags': {}, 'typeName': "Sequence", 'type': T_SEQUENCE } )
        sequence = []
        flag = {}
        flag[ _G.specialChars['|'] ] = 1
        return { 'part': alternation, 'flags': flag, 'typeName': "Alternation", 'type': T_ALTERNATION }
    
    return { 'part': sequence, 'flags': {}, 'typeName': "Sequence", 'type': T_SEQUENCE }
    



class RegexAnalyzer:
    
    VERSION = "0.4.4"
    
    # A simple (js-flavored) regular expression analyzer
    def __init__(self, regex=None, delim=None):
        self._regex = None
        self._flags = None
        self._parts = None
        self._needsRefresh = False
       
        if regex is not None:   
            self.regex(regex, delim)
            
            
    def dispose( self ):
        self._regex = None
        self._flags = None
        self._parts = None
        return self
    
    def regex(self, regex, delim=None):
        if regex:
            flags = {}
            
            if not delim: delim = '/'
            
            r = str(regex)
            l = len(r)
            ch = r[l-1]
            
            # parse regex flags
            while delim != ch:
            
                flags[ ch ] = 1
                r = r[0:-1]
                l -= 1
                ch = r[-1]
            
            # remove regex delimiters
            if delim == r[0] and delim == r[-1]:  r = r[1:-1]
            
            if self._regex != r: self._needsRefresh = True
            self._regex = r 
            self._flags = flags
        
        return self
        
    def getRegex( self ):
        return re.compile(self._regex, re.I if 'i' in self._flags else None)
    
    def getParts( self ):
        if self._needsRefresh: self.analyze( )
        return self._parts
    
    def analyze( self ):
        if self._needsRefresh:
            self._parts = analyze_re( RE_OBJ(self._regex) )
            self._needsRefresh = False
        
        return self
    
    # experimental feature
    def sample( self ):
        if self._needsRefresh: self.analyze( )
        return generate( self._parts, 'i' in self._flags )
    
    # experimental feature, implement (optimised) RE matching as well
    def match( str ):
        #return match( self.$parts, str, 0, self.$flags && self.$flags.i );
        return False
    
    # experimental feature
    def peek( self ):
        if self._needsRefresh: self.analyze( )
        isCaseInsensitive = 'i' in self._flags
        peek = peek_characters( self._parts )
        
        for n,p in peek.items():
        
            cases = {}
            
            # either peek or negativepeek
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
