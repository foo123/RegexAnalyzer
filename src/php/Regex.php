<?php
/**
*
*   Regex
*   @version: 1.0.0
*
*   A simple & generic Regular Expression Analyzer & Composer for PHP, Python, Node/XPCOM/JS, Java, C/C++, ActionScript
*   https://github.com/foo123/RegexAnalyzer
*
**/
if ( !class_exists('Regex') )
{
class RE_OBJ
{ 
    public $re = null;
    public $len = null;
    public $pos = 0;
    public $index = 0;
    public $groupIndex = 0;
    public $group = null;
    public $inGroup = 0;
    public function __construct( $re ) 
    {
        $this->re = $re;
        $this->len = strlen($re);
        $this->pos = 0;
        $this->index = 0;
        $this->groupIndex = 0;
        $this->group = array();
        $this->inGroup = 0;
    }
    public function dispose( ) 
    {
        $this->re = null;
        $this->len = null;
        $this->pos = null;
        $this->index = null;
        $this->groupIndex = null;
        $this->group = null;
        $this->inGroup = null;
    }
    public function __destruct( ) 
    {
        $this->dispose();
    }
}

class RegexNode
{
    public static function toObjectStatic( $v )
    {
        if ($v instanceof RegexNode)
        {
            $fl = (array)$v->flags;
            return !empty($fl) ? array(
                'type'=> $v->typeName,
                'value'=> self::toObjectStatic($v->val),
                'flags'=> $v->flags
            ) : array(
                'type'=> $v->typeName,
                'value'=> self::toObjectStatic($v->val)
            ); 
        }
        elseif ( is_array($v) )
        {
            return array_map(array(__CLASS__,'toObjectStatic'), $v);
        }
        return $v;
    }
    
    public $type = null;
    public $typeName = null;
    public $val = null;
    public $flags = null;
    
    public function __construct( $type, $value, $flags=null )
    {
        $this->type = $type;
        $this->val = $value;
        if ( $flags ) $this->flags = $flags;
        else $this->flags = array();
        $this->flags = (object)$this->flags;
        switch($type)
        {
            case Regex::T_SEQUENCE: 
                $this->typeName = "Sequence"; break;
            case Regex::T_ALTERNATION: 
                $this->typeName = "Alternation"; break;
            case Regex::T_GROUP: 
                $this->typeName = "Group"; break;
            case Regex::T_CHARGROUP: 
                $this->typeName = "CharacterGroup"; break;
            case Regex::T_CHARS: 
                $this->typeName = "Characters"; break;
            case Regex::T_CHARRANGE: 
                $this->typeName = "CharacterRange"; break;
            case Regex::T_STRING: 
                $this->typeName = "String"; break;
            case Regex::T_QUANTIFIER: 
                $this->typeName = "Quantifier"; break;
            case Regex::T_UNICODECHAR: 
                $this->typeName = "UnicodeChar"; break;
            case Regex::T_HEXCHAR: 
                $this->typeName = "HexChar"; break;
            case Regex::T_SPECIAL: 
                $this->typeName = "Special"; break;
            case Regex::T_COMMENT: 
                $this->typeName = "Comment"; break;
            default: 
                $this->typeName = "unspecified"; break;
        }
    }
    
    public function dispose( ) 
    {
        $this->val = null;
        $this->flags = null;
        $this->type = null;
        $this->typeName = null;
        return $this;
    }
    
    public function toObject( ) 
    {
        return self::toObjectStatic($this);
    }
}

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
// https://docs.python.org/3/library/re.html
// http://php.net/manual/en/reference.pcre.pattern.syntax.php
class RegexAnalyzer
{
    const VERSION = "1.0.0";
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
    
    private static function walk( $ret, &$node, &$state )
    {
        if ( (null===$node) || empty($state) ) return $ret;
        
        $type = $node instanceof RegexNode ? $node->type : null;
        
        // walk the tree
        if ( null === $type )
        {
            // custom, let reduce handle it
            $ret = call_user_func( $state->reduce, $ret, $node, $state );
        }
        
        elseif ( $state->IGNORE & $type )
        {
            /* nothing */
        }
        
        elseif ( $state->MAP & $type )
        {
            $r = call_user_func( $state->map, $ret, $node, $state );
            if ( isset($state->ret) )
            {
                $ret = call_user_func( $state->reduce, $ret, $node, $state );
                $state->ret = null;
            }
            elseif ( null != $r )
            {
                $r = Regex::to_array($r);
                for($i=0,$l=empty($r)?0:count($r); $i<$l; $i++)
                {
                    $state->node = $node;
                    $ret = self::walk( $ret, $r[$i], $state );
                    if ( isset($state->stop) )
                    {
                        $state->stop = null;
                        return $ret;
                    }
                }
            }
        }
        
        elseif ( $state->REDUCE & $type )
        {
            $ret = call_user_func( $state->reduce, $ret, $node, $state );
        }
        
        $state->node = null;
        return $ret;
    }
    
    private static function map_src( $ret, &$node, &$state )
    {
        $type = $node->type;
        if ( Regex::T_ALTERNATION === $type )
        {
            $r = array();
            for($i=0,$l=count($node->val)-1; $i<$l; $i++) {$r[] = $node->val[$i]; $r[] = '|';}
            $r[] = $node->val[$l];
            return $r;
        }
        elseif ( Regex::T_CHARGROUP === $type )
        {
            return array_merge(array('['.(!empty($node->flags->NegativeMatch)?'^':'')), Regex::to_array($node->val), array(']'));
        }
        elseif ( Regex::T_QUANTIFIER === $type )
        {
            $q = '';
            if ( !empty($node->flags->MatchZeroOrOne) ) $q = '?';
            elseif ( !empty($node->flags->MatchZeroOrMore) ) $q = '*';
            elseif ( !empty($node->flags->MatchOneOrMore) ) $q = '+';
            else $q = $node->flags->min === $node->flags->max ? ('{'.$node->flags->min.'}') : ('{'.$node->flags->min.','.(-1===$node->flags->max?'':$node->flags->max).'}');
            if ( ($node->flags->min !== $node->flags->max) && !$node->flags->isGreedy ) $q .= '?';
            return array_merge(Regex::to_array($node->val), array($q));
        }
        elseif ( Regex::T_GROUP === $type )
        {
            $g = null;
            if ( !empty($node->flags->NotCaptured) )
            {
                $g = array_merge(array('(?:'), Regex::to_array($node->val), array(')'));
            }
            elseif ( !empty($node->flags->LookAhead) )
            {
                $g = array_merge(array('(?='), Regex::to_array($node->val), array(')'));
            }
            elseif ( !empty($node->flags->NegativeLookAhead) )
            {
                $g = array_merge(array('(?!'), Regex::to_array($node->val), array(')'));
            }
            elseif ( !empty($node->flags->LookBehind) )
            {
                $g = array_merge(array('(?<='), Regex::to_array($node->val), array(')'));
            }
            elseif ( !empty($node->flags->NegativeLookBehind) )
            {
                $g = array_merge(array('(?<!'), Regex::to_array($node->val), array(')'));
            }
            else
            {
                $g = array_merge(array('('), Regex::to_array($node->val), array(')'));
            }
            if ( isset($node->flags->GroupIndex) )
            {
                $ret->group[$node->flags->GroupIndex] = $node->flags->GroupIndex;
                if ( isset($node->flags->GroupName) ) $ret->group[$node->flags->GroupName] = $node->flags->GroupIndex;
            }
            return $g;
        }
        return $node->val;
    }
    
    private static function map_any( $ret, &$node, &$state )
    {
        $type = $node->type;
        if ( (Regex::T_ALTERNATION === $type) || (Regex::T_CHARGROUP === $type) )
        {
            return !empty($node->val) ? $node->val[rand(0, count($node->val)-1)] : null;
        }
        elseif ( Regex::T_QUANTIFIER === $type )
        {
            $numrepeats = 0;
            if ( strlen($ret) >= $state->maxLength )
            {
                $numrepeats = $node->flags->min;
            }
            else
            {
                $mmin = $node->flags->min;
                $mmax = -1===$node->flags->max ? ($mmin+1+2*$state->maxLength) : $node->flags->max;
                $numrepeats = rand($mmin, $mmax);
            }
            if ( $numrepeats )
            {
                $repeats = array();
                for($i=0; $i<$numrepeats; $i++) $repeats[] = $node->val;
                return $repeats;
            }
            else
            {
                return null;
            }
        }
        elseif ( (Regex::T_GROUP === $type) && isset($node->flags->GroupIndex) )
        {
            $sample = self::walk('', $node->val, $state);
            $state->group[$node->flags->GroupIndex] = $sample;
            $state->ret = $sample;
            return null;
        }
        else
        {
            return $node->val;
        }
    }
    
    private static function map_min( $ret, &$node, &$state )
    {
        $type = $node->type;
        if ( Regex::T_ALTERNATION === $type )
        {
            $l = count($node->val);
            $min = $l ? self::walk(0, $node->val[0], $state) : 0;
            for($i=1; $i<$l; $i++)
            {
                $cur = self::walk(0, $node->val[$i], $state);
                if ( $cur < $min ) $min = $cur;
            }
            if ( $l ) $state->ret = $min;
            return null;
        }
        elseif ( Regex::T_CHARGROUP === $type )
        {
            return !empty($node->val) ? $node->val[0] : null;
        }
        elseif ( Regex::T_QUANTIFIER === $type )
        {
            if ( 0 === $node->flags->min ) return null;
            $nrepeats = $node->flags->min;
            $repeats = array();
            for($i=0; $i<$nrepeats; $i++) $repeats[] = $node->val;
            return $repeats;
        }
        elseif ( (Regex::T_GROUP === $type) && isset($node->flags->GroupIndex) )
        {
            $min = self::walk(0, $node->val, $state);
            $state->group[$node->flags->GroupIndex] = $min;
            $state->ret = $min;
            return null;
        }
        else
        {
            return $node->val;
        }
    }
    
    private static function map_max( $ret, &$node, &$state )
    {
        $type = $node->type;
        if ( Regex::T_ALTERNATION === $type )
        {
            $l = count($node->val);
            $max = $l ? self::walk(0, $node->val[0], $state) : 0;
            if ( -1 !== $max )
            {
                for($i=1; $i<$l; $i++)
                {
                    $cur = self::walk(0, $node->val[i], $state);
                    if ( -1 === $cur )
                    {
                        $max = -1;
                        break;
                    }
                    else if ( $cur > $max )
                    {
                        $max = $cur;
                    }
                }
            }
            if ( $l ) $state->ret = $max;
            return null;
        }
        elseif ( Regex::T_CHARGROUP === $type )
        {
            return !empty($node->val) ? $node->val[0] : null;
        }
        elseif ( Regex::T_QUANTIFIER === $type )
        {
            $max = self::walk(0, $node->val, $state);
            if ( -1 === $max )
            {
                $state->ret = -1;
            }
            elseif ( 0 < $max )
            {
                if ( -1 === $node->flags->max )
                {
                    $state->ret = -1;
                }
                elseif ( 0 < $node->flags->max )
                {
                    $state->ret = $node->flags->max*$max;
                }
                else
                {
                    $state->ret = $max;
                }
            }
            return null;
        }
        elseif ( (Regex::T_GROUP === $type) && isset($node->flags->GroupIndex) )
        {
            $max = self::walk(0, $node->val, $state);
            $state->group[$node->flags->GroupIndex] = $max;
            $state->ret = $max;
            return null;
        }
        else
        {
            return $node->val;
        }
    }
    
    private static function map_1st( $ret, &$node, &$state )
    {
        $type = $node->type;
        if ( Regex::T_SEQUENCE === $type )
        {
            $seq = array();
            $l = count($node->val);
            for($i=0; $i<$l; $i++)
            {
                $n = $node->val[$i];
                $seq[] = $n;
                if ( (Regex::T_QUANTIFIER === $n->type) && (0 === $n->flags->min) )
                    continue;
                elseif ( (Regex::T_SPECIAL === $n->type) && (!empty($n->flags->MatchStart) || !empty($n->flags->MatchEnd)) )
                    continue;
                break;
            }
            return !empty($seq) ? $seq : null;
        }
        else
        {
            return $node->val;
        }
    }
    
    private static function reduce_len( $ret, &$node, &$state )
    {
        if ( isset($state->ret) )
        {
            if ( -1 === $state->ret ) $ret = -1;
            else $ret += $state->ret;
            return $ret;
        }
        if ( -1 === $ret ) return $ret;
        
        if ( is_int($node) )
        {
            $ret += $node;
            return $ret;
        }
        
        if ( Regex::T_SPECIAL === $node->type && isset($node->flags->MatchEnd) )
        {
            $state->stop = 1;
            return $ret;
        }
        $type = $node->type;
        if ( (Regex::T_CHARS === $type) || (Regex::T_CHARRANGE === $type) ||
            (Regex::T_UNICODECHAR === $type) || (Regex::T_HEXCHAR === $type) ||
            (Regex::T_SPECIAL === $type && !isset($node->flags->MatchStart) && !isset($node->flags->MatchEnd))
        )
        {
            $ret += isset($node->flags->BackReference) ? (isset($state->group[$node->val]) ? $state->group[$node->val] : 0) : 1;
        }
        elseif ( Regex::T_STRING === $type )
        {
            $ret += strlen($node->val);
        }
        
        return $ret;
    }
    
    private static function reduce_str( $ret, &$node, &$state )
    {
        if ( isset($state->ret) )
        {
            $ret .= $state->ret;
            return $ret;
        }
        
        if ( is_string($node) )
        {
            $ret .= $node;
            return $ret;
        }
        
        if ( (Regex::T_SPECIAL === $node->type) && isset($node->flags->MatchEnd) )
        {
            $state->stop = 1;
            return $ret;
        }
        $type = $node->type; $sample = null;
        
        if ( Regex::T_CHARS === $type )
        {
            $sample = $node->val;
        }
        elseif ( Regex::T_CHARRANGE === $type )
        {
            $range = array($node->val[0],$node->val[1]);
            if ( ($range[0] instanceof RegexNode) && (Regex::T_UNICODECHAR === $range[0]->type || Regex::T_HEXCHAR === $range[0]->type) ) $range[0] = $range[0]->flags->Char;
            if ( ($range[1] instanceof RegexNode) && (Regex::T_UNICODECHAR === $range[1]->type || Regex::T_HEXCHAR === $range[1]->type) ) $range[1] = $range[1]->flags->Char;
            $sample = self::character_range($range);
        }
        elseif ( (Regex::T_UNICODECHAR === $type) || (Regex::T_HEXCHAR === $type) )
        {
            $sample = array($node->flags->Char);
        }
        elseif ( (Regex::T_SPECIAL === $type) && !isset($node->flags->MatchStart) && !isset($node->flags->MatchEnd) )
        {
            $part = $node->val;
            if (isset($node->flags->BackReference))
            {
                $ret .= isset($state->group[$part]) ? $state->group[$part] : '';
                return $ret;
            }
            elseif ('D' === $part)
            {
                $sample = array(self::digit( false ));
            }
            elseif ('W' === $part)
            {
                $sample = array(self::word( false ));
            }
            elseif ('S' === $part)
            {
                $sample = array(self::space( false ));
            }
            elseif ('d' === $part)
            {
                $sample = array(self::digit( ));
            }
            elseif ('w' === $part)
            {
                $sample = array(self::word( ));
            }
            elseif ('s' === $part)
            {
                $sample = array(self::space( ));
            }
            elseif (('.' === $part) && !empty($node->flags->MatchAnyChar))
            {
                $sample = array(self::any( ));
            }
            else
            {
                $sample = array(Regex::ESC . $part);
            }
        }
        elseif ( Regex::T_STRING === $type )
        {
            $sample = $node->val;
        }
        
        if ( $sample )
        {
            $ret .= Regex::T_STRING === $type ?
            ($state->isCaseInsensitive ? self::case_insensitive($sample) : $sample) :
            (self::character($state->isCaseInsensitive ? self::case_insensitive($sample, true) : $sample, empty($state->node) || empty($state->node->flags->NegativeMatch)))
            ;
        }
        
        return $ret;
    }
    
    private static function reduce_src( $ret, &$node, &$state )
    {
        if ( isset($state->ret) )
        {
            if ( isset($state->ret->src) ) $ret->src .= $state->ret->src;
            if ( isset($state->ret->group) ) $ret->group = array_merge($ret->group, $state->ret->group);
            return $ret;
        }
        if ( is_string($node) )
        {
            $ret->src .= $node;
            return $ret;
        }
        
        $type = $node->type;
        if ( Regex::T_CHARS === $type )
        {
            $ret->src .= $state->escaped ? Regex::esc_re(implode('',$node->val), Regex::ESC, 1) : implode('',$node->val);
        }
        elseif ( Regex::T_CHARRANGE === $type )
        {
            $range = array($node->val[0],$node->val[1]);
            if ( $state->escaped )
            {
                if ( ($range[0] instanceof RegexNode) && (Regex::T_UNICODECHAR === $range[0]->type) ) $range[0] = Regex::ESC.'u'.Regex::pad($range[0]->flags->Code,4);
                elseif ( ($range[0] instanceof RegexNode) && (Regex::T_HEXCHAR === $range[0]->type) ) $range[0] = Regex::ESC.'x'.Regex::pad($range[0]->flags->Code,2);
                else $range[0] = Regex::esc_re($range[0], Regex::ESC, 1);
                if ( ($range[1] instanceof RegexNode) && (Regex::T_UNICODECHAR === $range[1]->type) ) $range[1] = Regex::ESC.'u'.Regex::pad($range[1]->flags->Code,4);
                elseif ( ($range[1] instanceof RegexNode) && (Regex::T_HEXCHAR === $range[1]->type) ) $range[1] = Regex::ESC.'x'.Regex::pad($range[1]->flags->Code,2);
                else $range[1] = Regex::esc_re($range[1], Regex::ESC, 1);
            }
            else
            {
                if ( ($range[0] instanceof RegexNode) && (Regex::T_UNICODECHAR === $range[0]->type || Regex::T_HEXCHAR === $range[0]->type) ) $range[0] = $range[0]->flags->Char;
                if ( ($range[1] instanceof RegexNode) && (Regex::T_UNICODECHAR === $range[1]->type || Regex::T_HEXCHAR === $range[1]->type) ) $range[1] = $range[1]->flags->Char;
            }
            $ret->src .= $range[0].'-'.$range[1];
        }
        elseif ( Regex::T_UNICODECHAR === $type )
        {
            $ret->src .= $state->escaped ? Regex::ESC.'u'.Regex::pad($node->flags->Code,4) : $node->flags->Char;
        }
        elseif ( Regex::T_HEXCHAR === $type )
        {
            $ret->src .= $state->escaped ? Regex::ESC.'x'.Regex::pad($node->flags->Code,2) : $node->flags->Char;
        }
        elseif ( Regex::T_SPECIAL === $type )
        {
            if ( !empty($node->flags->BackReference) )
            {
                $ret->src .= Regex::ESC.$node->val/*.'(?#)'*/;
            }
            else
            {
                $ret->src .= empty($node->flags->MatchStart) && empty($node->flags->MatchEnd) ? (Regex::ESC.$node->val) : (''.$node->val);
            }
        }
        elseif ( Regex::T_STRING === $type )
        {
            $ret->src .= $state->escaped ? Regex::esc_re($node->val, Regex::ESC) : $node->val;
        }
        
        return $ret;
    }
    
    private static function reduce_peek( $ret, &$node, &$state )
    {
        if ( isset($state->ret) )
        {
            $ret['positive'] = self::concat($ret['positive'], $state->ret['positive']);
            $ret['negative'] = self::concat($ret['negative'], $state->ret['negative']);
            return $ret;
        }
        if ( (Regex::T_SPECIAL === $node->type) && isset($node->flags->MatchEnd) )
        {
            $state->stop = 1;
            return $ret;
        }
        $type = $node->type;
        $inCharGroup = !empty($state->node) && (Regex::T_CHARGROUP === $state->node->type);
        $inNegativeCharGroup = $inCharGroup && !empty($state->node->flags->NegativeMatch);
        $peek = $inNegativeCharGroup ? "negative" : "positive";
        
        if ( Regex::T_CHARS === $type )
        {
            $ret[$peek] = self::concat( $ret[$peek], $node->val );
        }
        elseif ( Regex::T_CHARRANGE === $type )
        {
            $ret[$peek] = self::concat( $ret[$peek], self::character_range($node->val) );
        }
        elseif ( (Regex::T_UNICODECHAR === $type) || (Regex::T_HEXCHAR === $type) )
        {
            $ret[$peek][$node->flags->Char] = 1;
        }
        elseif ( (Regex::T_SPECIAL === $type) && !isset($node->flags->BackReference) && !isset($node->flags->MatchStart) && !isset($node->flags->MatchEnd) )
        {
            $part = $node->val;
            if ('D' === $part)
            {
                $ret[$inNegativeCharGroup?"positive":"negative"][ '\\d' ] = 1;
            }
            elseif ('W' === $part)
            {
                $ret[$inNegativeCharGroup?"positive":"negative"][ '\\w' ] = 1;
            }
            elseif ('S' === $part)
            {
                $ret[$inNegativeCharGroup?"positive":"negative"][ '\\s' ] = 1;
            }
            else
            {
                $ret[$peek][Regex::ESC . $part] = 1;
            }
        }
        elseif ( Regex::T_STRING === $type )
        {
            $ret["positive"][$node->val[0]] = 1;
        }
        
        return $ret;
    }
    
    private static function match_hex( $s ) 
    {
        $m = false;
        if ( (strlen($s) > 2) && ('x' === $s[0]) )
        {
            if ( self::match_char_ranges(self::$HEXDIGITS_RANGES, $s, 1, 2, 2) ) 
                return array($m=substr($s,0,3), substr($m,1));
        }
        return false;
    }
    private static function match_unicode( $s ) 
    {
        $m = false;
        if ( (strlen($s) > 4) && ('u' === $s[0]) )
        {
            if ( self::match_char_ranges(self::$HEXDIGITS_RANGES, $s, 1, 4, 4) ) 
                return array($m=substr($s,0,5), substr($m,1));
        }
        return false;
    }
    private static function match_repeats( $s ) 
    {
        $pos = 0; $m = false; $sl = strlen($s); $hasComma = false;
        if ( ($sl > 2) && ('{' === $s[$pos]) )
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
            if ( ($pos < $sl) && (',' === $s[$pos]) ) {$pos += 1; $hasComma = true;}
            if ( $l=self::match_chars(self::$SPACES, $s, $pos) ) $pos += $l;
            if ( $l=self::match_char_range(self::$DIGITS_RANGE, $s, $pos) ) 
            {
                $m[2] = substr($s, $pos, $l);
                $pos += $l;
            }
            if ( $l=self::match_chars(self::$SPACES, $s, $pos) ) $pos += $l;
            if ( ($pos < $sl) && ('}' === $s[$pos]) )
            {
                $pos++;
                $m[0] = substr($s, 0, $pos);
                if ( !$hasComma ) $m[2] = $m[1];
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
        $allchars = array(); 
        $flags = array(); 
        $isRange = false; 
        $escaped = false;
        $ch = '';
        
        if ( '^' === $re_obj->re[ $re_obj->pos ] )
        {
            $flags[ "NegativeMatch" ] = 1;
            $re_obj->pos++;
        }
        $lre = $re_obj->len;
        while ( $re_obj->pos < $lre )
        {
            $isUnicode = false;
            $isHex = false;
            $prevch = $ch;
            $ch = $re_obj->re[ $re_obj->pos++ ];
            
            $escaped = Regex::ESC === $ch;
            if ( $escaped && ($re_obj->pos < $lre) ) $ch = $re_obj->re[ $re_obj->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' === $ch )
                {
                    $m = self::match_unicode(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $ch = Regex::Node(Regex::T_UNICODECHAR, $m[0], array("Char"=> chr(intval($m[1], 16)), "Code"=> $m[1]));
                    $isUnicode = true; $isHex = false;
                }
                
                // hex character
                else if ( 'x' === $ch )
                {
                    $m = self::match_hex(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $ch = Regex::Node(Regex::T_HEXCHAR, $m[0], array("Char"=> chr(intval($m[1], 16)), "Code"=> $m[1]));
                    $isUnicode = true; $isHex = true;
                }
            }
            
            if ( $isRange )
            {
                if ( count($chars) )
                {
                    $allchars = array_merge($allchars, $chars);
                    $chars = array();
                }
                $range[1] = $ch;
                $isRange = false;
                $sequence[] = Regex::Node(Regex::T_CHARRANGE, $range);
            }
            else
            {
                if ( $escaped )
                {
                    if ( $isUnicode )
                    {
                        if ( count($chars) )
                        {
                            $allchars = array_merge($allchars, $chars);
                            $chars = array();
                        }
                        $sequence[] = $ch;
                    }
                    
                    elseif ( isset(Regex::$specialCharsEscaped[$ch]) && ('/' !== $ch))
                    {
                        if ( count($chars) )
                        {
                            $allchars = array_merge($allchars, $chars);
                            $chars = array();
                        }
                        $flag = array();
                        $flag[ Regex::$specialCharsEscaped[$ch] ] = 1;
                        $sequence[] = Regex::Node(Regex::T_SPECIAL, $ch, $flag);
                    }
                    
                    else
                    {
                        $chars[]  = $ch;
                    }
                }
                
                else
                {
                    // end of char group
                    if ( ']' === $ch )
                    {
                        if ( count($chars) )
                        {
                            $allchars = array_merge($allchars, $chars);
                            $chars = array();
                        }
                        // map all chars into one node
                        if ( count($allchars) ) $sequence[] = Regex::Node(Regex::T_CHARS, $allchars);
                        return Regex::Node(Regex::T_CHARGROUP, $sequence, $flags);
                    }
                    
                    else if ( '-' === $ch )
                    {
                        $range = array($prevch, '');
                        if ( $prevch instanceof RegexNode ) array_pop($sequence); else array_pop($chars);
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
            $allchars = array_merge($allchars, $chars);
            $chars = array();
        }
        // map all chars into one node
        if ( count($allchars) ) $sequence[] = Regex::Node(Regex::T_CHARS, $allchars);
        return Regex::Node(Regex::T_CHARGROUP, $sequence, $flags);
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
            $pre3 = substr($re_obj->re, $re_obj->pos, 3);
            $captured = 1;
            
            if ( "?P=" === $pre3 )
            {
                $flags[ "BackReference" ] = 1;
                $flags[ "GroupName" ] = '';
                $re_obj->pos += 3;
                $lre = $re_obj->len;
                while ( $re_obj->pos < $lre )
                {
                    $ch = $re_obj->re[ $re_obj->pos++ ];
                    if ( ")" === $ch ) break;
                    $flags[ "GroupName" ] .= $ch;
                }
                $flags[ "GroupIndex" ] = isset($re_obj->group[$flags[ "GroupName" ]]) ? $re_obj->group[$flags[ "GroupName" ]] : null;
                return Regex::Node(Regex::T_SPECIAL, (string)$flags[ "GroupIndex" ], $flags);
            }
            
            elseif ( "?#" === $pre )
            {
                $flags[ "Comment" ] = 1;
                $re_obj->pos += 2;
                $word = '';
                $lre = $re_obj->len;
                while ( $re_obj->pos < $lre )
                {
                    $ch = $re_obj->re[ $re_obj->pos++ ];
                    if ( ")" === $ch ) break;
                    $word .= $ch;
                }
                return Regex::Node(Regex::T_COMMENT, $word);
            }
            
            elseif ( "?:" === $pre )
            {
                $flags[ "NotCaptured" ] = 1;
                $re_obj->pos += 2;
                $captured = 0;
            }
            
            elseif ( "?=" === $pre )
            {
                $flags[ "LookAhead" ] = 1;
                $re_obj->pos += 2;
                $captured = 0;
            }
            
            elseif ( "?!" === $pre )
            {
                $flags[ "NegativeLookAhead" ] = 1;
                $re_obj->pos += 2;
                $captured = 0;
            }
            
            elseif ( "?<=" === $pre3 )
            {
                $flags[ "LookBehind" ] = 1;
                $re_obj->pos += 3;
                $captured = 0;
            }
            
            elseif ( "?<!" === $pre3 )
            {
                $flags[ "NegativeLookBehind" ] = 1;
                $re_obj->pos += 3;
                $captured = 0;
            }
            
            elseif ( ("?<" === $pre) || ("?P<" === $pre3) )
            {
                $flags[ "NamedGroup" ] = 1;
                $flags[ "GroupName" ] = '';
                $re_obj->pos += "?<" === $pre ? 2 : 3;
                $lre = $re_obj->len;
                while ( $re_obj->pos < $lre )
                {
                    $ch = $re_obj->re[ $re_obj->pos++ ];
                    if ( ">" === $ch ) break;
                    $flags[ "GroupName" ] .= $ch;
                }
            }
            
            ++$re_obj->index;
            if ( $captured )
            {
                ++$re_obj->groupIndex;
                $flags[ "GroupIndex" ] = $re_obj->groupIndex;
                $re_obj->group[''.(string)$flags[ "GroupIndex" ]] = $flags[ "GroupIndex" ];
                if ( isset($flags[ "GroupName" ]) ) $re_obj->group[$flags[ "GroupName" ]] = $flags[ "GroupIndex" ];
            }
        }
        $lre = $re_obj->len;
        while ( $re_obj->pos < $lre )
        {
            $ch = $re_obj->re[ $re_obj->pos++ ];
            
            //   \\abc
            $escaped = Regex::ESC === $ch;
            if ( $escaped && ($re_obj->pos < $lre) ) $ch = $re_obj->re[ $re_obj->pos++ ];
            
            if ( $escaped )
            {
                // unicode character
                if ( 'u' === $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $m = self::match_unicode(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $sequence[] = Regex::Node(Regex::T_UNICODECHAR, $m[0], array("Char"=> chr(intval($m[1], 16)), "Code"=> $m[1]));
                }
                
                // hex character
                else if ( 'x' === $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $m = self::match_hex(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $sequence[] = Regex::Node(Regex::T_HEXCHAR, $m[0], array("Char"=> chr(intval($m[1], 16)), "Code"=> $m[1]));
                }
                
                else if ( isset(Regex::$specialCharsEscaped[$ch]) && ('/' !== $ch) )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $flag = array();
                    $flag[ Regex::$specialCharsEscaped[$ch] ] = 1;
                    $sequence[] = Regex::Node(Regex::T_SPECIAL, $ch, $flag);
                }
                
                else if ( ('1' <= $ch) && ('9' >= $ch) )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $word = $ch;
                    while ($re_obj->pos < $lre)
                    {
                        $ch = $re_obj->re[$re_obj->pos];
                        if ( ('0' <= $ch) && ('9' >= $ch) ) { $word .= $ch; $re_obj->pos++; }
                        else break;
                    }
                    $flag = array();
                    $flag[ 'BackReference' ] = 1;
                    $flag[ 'GroupIndex' ] = intval($word, 10);
                    $sequence[] = Regex::Node(Regex::T_SPECIAL, $word, $flag);
                    $word = '';
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
                if ( ($re_obj->inGroup > 0) && (')' === $ch) )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    if ( count($alternation) )
                    {
                        $alternation[] = Regex::Node(Regex::T_SEQUENCE, $sequence);
                        $sequence = array();
                        $flag = array();
                        $flag[ Regex::$specialChars['|'] ] = 1;
                        return Regex::Node(Regex::T_GROUP, Regex::Node(Regex::T_ALTERNATION, $alternation, $flag), $flags);
                    }
                    else
                    {
                        return Regex::Node(Regex::T_GROUP, Regex::Node(Regex::T_SEQUENCE, $sequence), $flags);
                    }
                }
                
                // parse alternation
                elseif ( '|' === $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $alternation[] = Regex::Node(Regex::T_SEQUENCE, $sequence);
                    $sequence = array();
                }
                
                // parse character group
                else if ( '[' === $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $sequence[] = self::chargroup( $re_obj );
                }
                
                // parse sub-group
                else if ( '(' === $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $re_obj->inGroup+=1;
                    $sequence[] = self::analyze_re( $re_obj );
                    $re_obj->inGroup-=1;
                }
                
                // parse num repeats
                else if ( '{' === $ch )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $m = self::match_repeats(substr($re_obj->re, $re_obj->pos-1));
                    $re_obj->pos += strlen($m[0])-1;
                    $flag = array( 'val'=> $m[0], "MatchMinimum"=> $m[1], "MatchMaximum"=> isset($m[2]) ? $m[2] : "unlimited", 'min'=> intval($m[1],10), 'max'=> isset($m[2]) ? intval($m[2],10) : -1 );
                    $flag[ Regex::$specialChars[$ch] ] = 1;
                    if ( ($re_obj->pos < $lre) && ('?' === $re_obj->re[$re_obj->pos]) )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $re_obj->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( (Regex::T_STRING === $prev->type) && (strlen($prev->val) > 1) )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, substr($prev->val, 0, -1));
                        $prev->val = substr($prev->val, -1);
                    }
                    $sequence[] = Regex::Node(Regex::T_QUANTIFIER, $prev, $flag);
                }
                
                // quantifiers
                elseif ( ('*' === $ch) || ('+' === $ch) || ('?' === $ch) )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $flag = array();
                    $flag[ Regex::$specialChars[$ch] ] = 1;
                    $flag["min"] = '+' === $ch ? 1 : 0;
                    $flag["max"] = '?' === $ch ? 1 : -1;
                    if ( ($re_obj->pos < $lre) && ('?' === $re_obj->re[$re_obj->pos]) )
                    {
                        $flag[ "isGreedy" ] = 0;
                        $re_obj->pos++;
                    }
                    else
                    {
                        $flag[ "isGreedy" ] = 1;
                    }
                    $prev = array_pop($sequence);
                    if ( (Regex::T_STRING === $prev->type) && (strlen($prev->val) > 1) )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, substr($prev->val, 0, -1));
                        $prev->val = substr($prev->val, -1);
                    }
                    $sequence[] = Regex::Node(Regex::T_QUANTIFIER, $prev, $flag);
                }
            
                // special characters like ^, $, ., etc..
                elseif ( isset(Regex::$specialChars[$ch]) )
                {
                    if ( $wordlen )
                    {
                        $sequence[] = Regex::Node(Regex::T_STRING, $word);
                        $word = '';
                        $wordlen = 0;
                    }
                    $flag = array();
                    $flag[ Regex::$specialChars[$ch] ] = 1;
                    $sequence[] = Regex::Node(Regex::T_SPECIAL, $ch, $flag);
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
            $sequence[] = Regex::Node(Regex::T_STRING, $word);
            $word = '';
            $wordlen = 0;
        }
        
        if ( count($alternation) )
        {
            $alternation[] = Regex::Node(Regex::T_SEQUENCE, $sequence);
            $sequence = array();
            $flag = array();
            $flag[ Regex::$specialChars['|'] ] = 1;
            return Regex::Node(Regex::T_ALTERNATION, $alternation, $flag);
        }
        return Regex::Node(Regex::T_SEQUENCE, $sequence);
    }
    
    
    // A simple regular expression analyzer
    public $ast = null;
    public $re = null;
    public $fl = null;
    public $src = null;
    public $grp = null;
    public $min = null;
    public $max = null;
    public $ch = null;
    
    public function __construct( $re=null, $delim='/' )
    {
        if ( $re ) $this->input($re, $delim);
    }
    
    public function __destruct( )
    {
        $this->dispose();
    }
    
    public function dispose( ) 
    {
        $this->ast = null;
        $this->re = null;
        $this->fl = null;
        $this->src = null;
        $this->grp = null;
        $this->min = null;
        $this->max = null;
        $this->ch = null;
        return $this;
    }
        
    public function reset()
    {
        $this->ast = null;
        $this->src = null;
        $this->grp = null;
        $this->min = null;
        $this->max = null;
        $this->ch = null;
        return $this;
    }
    
    // alias
    public function set($re=null, $delim='/')
    {
        return $this->input($re, $delim);
    }
    
    public function input($re=null, $delim='/') 
    {
        if ( !func_num_args() ) return $this->re;
        if ( $re )
        {
            $delim = false === $delim ? false : (empty($delim) ? '/' : (string)$delim);
            $re = (string)$re;
            $fl = array();
            $l = strlen($re);
            
            if ( $delim )
            {
                // parse re flags, if any
                while ( 0 < $l )
                {
                    $ch = $re[$l-1];
                    if ( $delim === $ch ) break;
                    else { $fl[ $ch ] = 1; $l--; }
                }
                
                if ( 0 < $l )
                {
                    // remove re delimiters
                    if ( $delim === $re[0] && $delim === $re[$l-1] ) $re = substr($re, 1, $l-2);
                    else $re = substr($re, 0, $l);
                }
                else
                {
                    $re = '';
                }
            }
            
            // re is different, reset the ast, etc
            if ( $this->re !== $re ) $this->reset();
            $this->re = $re; $this->fl = $fl;
        }
        return $this;
    }
    
    public function analyze( ) 
    {
        if ( (null != $this->re) && (null === $this->ast) )
        {
            $re = new RE_OBJ($this->re);
            $this->ast = self::analyze_re( $re );
            $re->dispose();
        }
        return $this;
    }
    
    public function synthesize( $escaped=true )
    {
        if ( null == $this->re ) return $this;
        if ( null === $this->ast )
        {
            $this->analyze( );
            $this->src = null;
            $this->grp = null;
        }
        if ( null === $this->src )
        {
            $state = (object)array(
                'MAP'                 => Regex::T_SEQUENCE|Regex::T_ALTERNATION|Regex::T_GROUP|Regex::T_CHARGROUP|Regex::T_QUANTIFIER,
                'REDUCE'              => Regex::T_UNICODECHAR|Regex::T_HEXCHAR|Regex::T_SPECIAL|Regex::T_CHARS|Regex::T_CHARRANGE|Regex::T_STRING,
                'IGNORE'              => Regex::T_COMMENT,
                'map'                 => array(__CLASS__,'map_src'),
                'reduce'              => array(__CLASS__,'reduce_src'),
                'escaped'             => false !== $escaped,
                'group'               => array()
            );
            $re = self::walk((object)array('src'=>'','group'=>array()), $this->ast, $state);
            $this->src = $re->src; $this->grp = $re->group;
        }
        return $this;
    }
    
    public function source( )
    {
        if ( null == $this->re ) return null;
        if ( null === $this->src ) $this->synthesize();
        return $this->src;
    }
    
    public function groups( $raw=false )
    {
        if ( null == $this->re ) return null;
        if ( null === $this->grp ) $this->synthesize();
        return true===$raw ? $this->grp : /*array_merge(array(),*/$this->grp/*)*/;
    }
    
    public function compile( $flags=null ) 
    {
        if ( null == $this->re ) return null;
        $flags = empty($flags) ? (!empty($this->fl) ? $this->fl : array()): (array)$flags;
        return '/' . $this->source() . '/' . (!empty($flags['x'])?'x':'').(!empty($flags['X'])?'X':'').(!empty($flags['i'])||!empty($flags['I'])?'i':'').(!empty($flags['m'])||!empty($flags['M'])?'m':'').(!empty($flags['u'])?'u':'').(!empty($flags['U'])?'U':'').(!empty($flags['s'])?'s':'').(!empty($flags['S'])?'S':'');
    }
    
    public function tree( $flat=false ) 
    {
        if ( null == $this->re ) return null;
        if ( null === $this->ast ) $this->analyze( );
        return true === $flat ? $this->ast->toObject() : $this->ast;
    }
    
    // experimental feature
    public function sample( $maxlen=1, $numsamples=1 ) 
    {
        if ( null == $this->re ) return null;
        if ( null === $this->ast ) $this->analyze( );
        $state = (object)array(
            'MAP'               => Regex::T_SEQUENCE|Regex::T_ALTERNATION|Regex::T_GROUP|Regex::T_CHARGROUP|Regex::T_QUANTIFIER,
            'REDUCE'            => Regex::T_UNICODECHAR|Regex::T_HEXCHAR|Regex::T_SPECIAL|Regex::T_CHARS|Regex::T_CHARRANGE|Regex::T_STRING,
            'IGNORE'            => Regex::T_COMMENT,
            'map'               => array(__CLASS__, 'map_any'),
            'reduce'            => array(__CLASS__, 'reduce_str'),
            'maxLength'         => (int)$maxlen,
            'isCaseInsensitive' => !empty($this->fl['i']),
            'group'             => array()
        );
        $numsamples = (int)$numsamples;
        if ( 1 < $numsamples )
        {
            $samples = array_fill(0, $numsamples, null);
            for($i=0; $i<$numsamples; $i++) $samples[$i] = (string)self::walk('', $this->ast, $state);
            return $samples;
        }
        return (string)self::walk('', $this->ast, $state);
    }
    
    // experimental feature
    public function minimum( )
    {
        if ( null == $this->re ) return 0;
        if ( null === $this->ast )
        {
            $this->analyze( );
            $this->min = null;
        }
        if ( null === $this->min )
        {
            $state = (object)array(
                'MAP'               => Regex::T_SEQUENCE|Regex::T_ALTERNATION|Regex::T_GROUP|Regex::T_CHARGROUP|Regex::T_QUANTIFIER,
                'REDUCE'            => Regex::T_UNICODECHAR|Regex::T_HEXCHAR|Regex::T_SPECIAL|Regex::T_CHARS|Regex::T_CHARRANGE|Regex::T_STRING,
                'IGNORE'            => Regex::T_COMMENT,
                'map'               => array(__CLASS__, 'map_min'),
                'reduce'            => array(__CLASS__, 'reduce_len'),
                'group'             => array()
            );
            $this->min = (int)self::walk(0, $this->ast, $state);
        }
        return $this->min;
    }
    
    // experimental feature
    public function maximum( )
    {
        if ( null == $this->re ) return 0;
        if ( null === $this->ast )
        {
            $this->analyze( );
            $this->max = null;
        }
        if ( null === $this->max )
        {
            $state = (object)array(
                'MAP'               => Regex::T_SEQUENCE|Regex::T_ALTERNATION|Regex::T_GROUP|Regex::T_CHARGROUP|Regex::T_QUANTIFIER,
                'REDUCE'            => Regex::T_UNICODECHAR|Regex::T_HEXCHAR|Regex::T_SPECIAL|Regex::T_CHARS|Regex::T_CHARRANGE|Regex::T_STRING,
                'IGNORE'            => Regex::T_COMMENT,
                'map'               => array(__CLASS__, 'map_max'),
                'reduce'            => array(__CLASS__, 'reduce_len'),
                'group'             => array()
            );
            $this->max = self::walk(0, $this->ast, $state);
        }
        return $this->max;
    }
    
    // experimental feature
    public function peek( ) 
    {
        if ( null == $this->re ) return null;
        if ( null === $this->ast )
        {
            $this->analyze( );
            $this->ch = null;
        }
        if ( null === $this->ch )
        {
            $state = (object)array(
                'MAP'               => Regex::T_SEQUENCE|Regex::T_ALTERNATION|Regex::T_GROUP|Regex::T_CHARGROUP|Regex::T_QUANTIFIER,
                'REDUCE'            => Regex::T_UNICODECHAR|Regex::T_HEXCHAR|Regex::T_SPECIAL|Regex::T_CHARS|Regex::T_CHARRANGE|Regex::T_STRING,
                'IGNORE'            => Regex::T_COMMENT,
                'map'               => array(__CLASS__, 'map_1st'),
                'reduce'            => array(__CLASS__, 'reduce_peek'),
                'group'             => array()
            );
            $this->ch = self::walk(array('positive'=>array(),'negative'=>array()), $this->ast, $state);
        }
        $peek = array('positive'=>array_merge(array(),$this->ch['positive']), 'negative'=>array_merge(array(),$this->ch['negative']));
        $isCaseInsensitive = !empty($this->fl['i']);
        foreach ($peek as $n=>$p)
        {
            $cases = array();
            
            // either positive or negative
            foreach (array_keys($p) as $c)
            {
                if ('\\d' === $c)
                {
                    unset( $p[$c] );
                    $cases = self::concat($cases, self::character_range('0', '9'));
                }
                
                else if ('\\s' === $c)
                {
                    unset( $p[$c] );
                    $cases = self::concat($cases, array('\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029'));
                }
                
                else if ('\\w' === $c)
                {
                    unset( $p[$c] );
                    $cases = self::concat($cases, array_merge(
                            array('_'), 
                            self::character_range('0', '9'), 
                            self::character_range('a', 'z'), 
                            self::character_range('A', 'Z') 
                        ));
                }
                
                else if ('\\.' === $c)
                {
                    unset( $p[$c] );
                    $cases[ $this->specialChars['.'] ] = 1;
                }
                
                /*else if ('\\^' === $c)
                {
                    unset( $p[$c] );
                    $cases[ $this->specialChars['^'] ] = 1;
                }
                
                else if ('\\$' === $c)
                {
                    unset( $p[$c] );
                    $cases[ $this->specialChars['$'] ] = 1;
                }*/
                
                else if ( (Regex::ESC !== $c[0]) && $isCaseInsensitive )
                {
                    $cases[ strtolower($c) ] = 1;
                    $cases[ strtoupper($c) ] = 1;
                }
                
                else if ( Regex::ESC === $c[0] )
                {
                    unset( $p[$c] );
                }
            }
            $peek[$n] = self::concat($p, $cases);
        }
        return $peek;
    }
}
class RegexComposer
{
    
    const VERSION = "1.0.0";
    
    public $re = null;
    private $g = 0;
    private $grp = null;
    private $level = 0;
    private $ast = null;
    
    public function __construct( ) 
    {
        $this->re = null;
        $this->reset();
    }
    
    public function __destruct( ) 
    {
        $this->dispose();
    }
    
    public function dispose( )
    {
        $this->re = null;
        $this->g = null;
        $this->grp = null;
        $this->level = null;
        $this->ast = null;
        return $this;
    }
    
    public function reset( )
    {
        $this->g = 0;
        $this->grp = array();
        $this->level = 0;
        $this->ast = array((object)array('node'=> array(), 'type'=> Regex::T_SEQUENCE, 'flag'=> ''));
        return $this;
    }

    public function compose( /* flags */ )
    {
        $fl = implode('', func_get_args());
        $src = implode('', $this->ast[0]->node);
        $this->re = (object)array(
            'source'  => $src,
            'flags'   => $fl,
            'groups'  => $this->grp,
            'pattern' => '/'.$src.'/'.$fl
        );
        $this->reset( );
        return $this->re;
    }

    public function partial( $reset=true )
    {
        $re = implode('', $this->ast[0]->node);
        if ( false !== $reset ) $this->reset( );
        return $re;
    }

    public function token( $token, $escaped=false )
    {
        if ( null != $token )
            $this->ast[$this->level]->node[] = true===$escaped ? Regex::esc_re((string)$token, Regex::ESC) : (string)$token;
        return $this;
    }
    
    public function match( $token, $escaped=false )
    {
        return $this->token( (string)$token, $escaped );
    }
    
    public function literal( $literal )
    {
        return $this->token( (string)$literal, true );
    }
    
    public function regexp( $re )
    {
        return $this->token( (string)$re, false );
    }
    
    public function sub( $re )
    {
        return $this->regexp( $re );
    }
    
    public function SOL( )
    {
        $this->ast[$this->level]->node[] = '^';
        return $this;
    }
    
    public function SOF( )
    {
        return $this->SOL( );
    }
    
    public function EOL( )
    {
        $this->ast[$this->level]->node[] = '$';
        return $this;
    }
    
    public function EOF( )
    {
        return $this->EOL( );
    }
    
    public function LF( )
    {
        $this->ast[$this->level]->node[] = Regex::ESC.'n';
        return $this;
    }
    
    public function CR( )
    {
        $this->ast[$this->level]->node[] = Regex::ESC.'r';
        return $this;
    }
    
    public function TAB( )
    {
        $this->ast[$this->level]->node[] = Regex::ESC.'t';
        return $this;
    }
    
    public function CTRL( $code='0' )
    {
        $this->ast[$this->level]->node[] = Regex::ESC.'c'.$code;
        return $this;
    }
    
    public function HEX( $code='0' )
    {
        $this->ast[$this->level]->node[] = Regex::ESC.'x'.Regex::pad($code, 2);
        return $this;
    }
    
    public function UNICODE( $code='0' )
    {
        $this->ast[$this->level]->node[] = Regex::ESC.'u'.Regex::pad($code, 4);
        return $this;
    }
    
    public function backSpace( )
    {
        $this->ast[$this->level]->node[] = '['.Regex::ESC.'b]';
        return $this;
    }
    
    public function any( $multiline=false )
    {
        $this->ast[$this->level]->node[] = true===$multiline ? '['.Regex::ESC.'s'.Regex::ESC.'S]' : '.';
        return $this;
    }
    
    public function space( $positive=true )
    {
        $this->ast[$this->level]->node[] = false===$positive ? Regex::ESC.'S' : Regex::ESC.'s';
        return $this;
    }
    
    public function digit( $positive=true )
    {
        $this->ast[$this->level]->node[] = false===$positive ? Regex::ESC.'D' : Regex::ESC.'d';
        return $this;
    }
    
    public function word( $positive=true )
    {
        $this->ast[$this->level]->node[] = false===$positive ? Regex::ESC.'W' : Regex::ESC.'w';
        return $this;
    }
    
    public function boundary( $positive=true )
    {
        $this->ast[$this->level]->node[] = false===$positive ? Regex::ESC.'B' : Regex::ESC.'b';
        return $this;
    }
    
    public function characters( )
    {
        if ( Regex::T_CHARGROUP === $this->ast[$this->level]->type )
            $this->ast[$this->level]->node[] = implode('', array_map(array('Regex','esc_chars'), Regex::getArgs(func_get_args(),1)));
        return $this;
    }
    
    public function chars( )
    {
        if ( Regex::T_CHARGROUP === $this->ast[$this->level]->type )
            $this->ast[$this->level]->node[] = implode('', array_map(array('Regex','esc_chars'), Regex::getArgs(func_get_args(),1)));
        return $this;
    }
    
    public function range( $start=null, $end=null )
    {
        if ( null !== $start && null !== $end && Regex::T_CHARGROUP === $this->ast[$this->level]->type )
            $this->ast[$this->level]->node[] = Regex::esc_re((string)$start, Regex::ESC, 1).'-'.Regex::esc_re((string)$end, Regex::ESC, 1);
        return $this;
    }
    
    public function backReference( $n )
    {
        $this->ast[$this->level]->node[] = Regex::ESC.(isset($this->grp[$n]) ? $this->grp[$n] : (int)$n);
        return $this;
    }
    
    public function repeat( $min, $max=null, $greedy=true )
    {
        if ( null === $min ) return $this;
        $repeat = (null===$max || $min===$max? ('{'.(string)$min.'}') : ('{'.(string)$min.','.(string)$max.'}')) . (false===$greedy ? '?' : '');
        $this->ast[$this->level]->node[count($this->ast[$this->level]->node)-1] .= $repeat;
        return $this;
    }
    
    public function zeroOrOne( $greedy=true )
    {
        $this->ast[$this->level]->node[count($this->ast[$this->level]->node)-1] .= (false===$greedy ? '??' : '?');
        return $this;
    }
    
    public function zeroOrMore( $greedy=true )
    {
        $this->ast[$this->level]->node[count($this->ast[$this->level]->node)-1] .= (false===$greedy ? '*?' : '*');
        return $this;
    }
    
    public function oneOrMore( $greedy=true )
    {
        $this->ast[$this->level]->node[count($this->ast[$this->level]->node)-1] .= (false===$greedy ? '+?' : '+');
        return $this;
    }
    
    public function alternate( )
    {
        $this->level++;
        $this->ast[] = (object)array('node'=> array(), 'type'=> Regex::T_ALTERNATION, 'flag'=> '');
        return $this;
    }
    
    public function either( )
    {
        return $this->alternate( );
    }
    
    public function group( $opts=array() )
    {
        $type = Regex::T_GROUP; $fl = '';
        $opts = (array)$opts;
        if ( isset($opts['name']) && strlen($opts['name']) )
        {
            $this->g++;
            $this->grp[$this->g] = $this->g;
            $this->grp[$opts['name']] = $this->g;
        }
        elseif ( isset($opts['lookahead']) && ((true === $opts['lookahead']) || (false === $opts['lookahead'])) )
        {
            $fl = false === $opts['lookahead'] ? '?!' : '?=';
        }
        elseif ( isset($opts['lookbehind']) && ((true === $opts['lookbehind']) || (false === $opts['lookbehind'])) )
        {
            $fl = false === $opts['lookbehind'] ? '?<!' : '?<=';
        }
        elseif ( isset($opts['nocapture']) && (true === $opts['nocapture']) )
        {
            $fl = '?:';
        }
        elseif ( isset($opts['characters']) && ((true === $opts['characters']) || (false === $opts['characters'])) )
        {
            $type = Regex::T_CHARGROUP;
            $fl = false === $opts['characters'] ? '^' : '';
        }
        else
        {
            $this->g++;
            $this->grp[$this->g] = $this->g;
        }
        $this->level++;
        $this->ast[] = (object)array('node'=> array(), 'type'=> $type, 'flag'=> $fl);
        return $this;
    }
    
    public function subGroup( $opts=array() )
    {
        return $this->group( $opts );
    }
    
    public function characterGroup( $positive=true )
    {
        return $this->group(array('characters'=>false!==$positive));
    }
    
    public function charGroup( $positive=true )
    {
        return $this->group(array('characters'=>false!==$positive));
    }
    
    public function namedGroup( $name )
    {
        return $this->group(array('name'=>(string)$name));
    }
    
    public function nonCaptureGroup( )
    {
        return $this->group(array('nocapture'=>true));
    }
    
    public function lookAheadGroup( $positive=true )
    {
        return $this->group(array('lookahead'=>false!==$positive));
    }
    
    public function lookBehindGroup( $positive=true )
    {
        return $this->group(array('lookbehind'=>false!==$positive));
    }
    
    public function end( $n=1 )
    {
        $n = (int)$n;
        if ( 0 >= $n ) $n = 1;
        // support ending multiple blocks at once
        while( $n-- )
        {
            $prev = empty($this->ast) ? null : array_pop($this->ast);
            $type = $prev ? $prev->type : 0;
            $flag = $prev ? $prev->flag : '';
            $part = $prev ? $prev->node : array();
            if ( 0 < $this->level )
            {
                --$this->level;
                if ( Regex::T_ALTERNATION === $type )
                    $this->ast[$this->level]->node[] = implode('|',$part);
                elseif ( Regex::T_GROUP === $type )
                    $this->ast[$this->level]->node[] = '('.$flag.implode('',$part).')';
                elseif ( Regex::T_CHARGROUP === $type )
                    $this->ast[$this->level]->node[] = '['.$flag.implode('',$part).']';
                else
                    $this->ast[$this->level]->node[] = implode('',$part);
            }
        }
        return $this;
    }
    
    public function startOfLine( )
    {
        return $this->SOL( );
    }
    
    public function startOfInput( )
    {
        return $this->SOF( );
    }
    
    public function endOfLine( )
    {
        return $this->EOL( );
    }
    
    public function endOfInput( )
    {
        return $this->EOF( );
    }
}
class Regex
{
    const VERSION = "1.0.0";
    const T_SEQUENCE = 1;
    const T_ALTERNATION = 2;
    const T_GROUP = 4;
    const T_CHARGROUP = 8;
    const T_QUANTIFIER = 16;
    const T_UNICODECHAR = 32;
    const T_HEXCHAR = 64;
    const T_SPECIAL = 128;
    const T_CHARS = 256;
    const T_CHARRANGE = 512;
    const T_STRING = 1024;
    const T_COMMENT = 2048;
    const ESC = '\\';
    
    public static $specialChars = array(
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
    public static $specialCharsEscaped = array(
        "\\" => "ESC",
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
    
    public static function esc_re( $s, $esc, $chargroup=false )
    {
        $es = ''; $l = strlen($s); $i=0;
        //escaped_re = /([.*+?^${}()|[\]\/\\\-])/g
        if ( $chargroup )
        {
            while( $i < $l )
            {
                $c = $s[$i++];
                $es .= (/*('?' === $c) || ('*' === $c) || ('+' === $c) ||*/
                        ('-' === $c) || /*('.' === $c) ||*/ ('^' === $c) || ('$' === $c) || ('|' === $c) || 
                        ('{' === $c) || ('}' === $c) || ('(' === $c) || (')' === $c) ||
                        ('[' === $c) || (']' === $c) || ('/' === $c) || ($esc === $c) ? $esc : '') . $c;
            }
        }
        else
        {
            while( $i < $l )
            {
                $c = $s[$i++];
                $es .= (('?' === $c) || ('*' === $c) || ('+' === $c) ||
                        /*('-' === $c) ||*/ ('.' === $c) || ('^' === $c) || ('$' === $c) || ('|' === $c) || 
                        ('{' === $c) || ('}' === $c) || ('(' === $c) || (')' === $c) ||
                        ('[' === $c) || (']' === $c) || ('/' === $c) || ($esc === $c) ? $esc : '') . $c;
            }
        }
        return $es;
    }
    public static function esc_chars( $s )
    {
        return self::esc_re( $s, Regex::ESC, 1 );
    }
    public static function pad( $s, $n, $z='0' )
    {
        $ps = (string)$s;
        while ( strlen($ps) < $n ) $ps = $z . $ps;
        return $ps;
    }
    public static function to_array( $x )
    {
        if ( is_array($x) )
        {
            $k = array_keys($x);
            return $k === array_keys($k) ? $x : array($x);
        }
        else
        {
            return array($x);
        }
    }
    public static function flatten( $a=null ) 
    {
        if ( !$a ) return array();
        $r = array(); $i = 0;
        $l = count((array)$a);
        while ($i < $l) $r = array_merge( $r, (array)$a[$i++] );
        return $r;
    }
        
    public static function getArgs( $args, $asArray=null ) 
    {
        return self::flatten( $args ); //a;
    }
    
    public static function Node( $type, $value, $flags=null )
    {
        return new RegexNode($type, $value, $flags);
    }
    
    public static function Analyzer( $re=null, $delim='/' )
    {
        return new RegexAnalyzer($re, $delim);
    }
    
    public static function Composer( )
    {
        return new RegexComposer();
    }
    
    public static function init( )
    {
        RegexAnalyzer::init();
        //RegexComposer::init();
    }
}
Regex::init();
}