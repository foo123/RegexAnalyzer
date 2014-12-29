# -*- coding: UTF-8 -*-
##
#
#   RegExAnalyzer
#   @version: 0.4.3
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
    if "Alternation" == type:
    
        sample += generate( part['part'][rnd(0, len(part['part'])-1)], isCaseInsensitive )
    

    elif "Group" == type:
    
        sample += generate( part['part'], isCaseInsensitive )
    

    elif "Sequence" == type:
    
        for p in part['part']:
        
            if not p: continue
            repeat = 1
            if "Quantifier" == p['type']:
            
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
                
            
            elif "Special" == p['type']:
            
                if 'MatchAnyChar' in p['flags']: sample += any( )
            
            else:
            
                sample += generate( p, isCaseInsensitive )
            
        
    

    elif "CharGroup" == type:
    
        chars = []
        #l = len(part['part']);
        for p in part['part']:
        
            ptype = p['type']
            if "Chars" == ptype:
            
                if isCaseInsensitive: chars = chars + list(case_insensitive( list(p['part']), True ))
                else: chars = chars + list(p['part'])
            
            
            elif "CharRange" == ptype:
            
                if isCaseInsensitive: chars = chars + list(case_insensitive( character_range(list(p['part'])), True ))
                else: chars = chars + list(character_range(list(p['part'])))
            
            
            elif "UnicodeChar" == ptype or "HexChar" == ptype:
            
                chars.append( case_insensitive( p['flags']['Char'] ) if isCaseInsensitive else p['flags']['Char'] )
            
            
            elif "Special" == ptype:
            
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
    

    elif "String" == type:
    
        sample += case_insensitive( part['part'] ) if isCaseInsensitive else part['part']
    

    elif "Special" == type and not('MatchStart' in part['flags']) and not('MatchEnd' in part['flags']):
    
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
        
    
            
    elif "UnicodeChar" == type or "HexChar" == type:
    
        sample +=  case_insensitive( part['flags']['Char'] ) if isCaseInsensitive else part['flags']['Char']
    

    return sample


def peek_characters( part ):
    peek = {}
    negativepeek = {}
    
    if not part: return { 'peek': peek, 'negativepeek': negativepeek }
    
    type = part['type']
    # walk the sequence
    if "Alternation" == type:
        for p in part['part']:
            tmp = peek_characters( p )
            peek = concat( peek, tmp['peek'] )
            negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif "Group" == type:
        tmp = peek_characters( part['part'] )
        peek = concat( peek, tmp['peek'] )
        negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif "Sequence" == type:
        i = 0
        l = len(part['part'])
        p = part['part'][i]
        done = ( 
            i >= l or not(p) or "Quantifier" != p['type'] or 
            ((('MatchZeroOrMore' not in p['flags']) and ('MatchZeroOrOne' not in p['flags']) and ('MatchMinimum' not in p['flags'])) or "0" != p['flags']['MatchMinimum'])
        )
        while not done:
            tmp = peek_characters( p['part'] )
            peek = concat( peek, tmp['peek'] )
            negativepeek = concat( negativepeek, tmp['negativepeek'] )
            
            i += 1
            p = part['part'][i]
            
            done = ( 
                i >= l or not(p) or "Quantifier" != p['type'] or 
                ((('MatchZeroOrMore' not in p['flags']) and ('MatchZeroOrOne' not in p['flags']) and ('MatchMinimum' not in p['flags'])) or "0" != p['flags']['MatchMinimum'])
            )
        
        if i < l:
            p = part['part'][i]
            
            if "Special" == p['type'] and ('^'==p['part'] or '$'==p['part']):
                p = part['part'][i+1] if (i+1 < l) else None
            
            if p and "Quantifier" == p['type']:
                p = p['part']
            
            if p:
                tmp = peek_characters( p )
                peek = concat( peek, tmp['peek'] )
                negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif "CharGroup" == type:
        if 'NotMatch' in part['flags']:
            current = negativepeek
        else:
            current = peek
        
        for p in part['part']:
            ptype = p['type']
            if "Chars" == ptype:
                current = concat( current, p['part'] )
            
            elif "CharRange" == ptype:
                current = concat( current, character_range(p['part']) )
            
            elif "UnicodeChar" == ptype or "HexChar" == ptype:
                current[p['flags']['Char']] = 1
            
            elif "Special" == ptype:
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
    
    elif "String" == type:
        peek[part['part'][0]] = 1
    
    elif "Special" == type and ('MatchStart' not in part['flags']) and ('MatchEnd' not in part['flags']['MatchEnd']):
        if 'D' == part['part']:
            negativepeek[ '\\d' ] = 1
        elif 'W' == part['part']:
            negativepeek[ '\\W' ] = 1
        elif 'S' == part['part']:
            negativepeek[ '\\s' ] = 1
        else:
            peek['\\' + part['part']] = 1
            
    elif "UnicodeChar" == type or "HexChar" == type:
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
        self.regex = regex
        self.pos = 0
        self.groupIndex = 0
        
 
def subgroup( obj ):
    global _G
    word = ''
    alternation = []
    sequence = []
    flags = {}
    escaped = False
    ch = ''
    pre = obj.regex[obj.pos:obj.pos+2]
    
    if "?:" == pre:
    
        flags[ "NotCaptured" ] = 1
        obj.pos += 2
    
    
    elif "?=" == pre:
    
        flags[ "LookAhead" ] = 1
        obj.pos += 2
    
    
    elif "?!" == pre:
    
        flags[ "NegativeLookAhead" ] = 1
        obj.pos += 2
    
    
    obj.groupIndex+=1
    flags[ "GroupIndex" ] = obj.groupIndex
    
    lre = len(obj.regex)
    while obj.pos < lre:
    
        ch = obj.regex[obj.pos]
        obj.pos+=1
        escaped = True if (_G.escapeChar == ch) else False
        if escaped:  
            ch = obj.regex[obj.pos]
            obj.pos+=1
        
        if escaped:
        
            # unicode character
            if 'u' == ch:
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                match = match_unicode( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                sequence.append( { 'part': match[0], 'flags': { "Char": chr(int(match[1], 16)), "Code": match[1] }, 'type': "UnicodeChar" } )
            
            
            # hex character
            elif 'x' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                match = match_hex( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                sequence.append( { 'part': match[0], 'flags': { "Char": chr(int(match[1], 16)), "Code": match[1] }, 'type': "HexChar" } )
            
            
            elif ch in _G.specialCharsEscaped and '/' != ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                flag = {}
                flag[ _G.specialCharsEscaped[ch] ] = 1
                sequence.append( { 'part': ch, 'flags': flag, 'type': "Special" } )
            
            
            else:
            
                word += ch
            
        
        
        else:
        
            # group end
            if ')' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                if len(alternation):
                
                    alternation.append( { 'part': sequence, 'flags': {}, 'type': "Sequence" } )
                    sequence = []
                    flag = {}
                    flag[ _G.specialChars['|'] ] = 1
                    return { 'part': { 'part': alternation, 'flags': flag, 'type': "Alternation" }, 'flags': flags, 'type': "Group" }
                
                else:
                
                    return { 'part': { 'part': sequence, 'flags': {}, 'type': "Sequence" }, 'flags': flags, 'type': "Group" }
                
            
            
            # parse alternation
            elif '|' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                alternation.append( { 'part': sequence, 'flags': {}, 'type': "Sequence" } )
                sequence = []
            
            
            # parse character group
            elif '[' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                sequence.append( chargroup( obj ) )
            
            
            # parse sub-group
            elif '(' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                sequence.append( subgroup( obj ) )
            
            
            # parse num repeats
            elif '{' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                match = match_repeats( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                flag = { 'part': match[0], "MatchMinimum": match[1], "MatchMaximum": match[2] if match[2] else "unlimited" }
                flag[ _G.specialChars[ch] ] = 1
                if obj.pos<lre and '?' == obj.regex[obj.pos]:
                
                    flag[ "isGreedy" ] = 0
                    obj.pos+=1
                
                else:
                
                    flag[ "isGreedy" ] = 1
                
                prev = sequence.pop()
                if "String" == prev['type'] and len(prev['part']) > 1:
                
                    sequence.append( { 'part': prev['part'][0:-1], 'flags': {}, 'type': "String" } )
                    prev['part'] = prev['part'][-1]
                
                sequence.append( { 'part': prev, 'flags': flag, 'type': "Quantifier" } )
            
            
            # quantifiers
            elif '*' == ch or '+' == ch or '?' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                if obj.pos<lre and '?' == obj.regex[obj.pos]:
                
                    flag[ "isGreedy" ] = 0
                    obj.pos+=1
                
                else:
                
                    flag[ "isGreedy" ] = 1
                
                prev = sequence.pop()
                if "String" == prev['type'] and len(prev['part']) > 1:
                
                    sequence.append( { 'part': prev['part'][0:-1], 'flags': {}, 'type': "String" } )
                    prev['part'] = prev['part'][-1]
                
                sequence.append( { 'part': prev, 'flags': flag, 'type': "Quantifier" } )
            
        
            # special characters like ^, $, ., etc..
            elif ch in _G.specialChars:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                sequence.append( { 'part': ch, 'flags': flag, 'type': "Special" } )
            
        
            else:
            
                word += ch
            
        
    
    if len(word):
    
        sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
        word = ''
    
    if len(alternation):
    
        alternation.append( { 'part': sequence, 'flags': {}, 'type': "Sequence" } )
        sequence = []
        flag = {}
        flag[ _G.specialChars['|'] ] = 1
        return { 'part': { 'part': alternation, 'flags': flag, 'type': "Alternation" }, 'flags': flags, 'type': "Group" }
    
    else:
    
        return { 'part': { 'part': sequence, 'flags': {}, 'type': "Sequence" }, 'flags': flags, 'type': "Group" }
    


def chargroup( obj ):
    global _G
    sequence = []
    chars = []
    flags = {}
    isRange = False
    escaped = False
    ch = ''
    
    if '^' == obj.regex[obj.pos]:
    
        flags[ "NotMatch" ] = 1
        obj.pos+=1
    
    lre = len(obj.regex)
    while obj.pos < lre:
    
        isUnicode = False
        prevch = ch
        ch = obj.regex[obj.pos]
        obj.pos+=1
        
        escaped = True if (_G.escapeChar == ch) else False
        if escaped:  
            ch = obj.regex[obj.pos]
            obj.pos+=1
        
        if escaped:
        
            # unicode character
            if 'u' == ch:
            
                match = match_unicode( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                ch = chr(int(match[1], 16))
                isUnicode = True
            
            
            # hex character
            elif 'x' == ch:
            
                match = match_hex( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                ch = chr(int(match[1], 16))
                isUnicode = True
            
        
        
        if isRange:
        
            if len(chars):
            
                sequence.append( { 'part': chars, 'flags': {}, 'type': "Chars" } )
                chars = []
            
            range[1] = ch
            isRange = False
            sequence.append( { 'part': range, 'flags': {}, 'type': "CharRange" } )
        
        else:
        
            if escaped:
            
                if (not isUnicode) and (ch in _G.specialCharsEscaped) and ('/' != ch):
                
                    if len(chars):
                    
                        sequence.append( { 'part': chars, 'flags': {}, 'type': "Chars" } )
                        chars = []
                    
                    flag = {}
                    flag[ _G.specialCharsEscaped[ch] ] = 1
                    sequence.append( { 'part': ch, 'flags': flag, 'type': "Special" } )
                
                
                else:
                
                    chars.append( ch )
                
            
            
            else:
            
                # end of char group
                if ']' == ch:
                
                    if len(chars):
                    
                        sequence.append( { 'part': chars, 'flags': {}, 'type': "Chars" } )
                        chars = []
                    
                    return { 'part': sequence, 'flags': flags, 'type': "CharGroup" }
                
                
                elif '-' == ch:
                
                    range = [prevch, '']
                    chars.pop()
                    isRange = True
                
                
                else:
                
                    chars.append( ch )
                
            
        
    
    if len(chars):
    
        sequence.append( { 'part': chars, 'flags': {}, 'type': "Chars" } )
        chars = []
    
    return { 'part': sequence, 'flags': flags, 'type': "CharGroup" }


def analyze_re( regex ):
    global _G
    obj = RE_OBJ(regex)
    word = ''
    alternation = []
    sequence = []
    escaped = False
    ch = ''
    
    lre = len(obj.regex)
    while obj.pos < lre:
    
        ch = obj.regex[obj.pos]
        obj.pos+=1
        
        #   \\abc
        escaped = True if (_G.escapeChar == ch) else False
        if escaped:  
            ch = obj.regex[obj.pos]
            obj.pos+=1
        
        if escaped:
        
            # unicode character
            if 'u' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                match = match_unicode( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                sequence.append( { 'part': match[0], 'flags': { "Char": chr(int(match[1], 16)), "Code": match[1] }, 'type': "UnicodeChar" } )
            
            
            # hex character
            elif 'x' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                match = match_hex( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                sequence.append( { 'part': match[0], 'flags': { "Char": chr(int(match[1], 16)), "Code": match[1] }, 'type': "HexChar" } )
            
            
            elif (ch in _G.specialCharsEscaped) and ('/' != ch):
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, type: "String" } )
                    word = ''
                
                flag = {}
                flag[ _G.specialCharsEscaped[ch] ] = 1
                sequence.append( { 'part': ch, 'flags': flag, 'type': "Special" } )
            
            
            else:
            
                word += ch
            
        
        
        else:
        
            # parse alternation
            if '|' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                alternation.append( { 'part': sequence, 'flags': {}, 'type': "Sequence" } )
                sequence = []
            
            
            # parse character group
            elif '[' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                sequence.append( chargroup( obj ) )
            
            
            # parse sub-group
            elif '(' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                sequence.append( subgroup( obj ) )
            
            
            # parse num repeats
            elif '{' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                match = match_repeats( obj.regex[obj.pos-1:] )
                obj.pos += len(match[0])-1
                flag = { 'part': match[0], "MatchMinimum": match[1], "MatchMaximum": match[2] if match[2] else "unlimited" }
                flag[ _G.specialChars[ch] ] = 1
                if obj.pos<lre and '?' == obj.regex[obj.pos]:
                
                    flag[ "isGreedy" ] = 0
                    obj.pos+=1
                
                else:
                
                    flag[ "isGreedy" ] = 1
                
                prev = sequence.pop()
                if "String" == prev['type'] and len(prev['part']) > 1:
                
                    sequence.append( { 'part': prev['part'][0:-1], 'flags': {}, 'type': "String" } )
                    prev['part'] = prev['part'][-1]
                
                sequence.append( { 'part': prev, 'flags': flag, 'type': "Quantifier" } )
            
            
            # quantifiers
            elif '*' == ch or '+' == ch or '?' == ch:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                if obj.pos<lre and '?' == obj.regex[obj.pos]:
                
                    flag[ "isGreedy" ] = 0
                    obj.pos+=1
                
                else:
                
                    flag[ "isGreedy" ] = 1
                
                prev = sequence.pop()
                if "String" == prev['type'] and len(prev['part']) > 1:
                
                    sequence.append( { 'part': prev['part'][0:-1], 'flags': {}, 'type': "String" } )
                    prev['part'] = prev['part'][-1]
                
                sequence.append( { 'part': prev, 'flags': flag, 'type': "Quantifier" } )
            
        
            # special characters like ^, $, ., etc..
            elif ch in _G.specialChars:
            
                if len(word):
                
                    sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
                    word = ''
                
                flag = {}
                flag[ _G.specialChars[ch] ] = 1
                sequence.append( { 'part': ch, 'flags': flag, 'type': "Special" } )
            
        
            else:
            
                word += ch
            
        
    
    
    if len(word):
    
        sequence.append( { 'part': word, 'flags': {}, 'type': "String" } )
        word = ''
    
    
    if len(alternation):
    
        alternation.append( { 'part': sequence, 'flags': {}, 'type': "Sequence" } )
        sequence = []
        flag = {}
        flag[ _G.specialChars['|'] ] = 1
        return { 'part': alternation, 'flags': flag, 'type': "Alternation" }
    
    else:
    
        return { 'part': sequence, 'flags': {}, 'type': "Sequence" }
    



class RegExAnalyzer:
    
    VERSION = "0.4.3"
    
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
    
    def regex(self, regex=None, delim=None):
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
        
    def analyze( self ):
        if self._needsRefresh:
            self._parts = analyze_re( self._regex )
            self._needsRefresh = False
        
        return self
    
    def getRegex( self ):
        return re.compile(self._regex, re.I if 'i' in self._flags else None)
    
    def getParts( self ):
        if self._needsRefresh: self.analyze( )
        return self._parts
    
    # experimental feature
    def generateSample( self ):
        if self._needsRefresh: self.analyze( )
        return generate( self._parts, 'i' in self._flags )
    
    # experimental feature, implement (optimised) RE matching as well
    def match( str ):
        #return match( self.$parts, str, 0, self.$flags && self.$flags.i );
        return False
    
    # experimental feature
    def getPeekChars( self ):
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
__all__ = ['RegExAnalyzer']
