<?php
/**
*
*   RegExAnalyzer
*   @version: 0.1
*
*   A simple Regular Expression Analyzer in PHP
*   https://github.com/foo123/regex-analyzer
*
**/
if ( !class_exists('RegExAnalyzer') )
{
class RegExAnalyzer
{
    const VERSION = "0.1";
    
    public $regex = null;
    public $flags = null;
    public $parts = null;
    
    private $groupIndex = null;
    private $pos = null;
    
    public $escapeChar = '\\';
    
    public $repeatsRegex = '/^\\{\\s*(\\d+)\\s*,?\\s*(\\d+)?\\s*\\}/';
    
    public $unicodeRegex = '/^u([0-9a-fA-F]{4})/';
    
    public $hexRegex = '/^x([0-9a-fA-F]{2})/';
    
    public $specialChars = array(
        "." => "MatchAnyChar",
        "|" => "MatchEither",
        "?" => "MatchZeroOrOne",
        "*" => "MatchZeroOrMore",
        "+" => "MatchOneOrMore",
        "^" => "MatchStart",
        "$" => "MatchEnd",
        "{" => "StartRepeats",
        "}" => "EndRepeats",
        "(" => "StartGroup",
        ")" => "EndGroup",
        "[" => "StartCharGroup",
        "]" => "EndCharGroup"
    );
    
    public $specialCharsEscaped = array(
        "\\" => "EscapeChar",
        "/" => "/",
        "0" => "NULChar",
        "f" => "FormFeed",
        "n" => "LineFeed",
        "r" => "CarriageReturn",
        "t" => "HorizontalTab",
        "v" => "VerticalTab",
        "b" => "MatchWordBoundary",
        "B" => "MatchNonWordBoundary",
        "s" => "MatchSpaceChar",
        "S" => "MatchNonSpaceChar",
        "w" => "MatchWordChar",
        "W" => "MatchNonWordChar",
        "d" => "MatchDigitChar",
        "D" => "MatchNonDigitChar"
    );
    
    private static function concat($p1, $p2) 
    {
        if ( $p2 && is_array( $p2 ) )
        {
            $l = count($p2);
            for ($p=0; $p<$l; $p++)
            {
                $p1[ $p2[ $p ] ] = 1;
            }
        }
        else
        {
            foreach ($p2 as $p=>$dummy)
            {
                $p1[ $p ] = 1;
            }
        }
        return $p1;
    }
    
    // http://stackoverflow.com/questions/12376870/create-an-array-of-characters-from-specified-range
    // http://stackoverflow.com/questions/12990195/javascript-function-in-php-fromcharcode
    // http://stackoverflow.com/questions/9878483/php-equivlent-of-fromcharcode
    private static function getCharRange($first, $last) 
    {
        if ( $first && is_array($first) )
        {
            $last = $first[1];
            $first = $first[0];
        }
        $start = (int)$first[0]; 
        $end = (int)$last[0];
        
        if ( $end == $start ) return array( chr( $start ) );
        
        $chars = array();
        for ($ch = $start; $ch <= $end; ++$ch)
            $chars[] = chr( $ch );
        
        return $chars;
    }
    
    private static function GetPeekChars( $part ) 
    {
        $peek = array(); 
        $negativepeek = array(); 
        
        $type = $part['type'];
        // walk the sequence
        if ( "Alternation" == $type )
        {
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $tmp = self::GetPeekChars( $part['part'][$i] );
                $peek = self::concat( $peek, $tmp['peek'] );
                $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
            }
        }
        
        else if ( "Group" == $type )
        {
            $tmp = self::GetPeekChars( $part['part'] );
            $peek = self::concat( $peek, $tmp['peek'] );
            $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
        }
        
        else if ( "Sequence" == $type )
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
                $tmp = self::GetPeekChars( $p['part'] );
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
                    $tmp = self::GetPeekChars( $p );
                    $peek = self::concat( $peek, $tmp['peek'] );
                    $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
                }
            }
        }
        
        else if ( "CharGroup" == $type )
        {
            if ( isset($part['flags']['NotMatch']) )
                $current =& $negativepeek;
            else
                $current =& $peek;
            
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                $ptype = $p['type'];
                if ( "Chars" == $ptype )
                {
                    $current = self::concat( $current, $p['part'] );
                }
                
                else if ( "CharRange" == $ptype )
                {
                    $current = self::concat( $current, self::getCharRange($p['part']) );
                }
                
                else if ( "UnicodeChar" == $ptype || "HexChar" == $ptype )
                {
                    $current[$p['flags']['Char']] = 1;
                }
                
                else if ( "Special" == $ptype )
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
        
        else if ( "String" == $type )
        {
            $peek[$part['part'][0]] = 1;
        }
        
        else if ( "Special" == $type && !isset($part['flags']['MatchStart']) && !isset($part['flags']['MatchEnd']) )
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
                
        else if ( "UnicodeChar" == $type || "HexChar" == $type )
        {
            $peek[$part['flags']['Char']] = 1;
        }
        
        return array( 'peek'=> $peek, 'negativepeek'=> $negativepeek );
    }
    
    // A simple (js-flavored) regular expression analyzer
    public function __construct( $regex=null, $delim=null )
    {
        if ( $regex ) $this->setRegex($regex, $delim);
    }
    
    
    // experimental feature
    public function getPeekChars( ) 
    {
        $isCaseInsensitive = $this->flags && isset($this->flags['i']);
        $peek = self::GetPeekChars($this->parts);
        
        foreach ($peek as $n=>$p)
        {
            $cases = array();
            
            // either peek or negativepeek
            foreach ($p as $c=>$dummy)
            {
                if ('\\d' == $c)
                {
                    unset( $p[$c] );
                    $cases = self::concat($cases, self::getCharRange('0', '9'));
                }
                
                else if ('\\s' == $c)
                {
                    unset( $p[$c] );
                    $cases = self::concat($cases, array('\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029'));
                }
                
                else if ('\\w' == $c)
                {
                    unset( $p[$c] );
                    $cases = self::concat($cases, array_merge(
                            array('_'), 
                            self::getCharRange('0', '9'), 
                            self::getCharRange('a', 'z'), 
                            self::getCharRange('A', 'Z') 
                        ));
                }
                
                else if ('\\.' == $c)
                {
                    unset( $p[$c] );
                    $cases[ $this->specialChars['.'] ] = 1;
                }
                
                /*else if ('\\^' == $c)
                {
                    unset( $p[$c] );
                    $cases[ $this->specialChars['^'] ] = 1;
                }
                
                else if ('\\$' == $c)
                {
                    unset( $p[$c] );
                    $cases[ $this->specialChars['$'] ] = 1;
                }*/
                
                else if ( '\\' != $c[0] && $isCaseInsensitive )
                {
                    $cases[ strtolower($c) ] = 1;
                    $cases[ strtoupper($c) ] = 1;
                }
                
                else if ( '\\' == $c[0] )
                {
                    unset( $p[$c] );
                }
            }
            $peek[$n] = self::concat($p, $cases);
        }
        return $peek;
    }
    
    public function setRegex($regex=null, $delim=null) 
    {
        if ( $regex )
        {
            $this->flags = array();
            
            $delim = $delim ? $delim : '/';
            $r = strval($regex); 
            $l = strlen($r);
            $ch = $r[$l-1];
            
            // parse regex flags
            while ( $delim != $ch )
            {
                $this->flags[ $ch ] = 1;
                $r = substr($r, 0, $l-1);
                $l--;
                $ch = $r[$l-1];
            }
            // remove regex delimiters
            if ( $delim == $r[0] && $delim == $r[$l-1] )  $r = substr($r, 1, $l-2);
            
            $this->regex = $r;
        }
        return $this;
    }
    
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
    
}
}