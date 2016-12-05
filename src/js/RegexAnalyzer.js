/**
*
*   RegexAnalyzer
*   @version: 0.6.0
*
*   A simple Regular Expression Analyzer for PHP, Python, Node/XPCOM/JS, ActionScript
*   https://github.com/foo123/RegexAnalyzer
*
**/
!function( root, name, factory ){
"use strict";
if ( ('undefined'!==typeof Components)&&('object'===typeof Components.classes)&&('object'===typeof Components.classesByID)&&Components.utils&&('function'===typeof Components.utils['import']) ) /* XPCOM */
    (root.$deps = root.$deps||{}) && (root.EXPORTED_SYMBOLS = [name]) && (root[name] = root.$deps[name] = factory.call(root));
else if ( ('object'===typeof module)&&module.exports ) /* CommonJS */
    (module.$deps = module.$deps||{}) && (module.exports = module.$deps[name] = factory.call(root));
else if ( ('undefined'!==typeof System)&&('function'===typeof System.register)&&('function'===typeof System['import']) ) /* ES6 module */
    System.register(name,[],function($__export){$__export(name, factory.call(root));});
else if ( ('function'===typeof define)&&define.amd&&('function'===typeof require)&&('function'===typeof require.specified)&&require.specified(name) /*&& !require.defined(name)*/ ) /* AMD */
    define(name,['module'],function(module){factory.moduleUri = module.uri; return factory.call(root);});
else if ( !(name in root) ) /* Browser/WebWorker/.. */
    (root[name] = factory.call(root)||1)&&('function'===typeof(define))&&define.amd&&define(function(){return root[name];} );
}(  /* current root */          this, 
    /* module name */           "RegexAnalyzer",
    /* module factory */        function ModuleFactory__RegexAnalyzer( undef ){
"use strict";
var __version__ = "0.6.0",

    PROTO = 'prototype', Obj = Object, Arr = Array, /*Str = String,*/ 
    Keys = Obj.keys, to_string = Obj[PROTO].toString, 
    fromCharCode = String.fromCharCode, CHAR = 'charAt', CHARCODE = 'charCodeAt', toJSON = JSON.stringify,
    INF = Infinity, HAS = 'hasOwnProperty', ESC = '\\',
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
    },
    /*
        http://www.javascriptkit.com/javatutors/redev2.shtml
        
        \f matches form-feed.
        \r matches carriage return.
        \n matches linefeed.
        \t matches horizontal tab.
        \v matches vertical tab.
        \0 matches NUL character.
        [\b] matches backspace.
        \s matches whitespace (short for [\f\n\r\t\v\u00A0\u2028\u2029]).
        \S matches anything but a whitespace (short for [^\f\n\r\t\v\u00A0\u2028\u2029]).
        \w matches any alphanumerical character (word characters) including underscore (short for [a-zA-Z0-9_]).
        \W matches any non-word characters (short for [^a-zA-Z0-9_]).
        \d matches any digit (short for [0-9]).
        \D matches any non-digit (short for [^0-9]).
        \b matches a word boundary (the position between a word and a space).
        \B matches a non-word boundary (short for [^\b]).
        \cX matches a control character. E.g: \cm matches control-M.
        \xhh matches the character with two characters of hexadecimal code hh.
        \uhhhh matches the Unicode character with four characters of hexadecimal code hhhh.        
    */
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
    },
    T_SEQUENCE = 1, T_ALTERNATION = 2, T_GROUP = 3,
    T_QUANTIFIER = 4, T_UNICODECHAR = 5, T_HEXCHAR = 6,
    T_SPECIAL = 7, T_CHARGROUP = 8, T_CHARS = 9,
    T_CHARRANGE = 10, T_STRING = 11;

function is_array( x )
{
    return (x instanceof Array) || ('[object Array]' === to_string.call(x));
}
function is_string( x )
{
    return (x instanceof String) || ('[object String]' === to_string.call(x));
}
function is_regexp( x )
{
    return (x instanceof RegExp) || ('[object RegExp]' === to_string.call(x));
}
function clone( obj, cloned )
{
    cloned = cloned || {};
    for (var p in obj) if ( obj[HAS](p) ) cloned[p] = obj[p];
    return cloned;
}
var RE_OBJ = function( re ) {
    var self = this;
    self.re = re;
    self.len = re.length;
    self.pos = 0;
    self._groupIndex = 0;
    self.groupIndex = 0;
    self.inGroup = 0;
},
Node = function Node( type, value, flags ) {
    var self = this;
    if ( !(self instanceof Node) ) return new Node(type, value, flags);
    self.type = type;
    self.val = value;
    self.flags = flags || {};
    switch(type)
    {
        case T_SEQUENCE: 
            self.typeName = "Sequence"; break;
        case T_ALTERNATION: 
            self.typeName = "Alternation"; break;
        case T_GROUP: 
            self.typeName = "Group"; break;
        case T_CHARGROUP: 
            self.typeName = "CharacterGroup"; break;
        case T_CHARS: 
            self.typeName = "Characters"; break;
        case T_CHARRANGE: 
            self.typeName = "CharacterRange"; break;
        case T_STRING: 
            self.typeName = "String"; break;
        case T_QUANTIFIER: 
            self.typeName = "Quantifier"; break;
        case T_UNICODECHAR: 
            self.typeName = "UnicodeChar"; break;
        case T_HEXCHAR: 
            self.typeName = "HexChar"; break;
        case T_SPECIAL: 
            self.typeName = "Special"; break;
        default: 
            self.typeName = "unspecified"; break;
    }
};
Node.toObjectStatic = function toObject( v ) {
    if (v instanceof Node)
    {
        return {
            type: v.typeName,
            value: toObject(v.val),
            flags: v.flags
        }; 
    }
    else if (v instanceof Array)
    {
        return v.map(toObject);
    }
    return v;
};
Node[PROTO] = {
    constructor: Node
    ,type: null
    ,typeName: null
    ,val: null
    ,flags: null
    ,dispose: function( ) {
        var self = this;
        self.val = null;
        self.flags = null;
        self.type = null;
        self.typeName = null;
        return self;
    }
    ,toObject: function( ) {
        return Node.toObjectStatic(this);
    }
};

var rnd = function( a, b ){ return Math.round((b-a)*Math.random()+a); },
    esc_re = function( s, esc, chargroup ) {
        var es = '', l = s.length, i=0, c;
        if ( chargroup )
        {
            while( i < l )
            {
                c = s[CHAR](i++);
                //escaped_re = /([.*+?^${}()|[\]\/\\\-])/g
                es += (('?' === c) || ('*' === c) || ('+' === c) ||
                        ('-' === c) || ('^' === c) || ('$' === c) || ('|' === c) || 
                        ('{' === c) || ('}' === c) || ('(' === c) || (')' === c) ||
                        ('[' === c) || (']' === c) || ('/' === c) || (esc === c) ? esc : '') + c;
            }
        }
        else
        {
            while( i < l )
            {
                c = s[CHAR](i++);
                //escaped_re = /([.*+?^${}()|[\]\/\\\-])/g
                es += (('?' === c) || ('*' === c) || ('+' === c) ||
                    ('.' === c) || ('^' === c) || ('$' === c) || ('|' === c) || 
                    ('{' === c) || ('}' === c) || ('(' === c) || (')' === c) ||
                    ('[' === c) || (']' === c) || ('/' === c) || (esc === c) ? esc : '') + c;
            }
        }
        return es;
    },
    pad = function( s, n, z ) {
        var ps = String(s);
        z = z || '0';
        while ( ps.length < n ) ps += z + ps;
        return ps;
    },
    char_code = function( c ) { return c[CHARCODE](0); },
    char_code_range = function( s ) { return [s[CHARCODE](0), s[CHARCODE](s.length-1)]; },
    //char_codes = function( s_or_a ) { return (s_or_a.substr ? s_or_a.split("") : s_or_a).map( char_code ); },
    // http://stackoverflow.com/questions/12376870/create-an-array-of-characters-from-specified-range
    character_range = function(first, last) {
        if ( first && is_array(first) ) { last = first[1]; first = first[0]; }
        var ch, chars, start = first[CHARCODE](0), end = last[CHARCODE](0);
        
        if ( end === start ) return [ fromCharCode( start ) ];
        
        chars = [];
        for (ch = start; ch <= end; ++ch) chars.push( fromCharCode( ch ) );
        return chars;
    },
    concat = function(p1, p2) {
        if ( p2 )
        {
            var p, l;
            if ( is_array(p2) )
            {
                for (p=0,l=p2.length; p<l; p++) p1[p2[p]] = 1;
            }
            else
            {
                for (p in p2) if ( p2[HAS](p) ) p1[p] = 1;
            }
        }
        return p1;
    },
    
    BSPACES = "\r\n", SPACES = " \t\v", PUNCTS = "~!@#$%^&*()-+=[]{}\\|;:,./<>?",
    DIGITS = "0123456789", DIGITS_RANGE = char_code_range(DIGITS),
    HEXDIGITS_RANGES = [DIGITS_RANGE, [char_code("a"), char_code("f")], [char_code("A"), char_code("F")]],
    ALPHAS = "_"+(character_range("a", "z").join(""))+(character_range("A", "Z").join("")),
    ALL = SPACES+PUNCTS+DIGITS+ALPHAS, ALL_ARY = ALL.split(""),
    
    match_chars = function( CHARS, s, pos, minlen, maxlen ) {
        pos = pos || 0;
        minlen = minlen || 1;
        maxlen = maxlen || INF;
        var lp = pos, l = 0, sl = s.length, ch;
        while ( (lp < sl) && (l <= maxlen) && -1 < CHARS.indexOf( ch=s[CHAR](lp) ) ) 
        { 
            lp++; l++; 
        }
        return l >= minlen ? l : false;
    },
    match_char_range = function( RANGE, s, pos, minlen, maxlen ) {
        pos = pos || 0;
        minlen = minlen || 1;
        maxlen = maxlen || INF;
        var lp = pos, l = 0, sl = s.length, ch;
        while ( (lp < sl) && (l <= maxlen) && ((ch=s[CHARCODE](lp)) >= RANGE[0] && ch <= RANGE[1]) ) 
        { 
            lp++; l++;
        }
        return l >= minlen ? l : false;
    },
    match_char_ranges = function( RANGES, s, pos, minlen, maxlen ) {
        pos = pos || 0;
        minlen = minlen || 1;
        maxlen = maxlen || INF;
        var lp = pos, l = 0, sl = s.length, ch, 
            i, Rl = RANGES.length, RANGE, found = true;
        while ( (lp < sl) && (l <= maxlen) && found ) 
        { 
            ch = s[CHARCODE](lp); found = false;
            for (i=0; i<Rl; i++)
            {
                RANGE = RANGES[i];
                if ( ch >= RANGE[0] && ch <= RANGE[1] )
                {
                    lp++; l++; found = true;
                    break;
                }
            }
        }
        return l >= minlen ? l : false;
    },

    punct = function( ){ 
        return PUNCTS[CHAR](rnd(0, PUNCTS.length-1)); 
    },
    space = function( positive ){ 
        return false !== positive 
            ? SPACES[CHAR](rnd(0, SPACES.length-1))
            : (punct()+digit()+alpha())[CHAR](rnd(0,2))
        ; 
    },
    digit = function( positive ){ 
        return false !== positive 
            ? DIGITS[CHAR](rnd(0, DIGITS.length-1))
            : (punct()+space()+alpha())[CHAR](rnd(0,2))
        ; 
    },
    alpha = function( positive ){ 
        return false !== positive 
            ? ALPHAS[CHAR](rnd(0, ALPHAS.length-1))
            : (punct()+space()+digit())[CHAR](rnd(0,2))
        ; 
    },
    word = function( positive ){ 
        return false !== positive 
            ? (ALPHAS+DIGITS)[CHAR](rnd(0, ALPHAS.length+DIGITS.length-1))
            : (punct()+space())[CHAR](rnd(0,1))
        ; 
    },
    any = function( ){ 
        return ALL[CHAR](rnd(0, ALL.length-1));
    },
    character = function( chars, positive ){ 
        if ( false !== positive ) return chars.length ? chars[rnd(0, chars.length-1)] : ''; 
        var choices = ALL_ARY.filter(function(c){ return 0 > chars.indexOf(c); }); 
        return choices.length ? choices[rnd(0, choices.length-1)] : '';
    },
    random_upper_or_lower = function( c ) { return 0.5 < Math.random() ? c.toLowerCase( ) : c.toUpperCase( ); },
    case_insensitive = function( chars, asArray ) {
        if ( asArray )
        {
            if ( chars[CHAR] ) chars = chars.split('');
            chars = chars.map( random_upper_or_lower );
            //if ( !asArray ) chars = chars.join('');
            return chars;
        }
        else
        {
            return random_upper_or_lower( chars );
        }
    },
    
    walk = function walk( ret, node, state ) {
        if ( (null == node) || !state ) return ret;
        
        var i, l, r, type = node instanceof Node ? node.type : null;
        
        // walk the tree
        if ( null === type )
        {
            // custom, let reduce handle it
            ret = state.reduce( ret, node, state );
        }
        
        else if ( T_ALTERNATION === type || T_SEQUENCE === type ||
            T_CHARGROUP === type || T_GROUP === type || T_QUANTIFIER === type
        )
        {
            r = state.map( ret, node, state );
            if ( null != state.ret )
            {
                ret = state.reduce( ret, node, state );
                state.ret = null;
            }
            else if ( null != r )
            {
                if ( !is_array(r) ) r = [r];
                for(i=0,l=r?r.length:0; i<l; i++)
                {
                    state.node = node;
                    ret = walk( ret, r[i], state );
                    if ( state.stop )
                    {
                        state.stop = null;
                        return ret;
                    }
                }
            }
        }
        
        else if ( T_CHARS === type || T_CHARRANGE === type ||
                T_UNICODECHAR === type || T_HEXCHAR === type ||
                T_SPECIAL === type || T_STRING === type
        )
        {
            ret = state.reduce( ret, node, state );
        }
        
        state.node = null;
        return ret;
    },
    /*map_all = function map_all( ret, node, state ) {
        return node.val;
    },*/
    map_src = function map_src( ret, node, state ) {
        var type = node.type, r;
        if ( T_ALTERNATION === type )
        {
            r = [];
            for(var i=0,l=node.val.length-1; i<l; i++) r.push(node.val[i],'|');
            r.push(node.val[node.val.length-1]);
            return r;
        }
        else if ( T_CHARGROUP === type )
        {
            return [].concat('['+(node.flags.NegativeMatch?'^':'')).concat(node.val).concat(']');
        }
        else if ( T_QUANTIFIER === type )
        {
            var q = '';
            if ( node.flags.MatchZeroOrOne ) q = '?'+(node.flags.isGreedy?'':'?');
            else if ( node.flags.MatchZeroOrMore ) q = '*'+(node.flags.isGreedy?'':'?');
            else if ( node.flags.MatchOneOrMore ) q = '+'+(node.flags.isGreedy?'':'?');
            else q = node.flags.min === node.flags.max ? ('{'+node.flags.min+'}') : ('{'+node.flags.min+','+(-1===node.flags.max?'':node.flags.max)+'}');
            return [].concat(node.val).concat(q);
        }
        else if ( T_GROUP === type )
        {
            var g = null;
            if ( node.flags.NotCaptured )
            {
                g = [].concat('(?:').concat(node.val).concat(')');
            }
            else if ( node.flags.LookAhead )
            {
                g = [].concat('(?=').concat(node.val).concat(')');
            }
            else if ( node.flags.NegativeLookAhead )
            {
                g = [].concat('(?!').concat(node.val).concat(')');
            }
            /*else if ( node.flags.NegativeMatch )
            {
                g = [].concat('((?:').concat(node.val).concat(')|[\\s\\S]+)');
            }
            else if ( node.flags.LookBehind )
            {
                g = null;
            }*/
            else
            {
                g = [].concat('(').concat(node.val).concat(')');
            }
            if ( null != node.flags.GroupIndex )
            {
                ret.group[node.flags.GroupIndex] = node.flags.GroupIndex;
                if ( node.flags.GroupName ) ret.group[node.flags.GroupName] = node.flags.GroupIndex;
            }
            return g;
        }
        return node.val;
    },
    map_any = function map_any( ret, node, state ) {
        var type = node.type;
        if ( T_ALTERNATION === type || T_CHARGROUP === type )
        {
            return node.val.length ? node.val[rnd(0, node.val.length-1)] : null;
        }
        else if ( T_QUANTIFIER === type )
        {
            var numrepeats, mmin, mmax, repeats;
            if ( ret.length >= state.maxLength )
            {
                numrepeats = node.flags.min;
            }
            else
            {
                mmin = node.flags.min;
                mmax = -1 === node.flags.max ? (mmin+1+2*state.maxLength) : node.flags.max;
                numrepeats = rnd(mmin, mmax);
            }
            if ( numrepeats )
            {
                repeats = new Array(numrepeats);
                for(var i=0; i<numrepeats; i++) repeats[i] = node.val;
                return repeats;
            }
            else
            {
                return null;
            }
        }
        else
        {
            return node.val;
        }
    },
    map_min = function map_min( ret, node, state ) {
        var type = node.type;
        if ( T_ALTERNATION === type )
        {
            var i, l = node.val.length, cur,
                min = l ? walk(0, node.val[0], state) : 0;
            for(i=1; i<l; i++)
            {
                cur = walk(0, node.val[i], state);
                if ( cur < min ) min = cur;
            }
            if ( l ) state.ret = min;
            return null;
        }
        else if ( T_CHARGROUP === type )
        {
            return node.val.length ? node.val[0] : null;
        }
        else if ( T_QUANTIFIER === type )
        {
            if ( 0 === node.flags.min ) return null;
            var i, nrepeats = node.flags.min, repeats = new Array(nrepeats);
            for(i=0; i<nrepeats; i++) repeats[i] = node.val;
            return repeats;
        }
        else
        {
            return node.val;
        }
    },
    map_max = function map_max( ret, node, state ) {
        var type = node.type;
        if ( T_ALTERNATION === type )
        {
            var i, l = node.val.length, cur, max = l ? walk(0, node.val[0], state) : 0;
            if ( -1 !== max )
            {
                for(i=1; i<l; i++)
                {
                    cur = walk(0, node.val[i], state);
                    if ( -1 === cur )
                    {
                        max = -1;
                        break;
                    }
                    else if ( cur > max )
                    {
                        max = cur;
                    }
                }
            }
            if ( l ) state.ret = max;
            return null;
        }
        else if ( T_CHARGROUP === type )
        {
            return node.val.length ? node.val[0] : null;
        }
        else if ( T_QUANTIFIER === type )
        {
            max = walk(0, node.val, state);
            if ( -1 === max )
            {
                state.ret = -1;
            }
            else if ( 0 < max )
            {
                if ( -1 === node.flags.max )
                {
                    state.ret = -1;
                }
                else if ( 0 < node.flags.max )
                {
                    state.ret = node.flags.max*max;
                }
                else
                {
                    state.ret = max;
                }
            }
            return null;
        }
        else
        {
            return node.val;
        }
    },
    map_1st = function map_1st( ret, node, state ) {
        var type = node.type;
        if ( T_SEQUENCE === type )
        {
            var seq=[], i=0, l=node.val.length, n;
            for(i=0; i<l; i++)
            {
                n = node.val[i];
                seq.push( n );
                if ( (T_QUANTIFIER === n.type) && (0 === n.flags.min) )
                    continue;
                else if ( (T_SPECIAL === n.type) && (n.flags.MatchStart || n.flags.MatchEnd) )
                    continue;
                break;
            }
            return seq.length ? seq : null;
        }
        else
        {
            return node.val;
        }
    },
    reduce_len = function reduce_len( ret, node, state ) {
        if ( null != state.ret )
        {
            if ( -1 === state.ret ) ret = -1;
            else ret += state.ret;
            return ret;
        }
        if ( -1 === ret ) return ret;
        if ( (T_SPECIAL === node.type) && node.flags.MatchEnd )
        {
            state.stop = 1;
            return ret;
        }
        var type = node.type;
        
        if ( T_CHARS === type || T_CHARRANGE === type ||
            T_UNICODECHAR === type || T_HEXCHAR === type ||
            (T_SPECIAL === type && !node.flags.MatchStart && !node.flags.MatchEnd)
        )
        {
            ret += 1;
        }
        else if ( T_STRING === type )
        {
            ret += node.val.length;
        }
        
        return ret;
    },
    reduce_str = function reduce_str( ret, node, state ) {
        if ( null != state.ret )
        {
            ret += state.ret;
            return ret;
        }
        if ( (T_SPECIAL === node.type) && node.flags.MatchEnd )
        {
            state.stop = 1;
            return ret;
        }
        var type = node.type, sample = null;
        
        if ( T_CHARS === type )
        {
            sample = node.val;
        }
        else if ( T_CHARRANGE === type )
        {
            var range = [node.val[0],node.val[1]];
            if ( T_UNICODECHAR === range[0].type || T_HEXCHAR === range[0].type ) range[0] = range[0].flags.Char;
            if ( T_UNICODECHAR === range[1].type || T_HEXCHAR === range[1].type ) range[1] = range[1].flags.Char;
            sample = character_range(range);
        }
        else if ( (T_UNICODECHAR === type) || (T_HEXCHAR === type) )
        {
            sample = [node.flags.Char];
        }
        else if ( (T_SPECIAL === type) && !node.flags.MatchStart && !node.flags.MatchEnd )
        {
            var part = node.val;
            if ('D' === part)
            {
                sample = [digit( false )];
            }
            else if ('W' === part)
            {
                sample = [word( false )];
            }
            else if ('S' === part)
            {
                sample = [space( false )];
            }
            else if ('d' === part)
            {
                sample = [digit( )];
            }
            else if ('w' === part)
            {
                sample = [word( )];
            }
            else if ('s' === part)
            {
                sample = [space( )];
            }
            else if (('.' === part) && node.flags.MatchAnyChar)
            {
                sample = [any( )];
            }
            else
            {
                sample = ['\\' + part];
            }
        }
        else if ( T_STRING === type )
        {
            sample = node.val;
        }
        
        if ( sample )
        {
            ret += T_STRING === type ?
            (state.isCaseInsensitive ? case_insensitive(sample) : sample) :
            (character(state.isCaseInsensitive ? case_insensitive(sample, true) : sample, !state.node || !state.node.flags.NegativeMatch))
            ;
        }
        
        return ret;
    },
    reduce_src = function reduce_src( ret, node, state ) {
        if ( null != state.ret )
        {
            if ( state.ret.src ) ret.src += state.ret.src;
            if ( state.ret.group ) ret.group = clone(state.ret.group, ret.group);
            return ret;
        }
        if ( is_string(node) )
        {
            ret.src += node;
            return ret;
        }
        
        var type = node.type;
        if ( T_CHARS === type )
        {
            ret.src += state.escaped ? esc_re(node.val.join(''), ESC, 1) : node.val.join('');
        }
        else if ( T_CHARRANGE === type )
        {
            var range = [node.val[0],node.val[1]];
            if ( state.escaped )
            {
                if ( T_UNICODECHAR === range[0].type ) range[0] = '\\u'+pad(range[0].flags.Code,4);
                else if ( T_HEXCHAR === range[0].type ) range[0] = '\\x'+pad(range[0].flags.Code,2);
                else range[0] = esc_re(range[0], ESC, 1);
                if ( T_UNICODECHAR === range[1].type ) range[1] = '\\u'+pad(range[1].flags.Code,4);
                else if ( T_HEXCHAR === range[1].type ) range[1] = '\\x'+pad(range[1].flags.Code,2);
                else range[1] = esc_re(range[1], ESC, 1);
                ret.src += range[0]+'-'+range[1];
            }
            else
            {
                if ( T_UNICODECHAR === range[0].type || T_HEXCHAR === range[0].type ) range[0] = range[0].flags.Char;
                if ( T_UNICODECHAR === range[1].type || T_HEXCHAR === range[1].type ) range[1] = range[1].flags.Char;
                ret.src += range[0]+'-'+range[1];
            }
        }
        else if ( T_UNICODECHAR === type )
        {
            ret.src += state.escaped ? '\\u'+pad(node.flags.Code,4) : node.flags.Char;
        }
        else if ( T_HEXCHAR === type )
        {
            ret.src += state.escaped ? '\\x'+pad(node.flags.Code,2) : node.flags.Char;
        }
        else if ( T_SPECIAL === type )
        {
            ret.src += !node.flags.MatchStart && !node.flags.MatchEnd ? ('\\'+node.val) : (''+node.val);
        }
        else if ( T_STRING === type )
        {
            ret.src += state.escaped ? esc_re(node.val, ESC) : node.val;
        }
        
        return ret;
    },
    reduce_peek = function reduce_peek( ret, node, state ) {
        if ( null != state.ret )
        {
            ret.positive = concat( ret.positive, state.ret.positive );
            ret.negative = concat( ret.negative, state.ret.negative );
            return ret;
        }
        if ( T_SPECIAL === node.type && node.flags.MatchEnd )
        {
            state.stop = 1;
            return ret;
        }
        
        var type = node.type, inCharGroup = state.node && (T_CHARGROUP === state.node.type),
            inNegativeCharGroup = inCharGroup && state.node.flags.NegativeMatch,
            peek = inNegativeCharGroup ? "negative" : "positive";
        
        if ( T_CHARS === type )
        {
            ret[peek] = concat( ret[peek], node.val );
        }
        else if ( T_CHARRANGE === type )
        {
            var range = [node.val[0],node.val[1]];
            if ( T_UNICODECHAR === range[0].type || T_HEXCHAR === range[0].type ) range[0] = range[0].flags.Char;
            if ( T_UNICODECHAR === range[1].type || T_HEXCHAR === range[1].type ) range[1] = range[1].flags.Char;
            ret[peek] = concat( ret[peek], character_range(range) );
        }
        else if ( (T_UNICODECHAR === type) || (T_HEXCHAR === type) )
        {
            ret[peek][node.flags.Char] = 1;
        }
        else if ( (T_SPECIAL === type) && !node.flags.MatchStart && !node.flags.MatchEnd )
        {
            var part = node.val;
            if ('D' === part)
            {
                ret[inNegativeCharGroup?"positive":"negative"][ '\\d' ] = 1;
            }
            else if ('W' === part)
            {
                ret[inNegativeCharGroup?"positive":"negative"][ '\\w' ] = 1;
            }
            else if ('S' === part)
            {
                ret[inNegativeCharGroup?"positive":"negative"][ '\\s' ] = 1;
            }
            else
            {
                ret[peek]['\\' + part] = 1;
            }
        }
        else if ( T_STRING === type )
        {
            ret["positive"][node.val[CHAR](0)] = 1;
        }
        
        return ret;
    },
    
    match_hex = function( s ) {
        var m = false;
        if ( (s.length > 2) && ('x' === s[CHAR](0)) )
        {
            if ( match_char_ranges(HEXDIGITS_RANGES, s, 1, 2, 2) ) return [m=s.slice(0,3), m.slice(1)];
        }
        return false;
    },
    match_unicode = function( s ) {
        var m = false;
        if ( (s.length > 4) && ('u' === s[CHAR](0)) )
        {
            if ( match_char_ranges(HEXDIGITS_RANGES, s, 1, 4, 4) ) return [m=s.slice(0,5), m.slice(1)];
        }
        return false;
    },
    match_repeats = function( s ) {
        var l, sl = s.length, pos = 0, m = false, hasComma = false;
        if ( (sl > 2) && ('{' === s[CHAR](pos)) )
        {
            m = ['', '', null];
            pos++;
            if ( l=match_chars(SPACES, s, pos) ) pos += l;
            if ( l=match_char_range(DIGITS_RANGE, s, pos) ) 
            {
                m[1] = s.slice(pos, pos+l);
                pos += l;
            }
            else
            {
                return false;
            }
            if ( l=match_chars(SPACES, s, pos) ) pos += l;
            if ( (pos < sl) && (',' === s[CHAR](pos)) ) {pos += 1; hasComma = true;}
            if ( l=match_chars(SPACES, s, pos) ) pos += l;
            if ( l=match_char_range(DIGITS_RANGE, s, pos) ) 
            {
                m[2] = s.slice(pos, pos+l);
                pos += l;
            }
            if ( l=match_chars(SPACES, s, pos) ) pos += l;
            if ( (pos < sl) && ('}' === s[CHAR](pos)) )
            {
                pos++;
                m[0] = s.slice(0, pos);
                if ( !hasComma ) m[2] = m[1];
                return m;
            }
            else
            {
                return false;
            }
        }
        return false;
    },
    chargroup = function chargroup( re_obj ) {
        var sequence = [], chars = [], allchars = [], flags = {}, flag, ch, lre,
        prevch, range, isRange = false, m, isUnicode, isHex, escaped = false;
        
        if ( '^' === re_obj.re[CHAR]( re_obj.pos ) )
        {
            flags[ "NegativeMatch" ] = 1;
            re_obj.pos++;
        }
                
        lre = re_obj.len;
        while ( re_obj.pos < lre )
        {
            isUnicode = false;
            isHex = false;
            m = null;
            prevch = ch;
            ch = re_obj.re[CHAR]( re_obj.pos++ );
            
            escaped = ESC === ch;
            if ( escaped ) ch = re_obj.re[CHAR]( re_obj.pos++ );
            
            if ( escaped )
            {
                // unicode character
                if ( 'u' === ch )
                {
                    m = match_unicode( re_obj.re.substr( re_obj.pos-1 ) );
                    re_obj.pos += m[0].length-1;
                    ch = Node(T_UNICODECHAR, m[0], {"Char": fromCharCode(parseInt(m[1], 16)), "Code": m[1]});
                    isUnicode = true; isHex = false;
                }
                
                // hex character
                else if ( 'x' === ch )
                {
                    m = match_hex( re_obj.re.substr( re_obj.pos-1 ) );
                    re_obj.pos += m[0].length-1;
                    ch = Node(T_HEXCHAR, m[0], {"Char": fromCharCode(parseInt(m[1], 16)), "Code": m[1]});
                    isUnicode = true; isHex = true;
                }
            }
            
            if ( isRange )
            {
                if ( chars.length )
                {
                    allchars = allchars.concat( chars );
                    chars = [];
                }
                range[1] = ch;
                isRange = false;
                sequence.push( Node(T_CHARRANGE, range) );
            }
            else
            {
                if ( escaped )
                {
                    if ( isUnicode )
                    {
                        if ( chars.length )
                        {
                            allchars = allchars.concat( chars );
                            chars = [];
                        }
                        sequence.push( ch );
                    }
                    
                    else if ( specialCharsEscaped[HAS](ch) && ('/' !== ch) )
                    {
                        if ( chars.length )
                        {
                            allchars = allchars.concat( chars );
                            chars = [];
                        }
                        flag = {};
                        flag[ specialCharsEscaped[ch] ] = 1;
                        sequence.push( Node(T_SPECIAL, ch, flag) );
                    }
                    
                    else
                    {
                        chars.push( ch );
                    }
                }
                
                else
                {
                    // end of char group
                    if ( ']' === ch )
                    {
                        if ( chars.length )
                        {
                            allchars = allchars.concat( chars );
                            chars = [];
                        }
                        // map all chars into one node
                        if ( allchars.length ) sequence.push( Node(T_CHARS, allchars) );
                        return Node(T_CHARGROUP, sequence, flags);
                    }
                    
                    else if ( '-' === ch )
                    {
                        range = [prevch, ''];
                        if ( prevch instanceof Node ) sequence.pop(); else chars.pop();
                        isRange = true;
                    }
                    
                    else
                    {
                        chars.push( ch );
                    }
                }
            }
        }
        if ( chars.length )
        {
            allchars = allchars.concat( chars );
            chars = [];
        }
        // map all chars into one node
        if ( allchars.length ) sequence.push( Node(T_CHARS, allchars) );
        return Node(T_CHARGROUP, sequence, flags);
    },
    
    analyze_re = function analyze_re( re_obj ) {
        var lre, ch, m, word = '', wordlen = 0,
            alternation = [], sequence = [], flags = {},
            flag, escaped = false, pre, captured;
        
        if ( re_obj.inGroup > 0 )
        {
            pre = re_obj.re.substr(re_obj.pos, 2);
            captured = 1;
            
            if ( "?:" === pre )
            {
                flags[ "NotCaptured" ] = 1;
                re_obj.pos += 2;
                captured = 0;
            }
            
            else if ( "?=" === pre )
            {
                flags[ "LookAhead" ] = 1;
                re_obj.pos += 2;
                captured = 0;
            }
            
            else if ( "?!" === pre )
            {
                flags[ "NegativeLookAhead" ] = 1;
                re_obj.pos += 2;
                captured = 0;
            }
            
            /*else if ( "?^" === pre )
            {
                flags[ "NegativeMatch" ] = 1;
                re_obj.pos += 2;
            }
            
            else if ( "?&" === pre )
            {
                flags[ "LookBehind" ] = 1;
                re_obj.pos += 2;
                captured = 0;
            }*/
            
            else if ( "?<" === pre )
            {
                flags[ "NamedGroup" ] = 1;
                flags[ "GroupName" ] = '';
                re_obj.pos += 2;
                lre = re_obj.len;
                while ( re_obj.pos < lre )
                {
                    ch = re_obj.re[CHAR]( re_obj.pos++ );
                    if ( ">" === ch ) break;
                    flags[ "GroupName" ] += ch;
                }
            }
            
            ++re_obj._groupIndex;
            if ( captured ) flags[ "GroupIndex" ] = ++re_obj.groupIndex;
        }
        
        lre = re_obj.len;
        while ( re_obj.pos < lre )
        {
            ch = re_obj.re[CHAR]( re_obj.pos++ );
            
            //   \\abc
            escaped = ESC === ch;
            if ( escaped ) ch = re_obj.re[CHAR]( re_obj.pos++ );
            
            if ( escaped )
            {
                // unicode character
                if ( 'u' === ch )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    m = match_unicode( re_obj.re.substr( re_obj.pos-1 ) );
                    re_obj.pos += m[0].length-1;
                    sequence.push( Node(T_UNICODECHAR, m[0], {"Char": fromCharCode(parseInt(m[1], 16)), "Code": m[1]}) );
                }
                
                // hex character
                else if ( 'x' === ch )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    m = match_hex( re_obj.re.substr( re_obj.pos-1 ) );
                    re_obj.pos += m[0].length-1;
                    sequence.push( Node(T_HEXCHAR, m[0], {"Char": fromCharCode(parseInt(m[1], 16)), "Code": m[1]}) );
                }
                
                else if ( specialCharsEscaped[HAS](ch) && ('/' !== ch))
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    flag = {};
                    flag[ specialCharsEscaped[ch] ] = 1;
                    sequence.push( Node(T_SPECIAL, ch, flag) );
                }
                
                else
                {
                    word += ch;
                    wordlen += 1;
                }
            }
            
            else
            {
                // group end
                if ( (re_obj.inGroup > 0) && (')' === ch) )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    if ( alternation.length )
                    {
                        alternation.push( Node(T_SEQUENCE, sequence) );
                        sequence = [];
                        flag = {};
                        flag[ specialChars['|'] ] = 1;
                        return Node(T_GROUP, Node(T_ALTERNATION, alternation, flag), flags);
                    }
                    else
                    {
                        return Node(T_GROUP, Node(T_SEQUENCE, sequence), flags);
                    }
                }
                
                // parse alternation
                else if ( '|' === ch )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    alternation.push( Node(T_SEQUENCE, sequence) );
                    sequence = [];
                }
                
                // parse character group
                else if ( '[' === ch )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    sequence.push( chargroup( re_obj ) );
                }
                
                // parse sub-group
                else if ( '(' === ch )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    re_obj.inGroup += 1;
                    sequence.push( analyze_re( re_obj ) );
                    re_obj.inGroup -= 1;
                }
                
                // parse num repeats
                else if ( '{' === ch )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    m = match_repeats( re_obj.re.substr( re_obj.pos-1 ) );
                    re_obj.pos += m[0].length-1;
                    flag = { val: m[0], "MatchMinimum": m[1], "MatchMaximum": m[2] || "unlimited", "min": parseInt(m[1],10), "max": m[2] ? parseInt(m[2],10) : -1 };
                    flag[ specialChars[ch] ] = 1;
                    /*if ( (re_obj.pos < lre) && ('?' === re_obj.re[CHAR](re_obj.pos)) )
                    {
                        flag[ "isGreedy" ] = 0;
                        re_obj.pos++;
                    }
                    else
                    {*/
                        flag[ "isGreedy" ] = 1;
                    /*}*/
                    var prev = sequence.pop();
                    if ( (T_STRING === prev.type) && (prev.val.length > 1) )
                    {
                        sequence.push( Node(T_STRING, prev.val.slice(0, -1)) );
                        prev.val = prev.val.slice(-1);
                    }
                    sequence.push( Node(T_QUANTIFIER, prev, flag) );
                }
                
                // quantifiers
                else if ( ('*' === ch) || ('+' === ch) || ('?' === ch) )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    flag = {};
                    flag[ specialChars[ch] ] = 1;
                    flag["min"] = '+' === ch ? 1 : 0;
                    flag["max"] = '?' === ch ? 1 : -1;
                    if ( (re_obj.pos < lre) && ('?' === re_obj.re[CHAR](re_obj.pos)) )
                    {
                        flag[ "isGreedy" ] = 0;
                        re_obj.pos++;
                    }
                    else
                    {
                        flag[ "isGreedy" ] = 1;
                    }
                    var prev = sequence.pop();
                    if ( (T_STRING === prev.type) && (prev.val.length > 1) )
                    {
                        sequence.push( Node(T_STRING, prev.val.slice(0, -1)) );
                        prev.val = prev.val.slice(-1);
                    }
                    sequence.push( Node(T_QUANTIFIER, prev, flag) );
                }
            
                // special characters like ^, $, ., etc..
                else if ( specialChars[HAS](ch) )
                {
                    if ( wordlen )
                    {
                        sequence.push( Node(T_STRING, word) );
                        word = '';
                        wordlen = 0;
                    }
                    flag = {};
                    flag[ specialChars[ch] ] = 1;
                    sequence.push( Node(T_SPECIAL, ch, flag) );
                }
            
                else
                {
                    word += ch;
                    wordlen += 1;
                }
            }
        }
        
        if ( wordlen )
        {
            sequence.push( Node(T_STRING, word) );
            word = '';
            wordlen = 0;
        }
        
        if ( alternation.length )
        {
            alternation.push( Node(T_SEQUENCE, sequence) );
            sequence = [];
            flag = {};
            flags[ specialChars['|'] ] = 1;
            return Node(T_ALTERNATION, alternation, flag);
        }
        return Node(T_SEQUENCE, sequence);
    }
;

// A simple (js-flavored) regular expression analyzer
var RegexAnalyzer = function RegexAnalyzer( re, delim ) {
    if ( !(this instanceof RegexAnalyzer) ) return new RegexAnalyzer(re, delim);
    if ( re ) this.input( re, delim );
};
RegexAnalyzer.VERSION = __version__;
RegexAnalyzer.Node = Node;
RegexAnalyzer.getCharRange = character_range;
RegexAnalyzer[PROTO] = {
    
    constructor: RegexAnalyzer,

    ast: null,
    re: null,
    fl: null,
    src: null,
    grp: null,
    min: null,
    max: null,
    ch: null,

    dispose: function( ) {
        var self = this;
        self.ast = null;
        self.re = null;
        self.fl = null;
        self.src = null;
        self.grp = null;
        self.min = null;
        self.max = null;
        self.ch = null;
        return self;
    },
    
    reset: function( ) {
        var self = this;
        self.ast = null;
        self.src = null;
        self.grp = null;
        self.min = null;
        self.max = null;
        self.ch = null;
        return self;
    },
    
    input: function( re, delim ) {
        var self = this;
        if ( !arguments.length ) return self.re;
        if ( re )
        {
            delim = delim || '/';
            var src, l, ch, fl = {};
            src = is_regexp(re) ? re.source : null;
            re = re.toString( );
            l = re.length;
            
            // parse re flags, if any
            while ( 0 < l )
            {
                ch = re[CHAR](l-1);
                if ( delim === ch ) break;
                else { fl[ ch ] = 1; l--; }
            }
            
            if ( 0 < l )
            {
                // remove re delimiters
                if ( (delim === re[CHAR](0)) && (delim === re[CHAR](l-1)) ) re = re.slice(1, l-1);
                else re = re.slice(0, l);
            }
            else
            {
                re = '';
            }
            
            // re is different, reset the ast, etc
            if ( self.re !== re ) self.reset();
            self.re = re; self.fl = fl;
            // no need to reconstruct source, it is already regexp
            if ( null !== src ) { self.src = src; self.grp = {}; }
        }
        return self;
    },
    
    analyze: function( ) {
        var self = this;
        if ( (null != self.re) && (null === self.ast) ) self.ast = analyze_re( new RE_OBJ(self.re) );
        return self;
    },
    
    synthesize: function( escaped ) {
        var self = this, state, re;
        if ( null == self.re ) return self;
        if ( null === self.ast )
        {
            self.analyze( );
            self.src = null;
            self.grp = null;
        }
        if ( null === self.src )
        {
            state = {
                map                 : map_src,
                reduce              : reduce_src,
                escaped             : false !== escaped
            };
            re = walk({src:'',group:{}}, self.ast, state);
            self.src = re.src; self.grp = re.group;
        }
        return self;
    },
    
    compile: function( flags ) {
        var self = this, regexp;
        if ( null == self.re ) return null;
        flags = flags || self.fl || {};
        regexp = new RegExp(self.source(), (flags.g||flags.G?'g':'')+(flags.i||flags.I?'i':'')+(flags.m||flags.M?'m':''));
        regexp.$group = self.groups();
        return regexp;
    },
    
    source: function( ) {
        var self = this;
        if ( null == self.re ) return null;
        if ( null === self.src ) self.synthesize();
        return self.src;
    },
    
    groups: function( raw ) {
        var self = this;
        if ( null == self.re ) return null;
        if ( null === self.grp ) self.synthesize();
        return true===raw ? sel.grp : clone(self.grp);
    },
    
    tree: function( flat ) {
        var self = this;
        if ( null == self.re ) return null;
        if ( null === self.ast ) self.analyze( );
        return true===flat ? self.ast.toObject() : self.ast;
    },
    
    // experimental feature
    sample: function( maxlen, numsamples ) {
        var self = this, state;
        if ( null == self.re ) return null;
        if ( null === self.ast ) self.analyze( );
        state = {
            map                 : map_any,
            reduce              : reduce_str,
            maxLength           : (maxlen|0) || 1,
            isCaseInsensitive   : null != self.fl.i
        };
        numsamples = (numsamples|0) || 1;
        if ( 1 < numsamples )
        {
            var samples = new Array(numsamples);
            for(var i=0; i<numsamples; i++) samples[i] = walk('', self.ast, state);
            return samples;
        }
        return walk('', self.ast, state);
    },
    
    // experimental feature
    minimum: function( ) {
        var self = this, state;
        if ( null == self.re ) return 0;
        if ( null === self.ast )
        {
            self.analyze( );
            self.min = null;
        }
        if ( null === self.min )
        {
            state = {
                map                 : map_min,
                reduce              : reduce_len
            };
            self.min = walk(0, self.ast, state)|0;
        }
        return self.min;
    },
    
    // experimental feature
    maximum: function( ) {
        var self = this, state;
        if ( null == self.re ) return 0;
        if ( null === self.ast )
        {
            self.analyze( );
            self.max = null;
        }
        if ( null === self.max )
        {
            state = {
                map                 : map_max,
                reduce              : reduce_len
            };
            self.max = walk(0, self.ast, state);
        }
        return self.max;
    },
    
    // experimental feature
    peek: function( ) {
        var self = this, state, isCaseInsensitive, peek, n, c, p, cases;
        if ( null == self.re ) return null;
        if ( null === self.ast )
        {
            self.analyze( );
            self.ch = null;
        }
        if ( null === self.ch )
        {
            state = {
                map                 : map_1st,
                reduce              : reduce_peek
            };
            self.ch = walk({positive:{},negative:{}}, self.ast, state);
        }
        peek = {positive:clone(self.ch.positive), negative:clone(self.ch.negative)};
        isCaseInsensitive = null != self.fl.i;
        for (n in peek)
        {
            cases = {};
            // either positive or negative
            p = peek[n];
            for (c in p)
            {
                if ('\\d' === c)
                {
                    delete p[c];
                    cases = concat(cases, character_range('0', '9'));
                }
                
                else if ('\\s' === c)
                {
                    delete p[c];
                    cases = concat(cases, ['\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029']);
                }
                
                else if ('\\w' === c)
                {
                    delete p[c];
                    cases = concat(cases, ['_'].concat(character_range('0', '9')).concat(character_range('a', 'z')).concat(character_range('A', 'Z')));
                }
                
                else if ('\\.' === c)
                {
                    delete p[c];
                    cases[ specialChars['.'] ] = 1;
                }
                
                /*else if ('\\^' === c)
                {
                    delete p[c];
                    cases[ specialChars['^'] ] = 1;
                }
                
                else if ('\\$' === c)
                {
                    delete p[c];
                    cases[ specialChars['$'] ] = 1;
                }*/
                
                else if ( '\\' !== c[CHAR](0) && isCaseInsensitive )
                {
                    cases[ c.toLowerCase() ] = 1;
                    cases[ c.toUpperCase() ] = 1;
                }
                
                else if ( '\\' === c[CHAR](0) )
                {
                    delete p[c];
                }
            }
            peek[n] = concat(p, cases);
        }
        return peek;
    }
};
// alias
RegexAnalyzer[PROTO].set = RegexAnalyzer[PROTO].input;

// custom method to access named groups feature, if any
RegExp[PROTO].$group = null;
RegExp[PROTO].group = function( group ){
    group = group || 0;
    return this.$group && this.$group.hasOwnProperty(group) ? this.$group[group] : group;
};

/* export the module */
return RegexAnalyzer;
});