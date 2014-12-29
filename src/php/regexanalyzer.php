<?php
/**
*
*   RegExAnalyzer
*   @version: 0.4.3
*
*   A simple Regular Expression Analyzer for PHP, Python, Node/JS, ActionScript
*   https://github.com/foo123/RegexAnalyzer
*
**/
if ( !class_exists('RegExAnalyzer') )
{
class RegExAnalyzer
{
    const VERSION = "0.4.3";
    
    public static $escapeChar = null;
    public static $specialChars = null;
    public static $specialCharsEscaped = null;
    public static $BSPACES = null;
    public static $SPACES = null;
    public static $PUNCTS = null;
    public static $DIGITS = null; 
    public static $DIGITS_RANGE = null;
    public static $HEXDIGITS_RANGES = null;
    public static $ALPHAS = null;
    public static $ALL = null; 
    public static $ALL_ARY = null;
    
    public static function init( )
    {
        static $inited = false;
        if ( $inited ) return;
        
        self::$escapeChar = '\\';
        self::$specialChars = array(
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
        self::$specialCharsEscaped = array(
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
        self::$BSPACES = array("\r","\n");
        self::$SPACES = array(" ","\t","\v");
        self::$PUNCTS = array("~","!","@","#","$","%","^","&","*","(",")","-","+","=","[","]","{","}","\\","|",";",":",",",".","/","<",">","?");
        self::$DIGITS = array("0","1","2","3","4","5","6","7","8","9"); 
        self::$DIGITS_RANGE = self::char_code_range(self::$DIGITS);
        self::$HEXDIGITS_RANGES = array(self::$DIGITS_RANGE, array(self::char_code("a"), self::char_code("f")), array(self::char_code("A"), self::char_code("F")));
        self::$ALPHAS = array_merge(array("_"), self::character_range("a", "z"), self::character_range("A", "Z"));
        self::$ALL = array_merge(self::$SPACES,self::$PUNCTS,self::$DIGITS,self::$ALPHAS);
        //self::$ALL_ARY = @explode("", self::$ALL);
        
        $inited = true;
    }
    
    private static function char_code( $c ) 
    { 
        return ord($c[0]); 
    }
    private static function char_code_range( $s ) 
    { 
        $l = is_array($s) ? count($s) : strlen($s);
        return array(ord($s[0]), ord($s[$l-1])); 
    }
    private static function character_range($first, $last=null) 
    {
        if ( $first && is_array($first) )
        {
            $last = $first[1];
            $first = $first[0];
        }
        $start = ord($first[0]); 
        $end = ord($last[0]);
        
        if ( $end == $start ) return array( chr( $start ) );
        
        $chars = array();
        for ($ch = $start; $ch <= $end; ++$ch)
            $chars[] = chr( $ch );
        
        return $chars;
    }
    private static function concat($p1, $p2) 
    {
        if ( $p2 )
        {
            if ( $p2 == array_values($p2) ) $arr = $p2;
            else $arr = array_keys($p2);
            foreach ($arr as $p)
            {
                $p1[ $p ] = 1;
            }
        }
        return $p1;
    }
    
    private static function match_chars( $CHARS, $s, $pos=0, $minlen=1, $maxlen=INF ) 
    {
        $lp = $pos; $l = 0; $sl = strlen($s);
        while ( ($lp < $sl) && ($l <= $maxlen) && in_array($ch=$s[$lp], $CHARS) ) 
        { 
            $lp++; $l++; 
        }
        return ($l >= $minlen) ? $l : false;
    }
    private static function match_char_range( $RANGE, $s, $pos=0, $minlen=1, $maxlen=INF ) 
    {
        $lp = $pos; $l = 0; $sl = strlen($s);
        while ( ($lp < $sl) && ($l <= $maxlen) && (($ch=ord($s[$lp])) >= $RANGE[0] && $ch <= $RANGE[1]) ) 
        { 
            $lp++; $l++;
        }
        return ($l >= $minlen) ? $l : false;
    }
    private static function match_char_ranges( $RANGES, $s, $pos=0, $minlen=1, $maxlen=INF ) 
    {
        $lp = $pos; $l = 0; $sl = strlen($s); 
        $Rl = count($RANGES); $found = true;
        while ( ($lp < $sl) && ($l <= $maxlen) && $found ) 
        { 
            $ch = ord($s[$lp]); $found = false;
            for ($i=0; $i<$Rl; $i++)
            {
                $RANGE = $RANGES[$i];
                if ( $ch >= $RANGE[0] && $ch <= $RANGE[1] )
                {
                    $lp++; $l++; $found = true;
                    break;
                }
            }
        }
        return ($l >= $minlen) ? $l : false;
    }
    private static function punct( )
    { 
        return self::$PUNCTS[rand(0, count(self::$PUNCTS)-1)]; 
    }
    private static function space( $positive=true )
    { 
        if ( false !== $positive )
        {
            return self::$SPACES[rand(0, count(self::$SPACES)-1)];
        }
        else 
        {
            $s = array(self::punct(),self::digit(),self::alpha());
            return $s[rand(0,2)];
        }
    }
    private static function digit( $positive=true )
    { 
        if ( false !== $positive )
        {
            return self::$DIGITS[rand(0, count(self::$DIGITS)-1)];
        }
        else 
        {
            $s = array(self::punct(),self::space(),self::alpha());
            return $s[rand(0,2)];
        }
    }
    private static function alpha( $positive=true )
    { 
        if ( false !== $positive )
        {
            return self::$ALPHAS[rand(0, count(self::$ALPHAS)-1)];
        }
        else 
        {
            $s = array(self::punct(),self::space(),self::digit());
            return $s[rand(0,2)];
        }
    }
    private static function word( $positive=true )
    { 
        if ( false !== $positive )
        {
            $s = array_merge(self::$ALPHAS , self::$DIGITS);
            return $s[rand(0, count($s)-1)];
        }
        else 
        {
            $s = array(self::punct(),self::space());
            return $s[rand(0,1)];
        }
    }
    private static function any( )
    { 
        return self::$ALL[rand(0, count(self::$ALL)-1)];
    }
    private static function character( $chars, $positive=true )
    { 
        if ( false !== $positive )
        {
            $l = count($chars);
            return $l ? $chars[rand(0, $l-1)] : '';
        }
        else 
        {
            $choices = array();
            foreach (self::$ALL as $choice)
            {
                if ( false === strpos($chars, $choice) ) $choices[] = $choice;
            }
            $l = count($choices);
            return $l ? $choices[rand(0, $l-1)] : '';
        }
    }
    private static function random_upper_or_lower( $c ) 
    { 
        return rand(0,1) ? strtolower($c) : strtoupper($c); 
    }
    private static function case_insensitive( $chars, $asArray=false ) 
    {
        if ( $asArray )
        {
            if ( is_string($chars) ) $chars = explode("", $chars);
            $chars = array_map(array(__CLASS__, 'random_upper_or_lower'), $chars);
            //if ( !asArray ) chars = chars.join('');
            return $chars;
        }
        else
        {
            return self::random_upper_or_lower( $chars );
        }
    }
    private static function generate( $part, $isCaseInsensitive=false ) 
    {
        $sample = '';
        
        $type = $part['type'];
        // walk the sequence
        if ( "Alternation" == $type )
        {
            $sample .= self::generate( $part['part'][rand(0, count($part['part'])-1)], $isCaseInsensitive );
        }
        
        elseif ( "Group" == $type )
        {
            $sample .= self::generate( $part['part'], $isCaseInsensitive );
        }
        
        elseif ( "Sequence" == $type )
        {
            $i = 0;
            $l = count($part['part']);
            $p = $part['part'][$i];
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                if ( !$p ) continue;
                $repeat = 1;
                if ( "Quantifier" == $p['type'] )
                {
                    if ( isset($p['flags']['MatchZeroOrMore']) && $p['flags']['MatchZeroOrMore'] ) $repeat = rand(0, 10);
                    elseif ( isset($p['flags']['MatchZeroOrOne']) && $p['flags']['MatchZeroOrOne'] ) $repeat = rand(0, 1);
                    elseif ( isset($p['flags']['MatchOneOrMore']) && $p['flags']['MatchOneOrMore'] ) $repeat = rand(1, 11);
                    else 
                    {
                        $mmin = intval($p['flags']['MatchMinimum'], 10);
                        $mmax = intval($p['flags']['MatchMaximum'], 10);
                        $repeat = rand($mmin, is_nan($mmax) ? ($mmin+10) : $mmax);
                    }
                    while ( $repeat > 0 ) 
                    {
                        $repeat--;
                        $sample .= self::generate( $p['part'], $isCaseInsensitive );
                    }
                }
                else if ( "Special" == $p['type'] )
                {
                    if ( isset($p['flags']['MatchAnyChar']) && $p['flags']['MatchAnyChar'] ) $sample .= self::any( );
                }
                else
                {
                    $sample .= self::generate( $p, $isCaseInsensitive );
                }
            }
        }
        
        elseif ( "CharGroup" == $type )
        {
            $chars = array();
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                $ptype = $p['type'];
                if ( "Chars" == $ptype )
                {
                    if ( $isCaseInsensitive )
                        $chars = array_merge($chars, self::case_insensitive( $p['part'], true ) );
                    else
                        $chars = array_merge($chars, $p['part'] );
                }
                
                elseif ( "CharRange" == $ptype )
                {
                    if ( $isCaseInsensitive )
                        $chars = array_merge($chars, self::case_insensitive( self::character_range($p['part']), true ) );
                    else
                        $chars = array_merge($chars, self::character_range($p['part']) );
                }
                
                elseif ( "UnicodeChar" == $ptype || "HexChar" == $ptype )
                {
                    $chars[] = $isCaseInsensitive ? self::case_insensitive( $p['flags']['Char'] ): $p['flags']['Char'];
                }
                
                elseif ( "Special" == $ptype )
                {
                    $p_part = $p['part'];
                    if ('D' == $p_part)
                    {
                        $chars[] = self::digit( false );
                    }
                    elseif ('W' == $p_part)
                    {
                        $chars[] = self::word( false );
                    }
                    elseif ('S' == $p_part)
                    {
                        $chars[] = self::space( false );
                    }
                    elseif ('d' == $p_part)
                    {
                        $chars[] = self::digit( );
                    }
                    elseif ('w' == $p_part)
                    {
                        $chars[] = self::word( );
                    }
                    elseif ('s' == $p_part)
                    {
                        $chars[] = self::space( );
                    }
                    else
                    {
                        $chars[] = '\\' . $p_part;
                    }
                }
            }
            $sample .= self::character($chars, isset($part['flags']['NotMatch']) && $part['flags']['NotMatch'] ? false: true);
        }
        
        elseif ( "String" == $type )
        {
            $sample .= $isCaseInsensitive ? self::case_insensitive( $part['part'] ) : $part['part'];
        }
        
        elseif ( "Special" == $type && 
            (!isset($part['flags']['MatchStart']) || !$part['flags']['MatchStart']) && 
            (!isset($part['flags']['MatchEnd']) || !$part['flags']['MatchEnd']) )
        {
            $p_part = $part['part'];
            if ('D' == $p_part)
            {
                $sample .= self::digit( false );
            }
            elseif ('W' == $p_part)
            {
                $sample .= self::word( false );
            }
            elseif ('S' == $p_part)
            {
                $sample .= self::space( false );
            }
            elseif ('d' == $p_part)
            {
                $sample .= self::digit( );
            }
            elseif ('w' == $p_part)
            {
                $sample .= self::word( );
            }
            elseif ('s' == $p_part)
            {
                $sample .= self::space( );
            }
            elseif ('.' == $p_part)
            {
                $sample .= self::any( );
            }
            else
            {
                $sample .= '\\' . $p_part;
            }
        }
                
        elseif ( "UnicodeChar" == $type || "HexChar" == $type )
        {
            $sample .= $isCaseInsensitive ? self::case_insensitive( $part['flags']['Char'] ) : $part['flags']['Char'];
        }
        
        return $sample;
    }

    private static function peek_characters( $part ) 
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
                $tmp = self::peek_characters( $part['part'][$i] );
                $peek = self::concat( $peek, $tmp['peek'] );
                $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
            }
        }
        
        elseif ( "Group" == $type )
        {
            $tmp = self::peek_characters( $part['part'] );
            $peek = self::concat( $peek, $tmp['peek'] );
            $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
        }
        
        elseif ( "Sequence" == $type )
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
                $tmp = self::peek_characters( $p['part'] );
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
                
                if ("Special" == $p['type'] && ('^'==$p['part'] || '$'==$p['part'])) 
                    $p = isset($part['part'][$i+1]) ? $part['part'][$i+1] : null;
                
                if ($p && "Quantifier" == $p['type']) $p = $p['part'];
                
                if ($p)
                {
                    $tmp = self::peek_characters( $p );
                    $peek = self::concat( $peek, $tmp['peek'] );
                    $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
                }
            }
        }
        
        elseif ( "CharGroup" == $type )
        {
            $isNegative = isset($part['flags']['NotMatch']) && $part['flags']['NotMatch'];
            $current = array();
            
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                $ptype = $p['type'];
                if ( "Chars" == $ptype )
                {
                    $current = self::concat( $current, $p['part'] );
                }
                
                elseif ( "CharRange" == $ptype )
                {
                    $current = self::concat( $current, self::character_range($p['part']) );
                }
                
                elseif ( "UnicodeChar" == $ptype || "HexChar" == $ptype )
                {
                    $current[$p['flags']['Char']] = 1;
                }
                
                elseif ( "Special" == $ptype )
                {
                    $p_part = $p['part'];
                    if ('D' == $p_part)
                    {
                        if (isset($part['flags']['NotMatch']) && $part['flags']['NotMatch'])
                            $peek[ '\\d' ] = 1;
                        else
                            $negativepeek[ '\\d' ] = 1;
                    }
                    elseif ('W' == $p_part)
                    {
                        if (isset($part['flags']['NotMatch']) && $part['flags']['NotMatch'])
                            $peek[ '\\w' ] = 1;
                        else
                            $negativepeek[ '\\W' ] = 1;
                    }
                    elseif ('S' == $p_part)
                    {
                        if (isset($part['flags']['NotMatch']) && $part['flags']['NotMatch'])
                            $peek[ '\\s' ] = 1;
                        else
                            $negativepeek[ '\\s' ] = 1;
                    }
                    else
                    {
                        $current['\\' . $p_part] = 1;
                    }
                }
            }
            if ( $isNegative )
                $negativepeek = self::concat($negativepeek, $current);
            else
                $peek = self::concat($peek, $current);
        }
        
        elseif ( "String" == $type )
        {
            $peek[$part['part'][0]] = 1;
        }
        
        elseif ( "Special" == $type && 
            (!isset($part['flags']['MatchStart']) || !$part['flags']['MatchStart']) && 
            (!isset($part['flags']['MatchEnd']) || !$part['flags']['MatchEnd']) )
        {
            $p_part = $part['part'];
            if ('D' == $p_part)
            {
                $negativepeek[ '\\d' ] = 1;
            }
            else if ('W' == $p_part)
            {
                $negativepeek[ '\\W' ] = 1;
            }
            else if ('S' == $p_part)
            {
                $negativepeek[ '\\s' ] = 1;
            }
            else
            {
                $peek['\\' . $p_part] = 1;
            }
        }
                
        elseif ( "UnicodeChar" == $type || "HexChar" == $type )
        {
            $peek[$part['flags']['Char']] = 1;
        }
        
        return array('peek'=> $peek, 'negativepeek'=> $negativepeek);
    }
    
    private static function match_hex( $s ) 
    {
        $m = false;
        if ( strlen($s) > 2 && 'x' == $s[0] )
        {
            if ( self::match_char_ranges(self::$HEXDIGITS_RANGES, $s, 1, 2, 2) ) 
                return array($m=substr($s,0,3), substr($m,1));
        }
        return false;
    }
    private static function match_unicode( $s ) 
    {
        $m = false;
        if ( strlen($s) > 4 && 'u' == $s[0] )
        {
            if ( self::match_char_ranges(self::$HEXDIGITS_RANGES, $s, 1, 4, 4) ) 
                return array($m=substr($s,0,5), substr($m,1));
        }
        return false;
    }
    private static function match_repeats( $s ) 
    {
        $pos = 0; $m = false; $sl = strlen($s);
        if ( $sl > 2 && '{' == $s[$pos] )
        {
            $m = array('', '', null);
            $pos++;
            if ( $l=self::match_chars(self::$SPACES, $s, $pos) ) $pos += $l;
            if ( $l=self::match_char_range(self::$DIGITS_RANGE, $s, $pos) ) 
            {
                $m[1] = substr($s, $pos, $l);
                $pos += $l;
            }
            else
            {
                return false;
            }
            if ( $l=self::match_chars(self::$SPACES, $s, $pos) ) $pos += $l;
            if ( $pos < $sl && ',' === $s[$pos] ) $pos += 1;
            if ( $l=self::match_chars(self::$SPACES, $s, $pos) ) $pos += $l;
            if ( $l=self::match_char_range(self::$DIGITS_RANGE, $s, $pos) ) 
            {
                $m[2] = substr($s, $pos, $l);
                $pos += $l;
            }
            if ( $l=self::match_chars(self::$SPACES, $s, $pos) ) $pos += $l;
            if ( $pos < $sl && '}' == $s[$pos] )
            {
                $pos++;
                $m[0] = substr($s, 0, $pos);
                return $m;
            }
            else
            {
                return false;
            }
        }
        return false;
    }
    private static function analyze_re( $regex ) 
    {
        $obj = (object)array(
            'regex'=>$regex,
            'pos'=>0,
            'groupIndex'=>0
        );
        $word = ''; 
        $alternation = array(); 
        $sequence = array(); 
        $escaped = false;
        
        $lre = strlen($obj->regex);
        while ( $obj->pos < $lre )
        {
            $ch = $obj->regex[ $obj->pos++ ];
            
            //   \\abc
            $escaped = (self::$escapeChar == $ch) ? true : false;
            if ( $obj->pos < $lre && $escaped )  $ch = $obj->regex[ $obj->pos++ ];
            
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
                    $match = self::match_unicode(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
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
                    $match = self::match_hex(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "HexChar" );
                }
                
                else if ( isset(self::$specialCharsEscaped[$ch]) && '/' != $ch)
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ self::$specialCharsEscaped[$ch] ] = 1;
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
                    $sequence[] = self::chargroup( $obj );
                }
                
                // parse sub-group
                else if ( '(' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $sequence[] = self::subgroup( $obj );
                }
                
                // parse num repeats
                else if ( '{' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $match = self::match_repeats(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
                    $flag = array( 'part'=> $match[0], "MatchMinimum"=> $match[1], "MatchMaximum"=> isset($match[2]) ? $match[2] : "unlimited" );
                    $flag[ self::$specialChars[$ch] ] = 1;
                    if ( $obj->pos < $lre && '?' == $obj->regex[$obj->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $obj->pos++;
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
                    $flag[ self::$specialChars[$ch] ] = 1;
                    if ( $obj->pos < $lre && '?' == $obj->regex[$obj->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $obj->pos++;
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
                else if ( isset(self::$specialChars[$ch]) )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ self::$specialChars[$ch] ] = 1;
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
            $flag[ self::$specialChars['|'] ] = 1;
            return array( 'part'=> $alternation, 'flags'=> $flag, 'type'=> "Alternation" );
        }
        else
        {
            return array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" );
        }
    }
    private static function subgroup( &$obj ) 
    {
        
        $word = ''; 
        $alternation = array(); 
        $sequence = array(); 
        $flags = array(); 
        $escaped = false;
        
        $pre = substr($obj->regex, $obj->pos, 2);
        
        if ( "?:" == $pre )
        {
            $flags[ "NotCaptured" ] = 1;
            $obj->pos += 2;
        }
        
        else if ( "?=" == $pre )
        {
            $flags[ "LookAhead" ] = 1;
            $obj->pos += 2;
        }
        
        else if ( "?!" == $pre )
        {
            $flags[ "NegativeLookAhead" ] = 1;
            $obj->pos += 2;
        }
        
        $flags[ "GroupIndex" ] = ++$obj->groupIndex;
        $lre = strlen($obj->regex);
        while ( $obj->pos < $lre )
        {
            $ch = $obj->regex[ $obj->pos++ ];
            
            $escaped = (self::$escapeChar == $ch) ? true : false;
            if ( $obj->pos < $l && $escaped )  $ch = $obj->regex[ $obj->pos++ ];
            
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
                    $match = self::match_unicode(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
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
                    $match = self::match_hex(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
                    $sequence[] = array( 'part'=> $match[0], 'flags'=> array( "Char"=> chr(intval($match[1], 16)), "Code"=> $match[1] ), 'type'=> "HexChar" );
                }
                
                else if ( isset(self::$specialCharsEscaped[$ch]) && '/' != $ch)
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ self::$specialCharsEscaped[$ch] ] = 1;
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
                        $flag[ self::$specialChars['|'] ] = 1;
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
                    $sequence[] = self::chargroup( $obj );
                }
                
                // parse sub-group
                else if ( '(' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $sequence[] = self::subgroup( $obj );
                }
                
                // parse num repeats
                else if ( '{' == $ch )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $match = self::match_repeats(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
                    $flag = array( 'part'=> $match[0], "MatchMinimum"=> $match[1], "MatchMaximum"=> isset($match[2]) ? $match[2] : "unlimited" );
                    $flag[ self::$specialChars[$ch] ] = 1;
                    if ( $obj->pos < $lre && '?' == $obj->regex[$obj->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $obj->pos++;
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
                    $flag[ self::$specialChars[$ch] ] = 1;
                    if ( $obj->pos < $lre && '?' == $obj->regex[$obj->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $obj->pos++;
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
                else if ( isset(self::$specialChars[$ch]) )
                {
                    if ( strlen($word) )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'type'=> "String" );
                        $word = '';
                    }
                    $flag = array();
                    $flag[ self::$specialChars[$ch] ] = 1;
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
            $flag[ self::$specialChars['|'] ] = 1;
            return array( 'part'=> array( 'part'=> $alternation, 'flags'=> $flag, 'type'=> "Alternation" ), 'flags'=> $flags, 'type'=> "Group" );
        }
        else
        {
            return array( 'part'=> array( 'part'=> $sequence, 'flags'=> array(), 'type'=> "Sequence" ), 'flags'=> $flags, 'type'=> "Group" );
        }
    }
    private static function chargroup( &$obj ) 
    {
        
        $sequence = array(); 
        $chars = array(); 
        $flags = array(); 
        $isRange = false; 
        $escaped = false;
        $ch = '';
        
        if ( '^' == $obj->regex[ $obj->pos ] )
        {
            $flags[ "NotMatch" ] = 1;
            $obj->pos++;
        }
        $lre = strlen($obj->regex);
        while ( $obj->pos < $lre )
        {
            $isUnicode = false;
            $prevch = $ch;
            $ch = $obj->regex[ $obj->pos++ ];
            
            $escaped = (self::$escapeChar == $ch) ? true : false;
            if ( $obj->pos < $lre && $escaped )  $ch = $obj->regex[ $obj->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' == $ch )
                {
                    $match = self::match_unicode(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
                    $ch = chr(intval($match[1], 16));
                    $isUnicode = true;
                }
                
                // hex character
                else if ( 'x' == $ch )
                {
                    $match = self::match_hex(substr($obj->regex, $obj->pos-1));
                    $obj->pos += strlen($match[0])-1;
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
                    if ( !$isUnicode && isset(self::$specialCharsEscaped[$ch]) && '/' != $ch)
                    {
                        if ( count($chars) )
                        {
                            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'type'=> "Chars" );
                            $chars = array();
                        }
                        $flag = array();
                        $flag[ self::$specialCharsEscaped[$ch] ] = 1;
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
    
    
    // A simple (js-flavored) regular expression analyzer
    public $_regex = null;
    public $_flags = null;
    public $_parts = null;
    public $_needsRefresh = true;
    
    public function __construct( $regex=null, $delim=null )
    {
        if ( $regex ) $this->regex($regex, $delim);
    }
    
    public function dispose( ) 
    {
        $this->_regex = null;
        $this->_flags = null;
        $this->_parts = null;
        return $this;
    }
        
    public function regex($regex=null, $delim=null) 
    {
        if ( $regex )
        {
            $flags = array();
            
            $delim = $delim ? $delim : '/';
            $r = strval($regex); 
            $l = strlen($r);
            $ch = $r[$l-1];
            
            // parse regex flags
            while ( $delim != $ch )
            {
                $flags[ $ch ] = 1;
                $r = substr($r, 0, $l-1);
                $l--;
                $ch = $r[$l-1];
            }
            // remove regex delimiters
            if ( $delim == $r[0] && $delim == $r[$l-1] )  $r = substr($r, 1, $l-2);
            
            if ( $this->_regex !== $r ) $this->_needsRefresh = true;
            $this->_regex = $r; $this->_flags = $flags;
        }
        return $this;
    }
    
    public function analyze( ) 
    {
        if ( $this->_needsRefresh )
        {
            $this->_parts = self::analyze_re( $this->_regex );
            $this->_needsRefresh = false;
        }
        return $this;
    }
    
    public function getRegex( ) 
    {
        return '/' . $this->_regex . '/' . implode("", array_keys($this->_flags));
    }
    
    public function getParts( ) 
    {
        if ( $this->_needsRefresh ) $this->analyze( );
        return $this->_parts;
    }
    
    // experimental feature
    public function generateSample( ) 
    {
        if ( $this->_needsRefresh ) $this->analyze( );
        return self::generate( $this->_parts, isset($this->_flags['i']) );
    }
    
    // experimental feature, implement (optimised) RE matching as well
    public function match( $str ) 
    {
        //return self::match( $this->_parts, $str, 0, isset($this->_flags['i']) );
        return false;
    }
        
    // experimental feature
    public function getPeekChars( ) 
    {
        if ( $this->_needsRefresh ) $this->analyze( );
        $isCaseInsensitive = isset($this->_flags['i']);
        $peek = self::peek_characters( $this->_parts );
        
        foreach ($peek as $n=>$p)
        {
            $cases = array();
            
            // either peek or negativepeek
            foreach (array_keys($p) as $c)
            {
                if ('\\d' == $c)
                {
                    unset( $p[$c] );
                    $cases = self::concat($cases, self::character_range('0', '9'));
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
                            self::character_range('0', '9'), 
                            self::character_range('a', 'z'), 
                            self::character_range('A', 'Z') 
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
}
RegExAnalyzer::init();
}