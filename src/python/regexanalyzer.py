# -*- coding: UTF-8 -*-
##
#
#   RegExAnalyzer
#   @version: 0.1
#
#   A simple Regular Expression Analyzer in Python
#   https://github.com/foo123/RegexAnalyzer
#
##
# needed imports
import re

def concat( p1, p2=None ):
    if p2 and isinstance(p2, (list, tuple)):
        l = len(p2)
        for p in range(l): p1[ p2[ p ] ] = 1
        
    
    else:
        for p in p2:  p1[ p ] = 1;
        
    return p1


# http://stackoverflow.com/questions/12376870/create-an-array-of-characters-from-specified-range
def getCharRange( first=None, last=None ):
    if first and isinstance(first, (list, tuple)):
        last = first[1]
        first = first[0]
    
    start = first[0] 
    end = last[0]
    
    if end == start: return [ chr( start ) ]
    
    chars = []
    for ch = start; ch <= end; ch+=1:
        chars.append(chr( ch ))
    
    return chars


def getPeekChars( part=None ):
    peek = {}
    negativepeek = {}
    
    if not part: return { 'peek': peek, 'negativepeek': negativepeek }
    
    type = part['type']
    # walk the sequence
    if "Alternation" == type:
        for p in part['part']:
            tmp = getPeekChars( p )
            peek = concat( peek, tmp['peek'] )
            negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif "Group" == type:
        tmp = getPeekChars( part['part'] )
        peek = concat( peek, tmp['peek'] )
        negativepeek = concat( negativepeek, tmp['negativepeek'] )
    
    elif "Sequence" == type:
        i = 0
        l = len(part['part'])
        p = part['part'][i]
        done = ( 
            i >= l or !p or "Quantifier" != p['type'] or 
            ((('MatchZeroOrMore' not in p['flags']) and ('MatchZeroOrOne' not in p['flags']) and ('MatchMinimum' not in p['flags'])) or "0" != p['flags']['MatchMinimum'])
        )
        while not done:
            tmp = getPeekChars( p['part'] )
            peek = concat( peek, tmp['peek'] )
            negativepeek = concat( negativepeek, tmp['negativepeek'] )
            
            i += 1
            p = part['part'][i]
            
            done = ( 
                i >= l or !p or "Quantifier" != p['type'] or 
                ((('MatchZeroOrMore' not in p['flags']) and ('MatchZeroOrOne' not in p['flags']) and ('MatchMinimum' not in p['flags'])) or "0" != p['flags']['MatchMinimum'])
            )
        
        if i < l:
            p = part['part'][i]
            
            if "Special" == p['type'] and ('^'==p['part'] or '$'==p['part']):
                p = part['part'][i+1] if (i+1 < l) else None
            
            if p and "Quantifier" == p['type']:
                p = p['part']
            
            if p:
                tmp = getPeekChars( p )
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
                current = concat( current, getCharRange(p['part']) )
            
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


class RegExAnalyzer:
    
    VERSION = "0.1"
    
    # A simple (js-flavored) regular expression analyzer
    def __init__(self, regex=None, delim=None):
        self.escapeChar = '\\'
        
        self.repeatsRegex = re.compile(r'^\{\s*(\d+)\s*,?\s*(\d+)?\s*\}')
        
        self.unicodeRegex = re.compile(r'^u([0-9a-fA-F]{4})')
        
        self.hexRegex = re.compile(r'^x([0-9a-fA-F]{2})')
        
        self.specialChars = {
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
        
        self.specialCharsEscaped = {
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
        
        self.regex = None
        self.flags = None
        self.parts = None
        
        self.groupIndex = None
        self.pos = None
        
        if regex is not None:   
            self.setRegex(regex, delim)
            
            
    
    # experimental feature
    def getPeekChars(self):
        
        isCaseInsensitive = self.flags and 'i' in self.flags
        peek = getPeekChars(self.parts)
        
        for n,p in peek.items():
        
            cases = {}
            
            # either peek or negativepeek
            for c,dummy in p.items():
            
                if '\\d' == c:
                
                    del p[c]
                    cases = concat(cases, getCharRange('0', '9'))
                
                
                elif '\\s' == c:
                
                    del p[c]
                    cases = concat(cases, ['\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029'])
                
                
                elif '\\w' == c:
                
                    del p[c]
                    cases = concat(cases, ['_'] + getCharRange('0', '9') + getCharRange('a', 'z') + getCharRange('A', 'Z'))
                
                
                elif '\\.' == c:
                
                    del p[c]
                    cases[ self.specialChars['.'] ] = 1
                
                
                elif '\\' != c[0] and isCaseInsensitive:
                
                    cases[ c.lower() ] = 1
                    cases[ c.upper() ] = 1
                
                
                elif '\\' == c[0]:
                
                    del p[c]
                
            
            peek[n] = concat(p, cases)
        
        return peek
    
    def setRegex(self, regex=None, delim=None):
        if regex:
            self.flags = {}
            
            if !delim: delim = '/'
            
            r = str(regex)
            l = len(r)
            ch = r[l-1]
            
            # parse regex flags
            while delim != ch:
            
                self.flags[ ch ] = 1;
                r = r[0:l-1]
                l -= 1
                ch = r[l-1]
            
            # remove regex delimiters
            if delim == r[0] and delim == r[l-1]:  r = r[1:l-2]
            
            self.regex = r
        
        return self
    
    
    def analyze( self ):
        word = ''
        alternation = []
        sequence = []
        escaped = False
        
        self.pos = 0
        self.groupIndex = 0
        
        l = len(self.regex)
        while self.pos < l:
            ch = self.regex[ self.pos ]
            self.pos += 1
            
            #   \\abc
            escaped = True if (self.escapeChar == ch) else False
            if self.pos < l and escaped:  
                ch = self.regex[ self.pos ]
                self.pos += 1
            
            if escaped:
                # unicode character
                if 'u' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    preg_match($this->unicodeRegex, substr($this->regex, $this->pos-1 ), $match );
                    self.pos += len(match[0])-1
                    sequence.append( {'part': match[0], 'flags': { "Char": chr(intval(match[1], 16)), "Code": match[1] }, 'type': "UnicodeChar"} )
                
                # hex character
                elif 'x' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    preg_match($this->hexRegex, substr($this->regex, $this->pos-1 ), $match );
                    self.pos += len(match[0])-1;
                    sequence.append( {'part': match[0], 'flags': { "Char": chr(intval($match[1], 16)), "Code": $match[1] }, 'type': "HexChar"} )
                
                elif ch in self.specialCharsEscaped and '/' != ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    flag = {}
                    flag[ self.specialCharsEscaped[ch] ] = 1
                    sequence.append( {'part': ch, 'flags': flag, 'type': "Special"} )
                
                else:
                    word += ch
            
            else:
                # parse alternation
                if '|' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
                    $sequence = array();
                
                # parse character group
                elif '[' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $sequence[] = $this->chargroup();
                
                # parse sub-group
                elif '(' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $sequence[] = $this->subgroup();
                
                # parse num repeats
                elif '{' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    preg_match($this->repeatsRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $flag = array( 'part'=> $match[0], "MatchMinimum"=> $match[1], "MatchMaximum"=> isset($match[2]) ? $match[2] : "unlimited" );
                    $flag[ $this->specialChars[$ch] ] = 1;
                    if ( $this->pos < $l && '?' == $this->regex[$this->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $this->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( "String" == $prev['type'] && strlen($prev['part']) > 1 )
                    {
                        $sequence[] = array( 'part'=> substr($prev['part'], 0, -1), 'flags'=> array(), 'type'=> "String" );
                        $prev['part'] = substr($prev['part'], -1);
                    }
                    $sequence[] = array( 'part'=> $prev, 'flags'=> $flag, 'type'=> "Quantifier" );
                
                # quantifiers
                elif '*' == ch or '+' == ch or '?' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $flag = array();
                    $flag[ $this->specialChars[$ch] ] = 1;
                    if ( $this->pos < $l && '?' == $this->regex[$this->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $this->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( "String" == $prev['type'] && strlen($prev['part']) > 1 )
                    {
                        $sequence[] = array( 'part'=> substr($prev['part'], 0, -1), 'flags'=> array(), 'type'=> "String" );
                        $prev['part'] = substr($prev['part'], -1);
                    }
                    $sequence[] = array( 'part'=> $prev, 'flags'=> $flag, 'type'=> "Quantifier" );
            
                # special characters like ^, $, ., etc..
                elif ( isset($this->specialChars[$ch]) ):
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $flag = array();
                    $flag[ $this->specialChars[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
            
                else:
                    word += ch
        
        if len(word):
            sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
            word = ''
        
        if len(alternation):
            $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
            $sequence = array();
            $flag = array();
            $flag[ $this->specialChars['|'] ] = 1;
            $this->parts = array( 'part'=> $alternation, 'flags'=> $flag, 'type'=> "Alternation" );
        else:
            $this->parts = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
        
        return self

    def subgroup(self):
        word = ''
        alternation = []
        sequence = []
        flags = {}
        escaped = False
        
        pre = self.regex[self.pos:self.pos+2]
        
        if "?:" == pre:
            flags[ "NotCaptured" ] = 1
            self.pos += 2
        
        elif "?=" == pre:
            flags[ "LookAhead" ] = 1
            self.pos += 2
        
        elif "?!" == pre:
            flags[ "NegativeLookAhead" ] = 1
            self.pos += 2
        
        self.groupIndex += 1
        flags[ "GroupIndex" ] = self.groupIndex
        l = len(self.regex)
        while self.pos < l:
            ch = self.regex[ self.pos ]
            self.pos += 1
            
            escaped = True if (self.escapeChar == ch) else False
            if self.pos < l and escaped:  
                ch = self.regex[ self.pos ]
                self.pos += 1
            
            if escaped:
                # unicode character
                if 'u' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    preg_match($this->unicodeRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "UnicodeChar" );
                
                # hex character
                elif 'x' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    preg_match($this->hexRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "HexChar" );
                
                elif ( isset($this->specialCharsEscaped[$ch]) && '/' != $ch):
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $flag = array();
                    $flag[ $this->specialCharsEscaped[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
                
                else:
                    word += ch
            
            else:
                # group end
                if ')' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    if ( count($alternation) )
                    {
                        $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
                        $sequence = array();
                        $flag = array();
                        $flag[ $this->specialChars['|'] ] = 1;
                        return array( 'part'=> array( 'part'=> $alternation, 'flags'=> $flag, 'type'=> "Alternation" ), 'flags'=> $flags, 'type'=> "Group" );
                    }
                    else
                    {
                        return array( 'part'=> array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" ), 'flags'=> $flags, 'type'=> "Group" );
                    }
                
                # parse alternation
                elif '|' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
                    $sequence = array();
                
                # parse character group
                elif '[' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $sequence[] = $this->chargroup();
                
                # parse sub-group
                elif '(' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $sequence[] = $this->subgroup();
                
                # parse num repeats
                elif '{' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    preg_match($thus->repeatsRegex, substr($this->regex, this.pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $flag = array( 'part'=> $match[0], "MatchMinimum"=> $match[1], "MatchMaximum"=> isset($match[2]) ? $match[2] : "unlimited" );
                    $flag[ $this->specialChars[$ch] ] = 1;
                    if ( $this->pos < $l && '?' == $this->regex[$this->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $this->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( "String" == $prev['type'] && strlen($prev['part']) > 1 )
                    {
                        $sequence[] = array( 'part'=> substr($prev['part'], 0, -1), 'flags'=> array(), 'type'=> "String" );
                        $prev['part'] = substr($prev['part'], -1);
                    }
                    $sequence[] = array( 'part'=> $prev, 'flags'=> $flag, 'type'=> "Quantifier" );
                
                # quantifiers
                elif '*' == ch or '+' == ch or '?' == ch:
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $flag = array();
                    $flag[ $this->specialChars[$ch] ] = 1;
                    if ( $this->pos < $l && '?' == $this->regex[$this->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $this->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( "String" == $prev['type'] && strlen($prev['part']) > 1 )
                    {
                        $sequence[] = array( 'part'=> substr($prev['part'], 0, -1), 'flags'=> array(), 'type'=> "String" );
                        $prev['part'] = substr($prev['part'], -1);
                    }
                    $sequence[] = array( 'part'=> $prev, 'flags'=> $flag, 'type'=> "Quantifier" );
            
                # special characters like ^, $, ., etc..
                elif ( isset($this->specialChars[$ch]) ):
                    if len(word):
                        sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
                        word = ''
                    $flag = array();
                    $flag[ $this->specialChars[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
            
                else:
                    word += ch
                    
        if len(word):
            sequence.append( { 'part': word, 'flags': {}, 'type': "String"} )
            word = ''
        
        if len(alternation):
            $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
            $sequence = array();
            $flag = array();
            $flag[ $this->specialChars['|'] ] = 1;
            return array( 'part'=> array( 'part'=> $alternation, 'flags'=> $flag, 'type'=> "Alternation" ), 'flags'=> $flags, 'type'=> "Group" );
        else:
            return array( 'part'=> array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" ), 'flags'=> $flags, 'type'=> "Group" );
    
    def chargroup(self):
        sequence = []
        chars = []
        flags = {}
        isRange = False
        escaped = False
        ch = ''
        
        if '^' == self.regex[ self.pos ]:
            flags[ "NotMatch" ] = 1
            self.pos += 1

        l = len(self.regex)
        while self.pos < l:
            isUnicode = False
            prevch = ch
            ch = self.regex[ self.pos ]
            self.pos += 1
            
            escaped = True if (self.escapeChar == ch) else False
            if self.pos < l and escaped:  
                ch = self.regex[ self.pos ]
                self.pos += 1
            
            if escaped:
                # unicode character
                if 'u' == ch:
                    preg_match($this->unicodeRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $ch = chr(intval($match[1], 16));
                    $isUnicode = true;
                
                # hex character
                elif 'x' == ch:
                    preg_match($this->hexRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $ch = chr(intval($match[1], 16));
                    $isUnicode = true;
            
            if isRange:
                if len(chars):
                    $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
                    $chars = array();
                $range[1] = $ch;
                $isRange = false;
                $sequence[] = array( 'part'=> $range, 'flags'=> array(), 'type'=> "CharRange" );
            else:
                if escaped:
                    if !isUnicode and isset($this->specialCharsEscaped[$ch]) && '/' != $ch:
                        if len(chars):
                            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
                            $chars = array();
                        $flag = array();
                        $flag[ $this->specialCharsEscaped[$ch] ] = 1;
                        $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
                    
                    else:
                        chars.append(ch)
                
                else:
                    # end of char group
                    if ']' == ch:
                        if ( count($chars) )
                        {
                            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
                            $chars = array();
                        }
                        return array( 'part'=> $sequence, 'flags'=> $flags, 'type'=> "CharGroup" );
                    
                    elif '-' == ch:
                        $range = array($prevch, '');
                        array_pop($chars);
                        isRange = True
                    
                    else:
                        chars.append(ch)
        
        if len(chars):
            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
            $chars = array();
        return array( 'part'=> $sequence, 'flags'=> $flags, 'type'=> "CharGroup" );
    
# if used with 'import *'
__all__ = ['RegExAnalyzer']
