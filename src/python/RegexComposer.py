# -*- coding: UTF-8 -*-
##
#
#   RegexComposer
#   @version: 0.1
#
#   A simple and intuitive Regular Expression Composer in Python
#   https://github.com/foo123/RegexAnalyzer
#
##
class RegexComposer:

    
    VERSION = "0.1"
    
    T_SEQ = 2
    T_EITHER = 4
    T_GROUP = 8
    T_CHARGROUP = 16
    
    private $level = 0;
    public $regex = null;
    public $parts = null;
    
    private static function esc($s) 
    {
        return preg_quote($s, '/');
    }
        
    private static function flatten($a=null) 
    {
        if ( !$a ) return array();
        $r = array(); $i = 0;
        $l = count((array)$a);
        while ($i < $l) $r = array_merge( $r, (array)$a[$i++] );
        return $r;
    }
        
    private static function getArgs($args, $asArray=null) 
    {
        return self::flatten( $args ); //a;
    }
        
    
    // A simple (js-flavored) regular expression composer
    public function __construct( ) 
    {
        $this->regex = null;
        $this->reset();
    }
    
    public function compose(/* flags */) 
    {
        $this->regex = '/' . implode('', $this->parts[0]['part'] ) . '/' . implode('', func_get_args());
        $this->reset();
        return $this->regex;
    }

    public function partial($reset=false) 
    {
        $p = implode('', $this->parts[0]['part']);
        if (false!==$reset) $this->reset();
        return $p;
    }

    public function reset() 
    {
        $this->level = 0;
        $this->parts = array(array('part'=> array(), 'type'=> self::T_SEQ, 'flag'=> ''));
        return $this;
    }

    public function repeat($min=null, $max=null, $greedy=true) 
    {
        if ( null === $min ) return $this;
        $repeat = ( null === $max ) ? ('{'.$min.'}') : ('{'.$min.','.$max.'}');
        
        $this->parts[$this->level]['part'][count($this->parts[$this->level]['part'])-1] .= (false===$greedy) ? ($repeat.'?') : $repeat;
        return $this;
    }
    
    public function zeroOrOne($greedy=true)
    {
        $this->parts[$this->level]['part'][count($this->parts[$this->level]['part'])-1] .= (false===$greedy) ? '??' : '?';
        return $this;
    }
    
    public function zeroOrMore($greedy=true) 
    {
        $this->parts[$this->level]['part'][count($this->parts[$this->level]['part'])-1] .= (false===$greedy) ? '*?' : '*';
        return $this;
    }
    
    public function oneOrMore($greedy=true) 
    {
        $this->parts[$this->level]['part'][count($this->parts[$this->level]['part'])-1] .= (false===$greedy) ? '+?' : '+';
        return $this;
    }
    
    public function sub($partialRegex=null, $withParen=false) 
    {
        if ( null !== $partialRegex )
        {
            if ( $withParen )
                $this->parts[$this->level]['part'][] = '(' . $partialRegex . ')';
            else
                $this->parts[$this->level]['part'][] = $partialRegex;
        }
        return $this;
    }
    
    public function match($part=null) 
    {
        if ( null !== $part )
            $this->parts[$this->level]['part'][] = self::esc($part);
        return $this;
    }
    
    public function startOfInput() 
    {
        $this->parts[$this->level]['part'][] = '^';
        return $this;
    }
    
    public function endOfInput() 
    {
        $this->parts[$this->level]['part'][] = '$';
        return $this;
    }
    
    public function any() 
    {
        $this->parts[$this->level]['part'][] = '.';
        return $this;
    }
    
    public function space($positive=true) 
    {
        $this->parts[$this->level]['part'][] = (false==$positive) ? '\\S' : '\\s';
        return $this;
    }
    
    public function digit($positive=true) 
    {
        $this->parts[$this->level]['part'][] = (false==$positive) ? '\\D' : '\\d';
        return $this;
    }
    
    public function word($positive=true) 
    {
        $this->parts[$this->level]['part'][] = (false==$positive) ? '\\W' : '\\w';
        return $this;
    }
    
    public function boundary($positive=true) 
    {
        $this->parts[$this->level]['part'][] = (false==$positive) ? '\\B' : '\\b';
        return $this;
    }
    
    public function LF() 
    {
        $this->parts[$this->level]['part'][] = '\\n';
        return $this;
    }
    
    public function CR() 
    {
        $this->parts[$this->level]['part'][] = '\\r';
        return $this;
    }
    
    public function TAB() 
    {
        $this->parts[$this->level]['part'][] = '\\t';
        return $this;
    }
    
    public function CTRL($_char=null) 
    {
        if ( $_char )
            $this->parts[$this->level]['part'][] = '\\c'.$_char;
        return $this;
    }
    
    public function backSpace() 
    {
        $this->parts[$this->level]['part'][] = '[\\b]';
        return $this;
    }
    
    public function backReference($n) 
    {
        $this->parts[$this->level]['part'][] = '\\'.intval($n, 10);
        return $this;
    }
    
    public function characters() 
    {
        if ( self::T_CHARGROUP == $this->parts[$this->level]['type'] )
        {
            $chars = implode( '', array_map( array('RegExComposer', 'esc'), self::getArgs(func_get_args(), 1)));
            $this->parts[$this->level]['part'][] = $chars;
        }
        return $this;
    }
    
    public function range($start=null, $end=null) 
    {
        if ( self::T_CHARGROUP == $this->parts[$this->level]['type'] )
        {
            if ( null === $start || null === $end ) return $this;
            $range = self::esc($start) . '-' . self::esc($end);
            $this->parts[$this->level]['part'][] = $range;
        }
        return $this;
    }
    
    public function alternate() 
    {
        $this->level++;
        $this->parts[] = array('part'=> array(), 'type'=> self::T_EITHER, 'flag'=> '');
        return $this;
    }
    
    // alias
    public function either() 
    {
        return $this->alternate();
    }
    
    public function group() 
    {
        $this->level++;
        $this->parts[] = array('part'=> array(), 'type'=> self::T_GROUP, 'flag'=> '');
        return $this;
    }
    
    public function nonCaptureGroup() 
    {
        $this->level++;
        $this->parts[] = array('part'=> array(), 'type'=> self::T_GROUP, 'flag'=> '?:');
        return $this;
    }
    
    public function lookAheadGroup($positive=true) 
    {
        $this->level++;
        $this->parts[] = array('part'=> array(), 'type'=> self::T_GROUP, 'flag'=> (false==$positive) ? '?!' : '?=');
        return $this;
    }
    
    public function characterGroup($positive=true) 
    {
        $this->level++;
        $this->parts[] = array('part'=> array(), 'type'=> self::T_CHARGROUP, 'flag'=> (false==$positive) ? '^' : '');
        return $this;
    }
    
    public function end() 
    {
        $prev = count($this->parts) > 1 ? array_pop($this->parts) : array();
        $type = isset($prev['type']) ? $prev['type'] : 0; 
        $flag = isset($prev['flag']) ? $prev['flag'] : '';
        $part = isset($prev['part']) ? $prev['part'] : array();
        
        if (0 < $this->level)
        {
            $level = --$this->level;
            
            if ( (self::T_EITHER|self::T_GROUP) & $type )
                $this->parts[$level]['part'][] = '(' . $flag . implode('|', $part) . ')';
            
            else if ( self::T_CHARGROUP & $type )
                $this->parts[$level]['part'][] = '[' . $flag . implode('', $part) . ']';
        }
        return $this;
    }
    
# if used with 'import *'
__all__ = ['RegexComposer']
