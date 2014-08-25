# -*- coding: UTF-8 -*-
##
#
#   RegExAnalyzer
#   @version: 0.1
#
#   A simple Regular Expression Analyzer in Python
#   https://github.com/foo123/regex-analyzer
#
##
# needed imports
import re

class RegExAnalyzer:
    
    VERSION = "0.1"
    
    def concat(p1, p2=None):
    
        if p2 and isinstance(p2, (list, tuple)):
        
            l = len(p2)
            for p in range(l):
            
                p1[ p2[ p ] ] = 1
            
        
        else:
        
            for p in p2:
            
                p1[ p ] = 1;
            
        
        return p1
    
    
    # http://stackoverflow.com/questions/12376870/create-an-array-of-characters-from-specified-range
    def getCharRange(first=None, last=None):
    
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
    
    
    def _getPeekChars( part=None ):
    
        $peek = array(); 
        $negativepeek = array(); 
        
        
        # walk the sequence
        if ( "Alternation" == $part['type'] )
        {
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $tmp = self::getPeekChars( $part['part'][$i] );
                $peek = self::concat( $peek, $tmp['peek'] );
                $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
            }
        }
        
        else if ( "Group" == $part['type'] )
        {
            $tmp = self::getPeekChars( $part['part'] );
            $peek = self::concat( $peek, $tmp['peek'] );
            $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
        }
        
        else if ( "Sequence" == $part['type'] )
        {
            $i = 0;
            $l = count($part['part']);
            $p = $part['part'][$i];
            $done = ( 
                $i >= $l || !$p || "Quantifier" != $p['type'] || 
                ( !isset($p['flags']['MatchZeroOrMore']) && !isset($p['flags']['MatchZeroOrOne']) && (!isset($p['flags']['MatchMinimum']) || "0"!=$p['flags']['MatchMinimum']) ) 
            );
            while ( !$done )
            {
                $tmp = self::getPeekChars( $p['part'] );
                $peek = self::concat( $peek, $tmp['peek'] );
                $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
                
                $i++;
                $p = $part['part'][$i];
                
                $done = ( 
                    $i >= $l || !$p || "Quantifier" != $p['type'] || 
                    ( !isset($p['flags']['MatchZeroOrMore']) && !isset($p['flags']['MatchZeroOrOne']) && (!isset($p['flags']['MatchMinimum']) || "0"!=$p['flags']['MatchMinimum']) ) 
                );
            }
            if ( $i < $l )
            {
                $p = $part['part'][$i];
                
                if ("Special" == $p['type'] && ('^'==$p['part'] || '$'==$p['part'])) $p = $part['part'][$i+1] || null;
                
                if ($p && "Quantifier" == $p['type']) $p = $p['part'];
                
                if ($p)
                {
                    $tmp = self::getPeekChars( $p );
                    $peek = self::concat( $peek, $tmp['peek'] );
                    $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
                }
            }
        }
        
        else if ( "CharGroup" == $part['type'] )
        {
            if ( isset($part['flags']['NotMatch']) )
                $current =& $negativepeek;
            else
                $current =& $peek;
            
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                
                if ( "Chars" == $p['type'] )
                {
                    $current = self::concat( $current, $p['part'] );
                }
                
                else if ( "CharRange" == $p['type'] )
                {
                    $current = self::concat( $current, self::getCharRange($p['part']) );
                }
                
                else if ( "UnicodeChar" == $p['type'] || "HexChar" == $p['type'] )
                {
                    $current[$p['flags']['Char']] = 1;
                }
                
                else if ( "Special" == $p['type'] )
                {
                    if ('D' == $p['part'])
                    {
                        if (isset($part['flags']['NotMatch']))
                            $peek[ '\\d' ] = 1;
                        else
                            $negativepeek[ '\\d' ] = 1;
                    }
                    else if ('W' == $p['part'])
                    {
                        if (isset($part['flags']['NotMatch']))
                            $peek[ '\\w' ] = 1;
                        else
                            $negativepeek[ '\\W' ] = 1;
                    }
                    else if ('S' == $p['part'])
                    {
                        if (isset($part['flags']['NotMatch']))
                            $peek[ '\\s' ] = 1;
                        else
                            $negativepeek[ '\\s' ] = 1;
                    }
                    else
                    {
                        $current['\\' . $p['part']] = 1;
                    }
                }
            }
        }
        
        else if ( "String" == $part['type'] )
        {
            $peek[$part['part'][0]] = 1;
        }
        
        else if ( "Special" == $part['type'] && !isset($part['flags']['MatchStart']) && !isset($part['flags']['MatchEnd']) )
        {
            if ('D' == $part['part'])
            {
                $negativepeek[ '\\d' ] = 1;
            }
            else if ('W' == $part['part'])
            {
                $negativepeek[ '\\W' ] = 1;
            }
            else if ('S' == $part['part'])
            {
                $negativepeek[ '\\s' ] = 1;
            }
            else
            {
                $peek['\\' . $part['part']] = 1;
            }
        }
                
        else if ( "UnicodeChar" == $part['type'] || "HexChar" == $part['type'] )
        {
            $peek[$part['flags']['Char']] = 1;
        }
        
        return array( 'peek'=> $peek, 'negativepeek'=> $negativepeek );
    
    
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
        peek = RegExAnalyzer._getPeekChars(self.parts)
        
        for ($peek as $n=>$p):
        
            $cases = array();
            
            # either peek or negativepeek
            foreach ($p as $c=>$dummy):
            
                if ('\\d' == $c):
                
                    unset( $p[$c] );
                    $cases = self::concat($cases, self::getCharRange('0', '9'));
                
                
                elif ('\\s' == $c):
                
                    unset( $p[$c] );
                    $cases = self::concat($cases, array('\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029'));
                
                
                elif ('\\w' == $c):
                
                    unset( $p[$c] );
                    $cases = self::concat($cases, array_merge(
                            array('_'), 
                            self::getCharRange('0', '9'), 
                            self::getCharRange('a', 'z'), 
                            self::getCharRange('A', 'Z') 
                        ));
                
                
                elif ('\\.' == $c):
                
                    unset( $p[$c] );
                    $cases[ $this->specialChars['.'] ] = 1;
                
                
                elif ( '\\' != $c[0] && $isCaseInsensitive ):
                
                    $cases[ strtolower($c) ] = 1;
                    $cases[ strtoupper($c) ] = 1;
                
                
                elif ( '\\' == $c[0] ):
                
                    unset( $p[$c] );
                
            
            $peek[$n] = self::concat($p, $cases);
        
        return $peek
    
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
    
    
    public function analyze( ) 
    {
        $word = ''; 
        $alternation = array(); 
        $sequence = array(); 
        $escaped = false;
        
        $this->pos = 0;
        $this->groupIndex = 0;
        
        $l = strlen($this->regex);
        while ( $this->pos < $l )
        {
            $ch = $this->regex[ $this->pos++ ];
            
            //   \\abc
            $escaped = ($this->escapeChar == $ch) ? true : false;
            if ( $this->pos < $l && $escaped )  $ch = $this->regex[ $this->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    preg_match($this->unicodeRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "UnicodeChar" );
                }
                
                // hex character
                else if ( 'x' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    preg_match($this->hexRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "HexChar" );
                }
                
                else if ( isset($this->specialCharsEscaped[$ch]) && '/' != $ch)
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ $this->specialCharsEscaped[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
                }
                
                else
                {
                    $word .= $ch;
                }
            }
            
            else
            {
                // parse alternation
                if ( '|' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[]  = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
                    $sequence = array();
                }
                
                // parse character group
                else if ( '[' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $sequence[] = $this->chargroup();
                }
                
                // parse sub-group
                else if ( '(' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $sequence[] = $this->subgroup();
                }
                
                // parse num repeats
                else if ( '{' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
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
                }
                
                // quantifiers
                else if ( '*' == $ch || '+' == $ch || '?' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
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
                }
            
                // special characters like ^, $, ., etc..
                else if ( isset($this->specialChars[$ch]) )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ $this->specialChars[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
                }
            
                else
                {
                    $word .= $ch;
                }
            }
        }
        
        if ( strlen($word) )
        {
            $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
            $word = '';
        }
        
        if ( count($alternation) )
        {
            $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
            $sequence = array();
            $flag = array();
            $flag[ $this->specialChars['|'] ] = 1;
            $this->parts = array( 'part'=> $alternation, 'flags'=> $flag, 'type'=> "Alternation" );
        }
        else
        {
            $this->parts = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
        }
        
        return $this;
    }

    public function subgroup() 
    {
        
        $word = ''; 
        $alternation = array(); 
        $sequence = array(); 
        $flags = array(); 
        $escaped = false;
        
        $pre = substr($this->regex, $this->pos, 2);
        
        if ( "?:" == $pre )
        {
            $flags[ "NotCaptured" ] = 1;
            $this->pos += 2;
        }
        
        else if ( "?=" == $pre )
        {
            $flags[ "LookAhead" ] = 1;
            $this->pos += 2;
        }
        
        else if ( "?!" == $pre )
        {
            $flags[ "NegativeLookAhead" ] = 1;
            $this->pos += 2;
        }
        
        $flags[ "GroupIndex" ] = ++$this->groupIndex;
        $l = strlen($this->regex);
        while ( $this->pos < $l )
        {
            $ch = $this->regex[ $this->pos++ ];
            
            $escaped = ($this->escapeChar == $ch) ? true : false;
            if ( $this->pos < $l && $escaped )  $ch = $this->regex[ $this->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    preg_match($this->unicodeRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "UnicodeChar" );
                }
                
                // hex character
                else if ( 'x' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    preg_match($this->hexRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "HexChar" );
                }
                
                else if ( isset($this->specialCharsEscaped[$ch]) && '/' != $ch)
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ $this->specialCharsEscaped[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
                }
                
                else
                {
                    $word .= $ch;
                }
            }
            
            else
            {
                // group end
                if ( ')' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
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
                }
                
                // parse alternation
                else if ( '|' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
                    $sequence = array();
                }
                
                // parse character group
                else if ( '[' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $sequence[] = $this->chargroup();
                }
                
                // parse sub-group
                else if ( '(' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $sequence[] = $this->subgroup();
                }
                
                // parse num repeats
                else if ( '{' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
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
                }
                
                // quantifiers
                else if ( '*' == $ch || '+' == $ch || '?' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
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
                }
            
                // special characters like ^, $, ., etc..
                else if ( isset($this->specialChars[$ch]) )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ $this->specialChars[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
                }
            
                else
                {
                    $word .= $ch;
                }
            }
        }
        if ( strlen($word) )
        {
            $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
            $word = '';
        }
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
    }
    
    public function chargroup() 
    {
        
        $sequence = array(); 
        $chars = array(); 
        $flags = array(); 
        $isRange = false; 
        $escaped = false;
        $ch = '';
        
        if ( '^' == $this->regex[ $this->pos ] )
        {
            $flags[ "NotMatch" ] = 1;
            $this->pos++;
        }
        $l = strlen($this->regex);        
        while ( $this->pos < $l )
        {
            $isUnicode = false;
            $prevch = $ch;
            $ch = $this->regex[ $this->pos++ ];
            
            $escaped = ($this->escapeChar == $ch) ? true : false;
            if ( $this->pos < $l && $escaped )  $ch = $this->regex[ $this->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' == $ch )
                {
                    preg_match($this->unicodeRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $ch = chr(intval($match[1], 16));
                    $isUnicode = true;
                }
                
                // hex character
                else if ( 'x' == $ch )
                {
                    preg_match($this->hexRegex, substr($this->regex, $this->pos-1 ), $match );
                    $this->pos += strlen($match[0])-1;
                    $ch = chr(intval($match[1], 16));
                    $isUnicode = true;
                }
            }
            
            if ( $isRange )
            {
                if ( count($chars) )
                {
                    $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
                    $chars = array();
                }
                $range[1] = $ch;
                $isRange = false;
                $sequence[] = array( 'part'=> $range, 'flags'=> array(), 'type'=> "CharRange" );
            }
            else
            {
                if ( $escaped )
                {
                    if ( !$isUnicode && isset($this->specialCharsEscaped[$ch]) && '/' != $ch)
                    {
                        if ( count($chars) )
                        {
                            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
                            $chars = array();
                        }
                        $flag = array();
                        $flag[ $this->specialCharsEscaped[$ch] ] = 1;
                        $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'type'=> "Special" );
                    }
                    
                    else
                    {
                        $chars[]  = $ch;
                    }
                }
                
                else
                {
                    // end of char group
                    if ( ']' == $ch )
                    {
                        if ( count($chars) )
                        {
                            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
                            $chars = array();
                        }
                        return array( 'part'=> $sequence, 'flags'=> $flags, 'type'=> "CharGroup" );
                    }
                    
                    else if ( '-' == $ch )
                    {
                        $range = array($prevch, '');
                        array_pop($chars);
                        $isRange = true;
                    }
                    
                    else
                    {
                        $chars[] = $ch;
                    }
                }
            }
        }
        if ( count($chars) )
        {
            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
            $chars = array();
        }
        return array( 'part'=> $sequence, 'flags'=> $flags, 'type'=> "CharGroup" );
    }
    
# if used with 'import *'
__all__ = ['RegExAnalyzer']
