<?php
/**
*
*   RegexAnalyzer
*   @version: 0.4.4
*
*   A simple Regular Expression Analyzer for PHP, Python, Node/JS, ActionScript
*   https://github.com/foo123/RegexAnalyzer
*
**/
if ( !class_exists('RegexAnalyzer') )
{
class RegexAnalyzer
{
    const VERSION = "0.4.4";
    const T_SEQUENCE = 1; 
    const T_ALTERNATION = 2; 
    const T_GROUP = 3;
    const T_QUANTIFIER = 4; 
    const T_UNICODECHAR = 5; 
    const T_HEXCHAR = 6;
    const T_SPECIAL = 7;
    const T_CHARGROUP = 8; 
    const T_CHARS = 9;
    const T_CHARRANGE = 10; 
    const T_STRING = 11;
    
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
            foreach ($arr as $p) $p1[ $p ] = 1;
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
        if ( self::T_ALTERNATION === $type )
        {
            $sample .= self::generate( $part['part'][rand(0, count($part['part'])-1)], $isCaseInsensitive );
        }
        
        elseif ( self::T_GROUP === $type )
        {
            $sample .= self::generate( $part['part'], $isCaseInsensitive );
        }
        
        elseif ( self::T_SEQUENCE === $type )
        {
            $i = 0;
            $l = count($part['part']);
            $p = $part['part'][$i];
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                if ( !$p ) continue;
                $repeat = 1;
                if ( self::T_QUANTIFIER === $p['type'] )
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
                else if ( self::T_SPECIAL === $p['type'] )
                {
                    if ( isset($p['flags']['MatchAnyChar']) && $p['flags']['MatchAnyChar'] ) $sample .= self::any( );
                }
                else
                {
                    $sample .= self::generate( $p, $isCaseInsensitive );
                }
            }
        }
        
        elseif ( self::T_CHARGROUP === $type )
        {
            $chars = array();
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                $ptype = $p['type'];
                if ( self::T_CHARS === $ptype )
                {
                    if ( $isCaseInsensitive )
                        $chars = array_merge($chars, self::case_insensitive( $p['part'], true ) );
                    else
                        $chars = array_merge($chars, $p['part'] );
                }
                
                elseif ( self::T_CHARRANGE === $ptype )
                {
                    if ( $isCaseInsensitive )
                        $chars = array_merge($chars, self::case_insensitive( self::character_range($p['part']), true ) );
                    else
                        $chars = array_merge($chars, self::character_range($p['part']) );
                }
                
                elseif ( self::T_UNICODECHAR === $ptype || self::T_HEXCHAR === $ptype )
                {
                    $chars[] = $isCaseInsensitive ? self::case_insensitive( $p['flags']['Char'] ): $p['flags']['Char'];
                }
                
                elseif ( self::T_SPECIAL === $ptype )
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
        
        elseif ( self::T_STRING === $type )
        {
            $sample .= $isCaseInsensitive ? self::case_insensitive( $part['part'] ) : $part['part'];
        }
        
        elseif ( self::T_SPECIAL === $type && 
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
                
        elseif ( self::T_UNICODECHAR === $type || self::T_HEXCHAR === $type )
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
        if ( self::T_ALTERNATION === $type )
        {
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $tmp = self::peek_characters( $part['part'][$i] );
                $peek = self::concat( $peek, $tmp['peek'] );
                $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
            }
        }
        
        elseif ( self::T_GROUP === $type )
        {
            $tmp = self::peek_characters( $part['part'] );
            $peek = self::concat( $peek, $tmp['peek'] );
            $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
        }
        
        elseif ( self::T_SEQUENCE === $type )
        {
            $i = 0;
            $l = count($part['part']);
            $p = $part['part'][$i];
            $done = ( 
                $i >= $l || !$p || self::T_QUANTIFIER !== $p['type'] || 
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
                    $i >= $l || !$p || self::T_QUANTIFIER !== $p['type'] || 
                    ( !isset($p['flags']['MatchZeroOrMore']) && !isset($p['flags']['MatchZeroOrOne']) && (!isset($p['flags']['MatchMinimum']) || "0"!=$p['flags']['MatchMinimum']) ) 
                );
            }
            if ( $i < $l )
            {
                $p = $part['part'][$i];
                
                if (self::T_SPECIAL === $p['type'] && ('^'==$p['part'] || '$'==$p['part'])) 
                    $p = isset($part['part'][$i+1]) ? $part['part'][$i+1] : null;
                
                if ($p && self::T_QUANTIFIER === $p['type']) $p = $p['part'];
                
                if ($p)
                {
                    $tmp = self::peek_characters( $p );
                    $peek = self::concat( $peek, $tmp['peek'] );
                    $negativepeek = self::concat( $negativepeek, $tmp['negativepeek'] );
                }
            }
        }
        
        elseif ( self::T_CHARGROUP === $type )
        {
            $isNegative = isset($part['flags']['NotMatch']) && $part['flags']['NotMatch'];
            $current = array();
            
            $l = count($part['part']);
            for ($i=0; $i<$l; $i++)
            {
                $p = $part['part'][$i];
                $ptype = $p['type'];
                if ( self::T_CHARS === $ptype )
                {
                    $current = self::concat( $current, $p['part'] );
                }
                
                elseif ( self::T_CHARRANGE === $ptype )
                {
                    $current = self::concat( $current, self::character_range($p['part']) );
                }
                
                elseif ( self::T_UNICODECHAR === $ptype || self::T_HEXCHAR === $ptype )
                {
                    $current[$p['flags']['Char']] = 1;
                }
                
                elseif ( self::T_SPECIAL === $ptype )
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
        
        elseif ( self::T_STRING === $type )
        {
            $peek[$part['part'][0]] = 1;
        }
        
        elseif ( self::T_SPECIAL === $type && 
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
                
        elseif ( self::T_UNICODECHAR === $type || self::T_HEXCHAR === $type )
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
    private static function chargroup( &$re_obj ) 
    {
        
        $sequence = array(); 
        $chars = array(); 
        $flags = array(); 
        $isRange = false; 
        $escaped = false;
        $ch = '';
        
        if ( '^' == $re_obj->re[ $re_obj->pos ] )
        {
            $flags[ "NotMatch" ] = 1;
            $re_obj->pos++;
        }
        $lre = $re_obj->len;
        while ( $re_obj->pos < $lre )
        {
            $isUnicode = false;
            $prevch = $ch;
            $ch = $re_obj->re[ $re_obj->pos++ ];
            
            $escaped = (self::$escapeChar == $ch) ? true : false;
            if ( $re_obj->pos < $lre && $escaped )  $ch = $re_obj->re[ $re_obj->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' == $ch )
                {
                    $m = self::match_unicode(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $ch = chr(intval($m[1], 16));
                    $isUnicode = true;
                }
                
                // hex character
                else if ( 'x' == $ch )
                {
                    $m = self::match_hex(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $ch = chr(intval($m[1], 16));
                    $isUnicode = true;
                }
            }
            
            if ( $isRange )
            {
                if ( count($chars) )
                {
                    $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'typeName'=> "Chars", 'type'=> self::T_CHARS );
                    $chars = array();
                }
                $range[1] = $ch;
                $isRange = false;
                $sequence[] = array( 'part'=> $range, 'flags'=> array(), 'typeName'=> "CharRange", 'type'=> self::T_CHARRANGE );
            }
            else
            {
                if ( $escaped )
                {
                    if ( !$isUnicode && isset(self::$specialCharsEscaped[$ch]) && '/' != $ch)
                    {
                        if ( count($chars) )
                        {
                            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'typeName'=> "Chars", 'type'=> self::T_CHARS );
                            $chars = array();
                        }
                        $flag = array();
                        $flag[ self::$specialCharsEscaped[$ch] ] = 1;
                        $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'typeName'=> "Special", 'type'=> self::T_SPECIAL );
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
                            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'typeName'=> "Chars", 'type'=> self::T_CHARS );
                            $chars = array();
                        }
                        return array( 'part'=> $sequence, 'flags'=> $flags, 'typeName'=> "CharGroup", 'type'=> self::T_CHARGROUP );
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
            $sequence[] = array( 'part'=> $chars, 'flags'=> array(), 'typeName'=> "Chars", 'type'=> self::T_CHARS );
            $chars = array();
        }
        return array( 'part'=> $sequence, 'flags'=> $flags, 'typeName'=> "CharGroup", 'type'=> self::T_CHARGROUP );
    }
    private static function analyze_re( &$re_obj ) 
    {
        $word = ''; $wordlen = 0;
        $alternation = array(); 
        $sequence = array(); 
        $flags = array();
        $escaped = false;
        
        if ( $re_obj->inGroup > 0 )
        {
            $pre = substr($re_obj->re, $re_obj->pos, 2);
            
            if ( "?:" == $pre )
            {
                $flags[ "NotCaptured" ] = 1;
                $re_obj->pos += 2;
            }
            
            else if ( "?=" == $pre )
            {
                $flags[ "LookAhead" ] = 1;
                $re_obj->pos += 2;
            }
            
            else if ( "?!" == $pre )
            {
                $flags[ "NegativeLookAhead" ] = 1;
                $re_obj->pos += 2;
            }
            
            $flags[ "GroupIndex" ] = ++$re_obj->groupIndex;
        }
        $lre = $re_obj->len;
        while ( $re_obj->pos < $lre )
        {
            $ch = $re_obj->re[ $re_obj->pos++ ];
            
            //   \\abc
            $escaped = (self::$escapeChar == $ch) ? true : false;
            if ( $re_obj->pos < $lre && $escaped )  $ch = $re_obj->re[ $re_obj->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $m = self::match_unicode(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $sequence[] = array( 'part'=> $m[0], 'flags'=> array( "Char"=> chr(intval($m[1], 16)), "Code"=> $m[1] ), 'typeName'=> "UnicodeChar", 'type'=> self::T_UNICODECHAR );
                }
                
                // hex character
                else if ( 'x' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $m = self::match_hex(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $sequence[] = array( 'part'=> $m[0], 'flags'=> array( "Char"=> chr(intval($m[1], 16)), "Code"=> $m[1] ), 'typeName'=> "HexChar", 'type'=> self::T_HEXCHAR );
                }
                
                else if ( isset(self::$specialCharsEscaped[$ch]) && '/' != $ch)
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $flag = array();
                    $flag[ self::$specialCharsEscaped[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'typeName'=> "Special", 'type'=> self::T_SPECIAL );
                }
                
                else
                {
                    $word .= $ch;
                    $wordlen += 1;
                }
            }
            
            else
            {
                // group end
                if ( $re_obj->inGroup > 0 && ')' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    if ( count($alternation) )
                    {
                        $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'typeName'=> "Sequence", 'type'=> self::T_SEQUENCE );
                        $sequence = array();
                        $flag = array();
                        $flag[ self::$specialChars['|'] ] = 1;
                        return array( 'part'=> array( 'part'=> $alternation, 'flags'=> $flag, 'typeName'=> "Alternation", 'type'=> self::T_ALTERNATION ), 'flags'=> $flags, 'typeName'=> "Group", 'type'=> self::T_GROUP );
                    }
                    else
                    {
                        return array( 'part'=> array( 'part'=> $sequence, 'flags'=> array(), 'typeName'=> "Sequence", 'type'=> self::T_SEQUENCE ), 'flags'=> $flags, 'typeName'=> "Group", 'type'=> self::T_GROUP );
                    }
                }
                
                // parse alternation
                elseif ( '|' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'typeName'=> "Sequence", 'type'=> self::T_SEQUENCE );
                    $sequence = array();
                }
                
                // parse character group
                else if ( '[' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $sequence[] = self::chargroup( $re_obj );
                }
                
                // parse sub-group
                else if ( '(' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $re_obj->inGroup+=1;
                    $sequence[] = self::analyze_re( $re_obj );
                    $re_obj->inGroup-=1;
                }
                
                // parse num repeats
                else if ( '{' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $m = self::match_repeats(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $flag = array( 'part'=> $m[0], "MatchMinimum"=> $m[1], "MatchMaximum"=> isset($m[2]) ? $m[2] : "unlimited" );
                    $flag[ self::$specialChars[$ch] ] = 1;
                    if ( $re_obj->pos < $lre && '?' == $re_obj->re[$re_obj->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $re_obj->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( self::T_STRING === $prev['type'] && strlen($prev['part']) > 1 )
                    {
                        $sequence[] = array( 'part'=> substr($prev['part'], 0, -1), 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $prev['part'] = substr($prev['part'], -1);
                    }
                    $sequence[] = array( 'part'=> $prev, 'flags'=> $flag, 'typeName'=> "Quantifier", 'type'=> self::T_QUANTIFIER );
                }
                
                // quantifiers
                else if ( '*' == $ch || '+' == $ch || '?' == $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $flag = array();
                    $flag[ self::$specialChars[$ch] ] = 1;
                    if ( $re_obj->pos < $lre && '?' == $re_obj->re[$re_obj->pos] )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $re_obj->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( self::T_STRING === $prev['type'] && strlen($prev['part']) > 1 )
                    {
                        $sequence[] = array( 'part'=> substr($prev['part'], 0, -1), 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $prev['part'] = substr($prev['part'], -1);
                    }
                    $sequence[] = array( 'part'=> $prev, 'flags'=> $flag, 'typeName'=> "Quantifier", 'type'=> self::T_QUANTIFIER );
                }
            
                // special characters like ^, $, ., etc..
                else if ( isset(self::$specialChars[$ch]) )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
                        $word = '';
                        $wordlen = 0;
                    }
                    $flag = array();
                    $flag[ self::$specialChars[$ch] ] = 1;
                    $sequence[] = array( 'part'=> $ch, 'flags'=> $flag, 'typeName'=> "Special", 'type'=> self::T_SPECIAL );
                }
            
                else
                {
                    $word .= $ch;
                    $wordlen += 1;
                }
            }
        }
        
        if ( $wordlen )
        {
            $sequence[] = array( 'part'=> $word, 'flags'=> array(), 'typeName'=> "String", 'type'=> self::T_STRING );
            $word = '';
            $wordlen = 0;
        }
        
        if ( count($alternation) )
        {
            $alternation[] = array( 'part'=> $sequence, 'flags'=> array(), 'typeName'=> "Sequence", 'type'=> self::T_SEQUENCE );
            $sequence = array();
            $flag = array();
            $flag[ self::$specialChars['|'] ] = 1;
            return array( 'part'=> $alternation, 'flags'=> $flag, 'typeName'=> "Alternation", 'type'=> self::T_ALTERNATION );
        }
        return array( 'part'=> $sequence, 'flags'=> array(), 'typeName'=> "Sequence", 'type'=> self::T_SEQUENCE );
    }
    
    
    // A simple (js-flavored) regular expression analyzer
    public $_regex = null;
    public $_flags = null;
    public $_parts = null;
    public $_needsRefresh = false;
    
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
        
    public function regex($regex, $delim=null) 
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
    
    public function getRegex( ) 
    {
        return '/' . str_replace('/', '\\/', $this->_regex) . '/' . implode("", array_keys($this->_flags));
    }
    
    public function getParts( ) 
    {
        if ( $this->_needsRefresh ) $this->analyze( );
        return $this->_parts;
    }
    
    public function analyze( ) 
    {
        if ( $this->_needsRefresh )
        {
            $re_obj = (object)array(
                're'=>          $this->_regex,
                'len'=>         strlen($this->_regex),
                'pos'=>         0,
                'groupIndex'=>  0,
                'inGroup'=>     0
            );
            $this->_parts = self::analyze_re( $re_obj );
            $this->_needsRefresh = false;
        }
        return $this;
    }
    
    // experimental feature
    public function sample( ) 
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
    public function peek( ) 
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