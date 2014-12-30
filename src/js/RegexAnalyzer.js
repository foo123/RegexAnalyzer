/**
*
*   RegexAnalyzer
*   @version: 0.4.4
*
*   A simple Regular Expression Analyzer for PHP, Python, Node/JS, ActionScript
*   https://github.com/foo123/RegexAnalyzer
*
**/
!function( root, name, factory ) {
    "use strict";
    
    //
    // export the module, umd-style (no other dependencies)
    var isCommonJS = ("object" === typeof(module)) && module.exports, 
        isAMD = ("function" === typeof(define)) && define.amd, m;
    
    // CommonJS, node, etc..
    if ( isCommonJS ) 
        module.exports = (module.$deps = module.$deps || {})[ name ] = module.$deps[ name ] || (factory.call( root, {NODE:module} ) || 1);
    
    // AMD, requireJS, etc..
    else if ( isAMD && ("function" === typeof(require)) && ("function" === typeof(require.specified)) && require.specified(name) ) 
        define( name, ['require', 'exports', 'module'], function( require, exports, module ){ return factory.call( root, {AMD:module} ); } );
    
    // browser, web worker, etc.. + AMD, other loaders
    else if ( !(name in root) ) 
        (root[ name ] = (m=factory.call( root, {} ) || 1)) && isAMD && define( name, [], function( ){ return m; } );


}(  /* current root */          this, 
    /* module name */           "RegexAnalyzer",
    /* module factory */        function( exports, undef ) {
        
    "use strict";
    /* main code starts here */
    var __version__ = "0.4.4",
    
        PROTO = 'prototype', Obj = Object, Arr = Array, /*Str = String,*/ 
        Keys = Obj.keys, to_string = Obj[PROTO].toString, 
        fromCharCode = String.fromCharCode, CHAR = 'charAt', CHARCODE = 'charCodeAt',
        INF = Infinity, HAS = 'hasOwnProperty',
        
        escapeChar = '\\',
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
        T_CHARRANGE = 10, T_STRING = 11,
        
        rnd = function( a, b ){ return Math.round((b-a)*Math.random()+a); },
        char_code = function( c ) { return c[CHARCODE](0); },
        char_code_range = function( s ) { return [s[CHARCODE](0), s[CHARCODE](s.length-1)]; },
        //char_codes = function( s_or_a ) { return (s_or_a.substr ? s_or_a.split("") : s_or_a).map( char_code ); },
        // http://stackoverflow.com/questions/12376870/create-an-array-of-characters-from-specified-range
        character_range = function(first, last) {
            if ( first && ('function' === typeof(first.push)) )
            {
                last = first[1];
                first = first[0];
            }
            var ch, chars, start = first[CHARCODE](0), end = last[CHARCODE](0);
            
            if ( end == start ) return [ fromCharCode( start ) ];
            
            chars = [];
            for (ch = start; ch <= end; ++ch) chars.push( fromCharCode( ch ) );
            return chars;
        },
        concat = function(p1, p2) {
            if ( p2 )
            {
                var p, l;
                if ( 'function' === typeof(p2.push) )
                {
                    for (p=0,l=p2.length; p<l; p++)
                    {
                        p1[p2[p]] = 1;
                    }
                }
                else
                {
                    for (p in p2)
                    {
                        if ( p2[HAS](p) ) p1[p] = 1;
                    }
                }
            }
            return p1;
        },
        
        BSPACES = "\r\n",
        SPACES = " \t\v",
        PUNCTS = "~!@#$%^&*()-+=[]{}\\|;:,./<>?",
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
        /*match_non_chars = function( CHARS, s, pos, minlen, maxlen ) {
            pos = pos || 0;
            minlen = minlen || 1;
            maxlen = maxlen || INF;
            var lp = pos, l = 0, sl = s.length, ch;
            while ( (lp < sl) && (l <= maxlen) && 0 > CHARS.indexOf( ch=s[CHAR](lp) ) ) 
            { 
                lp++; l++; 
            }
            return l >= minlen ? l : false;
        },*/
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
        /*match_non_char_range = function( RANGE, s, pos, minlen, maxlen ) {
            pos = pos || 0;
            minlen = minlen || 1;
            maxlen = maxlen || INF;
            var lp = pos, l = 0, sl = s.length, ch;
            while ( (lp < sl) && (l <= maxlen) && ((ch=s[CHARCODE](lp)) < RANGE[0] || ch > RANGE[1]) ) 
            { 
                lp++; l++;
            }
            return l >= minlen ? l : false;
        },*/
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
        /*match_non_char_ranges = function( RANGES, s, pos, minlen, maxlen ) {
            pos = pos || 0;
            minlen = minlen || 1;
            maxlen = maxlen || INF;
            var lp = pos, l = 0, sl = s.length, ch, 
                i, Rl = RANGES.length, RANGE, notfound = true;
            while ( (lp < sl) && (l <= maxlen) && notfound ) 
            { 
                ch = s[CHARCODE](lp);
                for (i=0; i<Rl; i++)
                {
                    RANGE = RANGES[i];
                    if ( ch >= RANGE[0] && ch <= RANGE[1] )
                    {
                        lp++; l++; notfound = false;
                        break;
                    }
                }
            }
            return l >= minlen ? l : false;
        },*/
        /*match_literal = function( lit, s, pos, caseInsensitive ) {
            var lp = pos, l = 0, mlen = lit.length, sl = s.length;
            if ( caseInsensitive )
            {
                while ( (lp < sl) && (l <= mlen) && (lit[CHAR](l).toLowerCase() === s[CHAR](lp).toLowerCase()) ) 
                { 
                    lp++; l++; 
                }
            }
            else
            {
                while ( (lp < sl) && (l <= mlen) && (lit[CHAR](l) === s[CHAR](lp)) ) 
                { 
                    lp++; l++; 
                }
            }
            return l === mlen;
        },*/
        // TODO, generate RE matcher for given RE and string
        /*match = function match( s, pos, part, isCaseInsensitive ) {
            var m = false, p, i, l, type;
            
            type = part.type;
            // walk the sequence
            if ( "Alternation" == type )
            {
                for (i=0; i<part.part.length; i++)
                {
                    if ( m = match(s, pos, part.part[i], isCaseInsensitive) )
                    {
                        break;
                    }
                }
            }
            
            else if ( "Group" == type )
            {
                m = match(s, pos, part.part, isCaseInsensitive);
            }
            
            else if ( "Sequence" == type )
            {
                var repeat, mmin, mmax;
                l = part.part.length;
                p = part.part[i];
                for (i=0; i<l; i++)
                {
                    p = part.part[i];
                    if ( !p ) continue;
                    repeat = 1;
                    if ( "Quantifier" == p.type )
                    {
                        if ( p.flags.MatchZeroOrMore ) repeat = rnd(0, 10);
                        else if ( p.flags.MatchZeroOrOne ) repeat = rnd(0, 1);
                        else if ( p.flags.MatchOneOrMore ) repeat = rnd(1, 11);
                        else 
                        {
                            mmin = parseInt(p.flags.MatchMinimum, 10);
                            mmax = parseInt(p.flags.MatchMaximum, 10);
                            repeat = rnd(mmin, isNaN(mmax) ? (mmin+10) : mmax);
                        }
                        while ( repeat > 0 ) 
                        {
                            repeat--;
                            sample += generate( p.part, isCaseInsensitive );
                        }
                    }
                    else if ( "Special" == p.type )
                    {
                        if ( p.flags.MatchAnyChar ) sample += any( );
                    }
                    else
                    {
                        sample += generate( p, isCaseInsensitive );
                    }
                }
            }
            
            else if ( "CharGroup" == type )
            {
                var chars = [], ptype;
                
                for (i=0, l=part.part.length; i<l; i++)
                {
                    p = part.part[i];
                    ptype = p.type;
                    if ( "Chars" == ptype )
                    {
                        m = match_chars(isCaseInsensitive ? p.part.toLowerCase()+p.part.toUpperCase() : p.part, s, pos);
                    }
                    
                    else if ( "CharRange" == ptype )
                    {
                        m = match_char_range(char_code_range(p.part.join("")), s, pos);
                    }
                    
                    else if ( "UnicodeChar" == ptype || "HexChar" == ptype )
                    {
                        m = match_chars(isCaseInsensitive ? p.flags.Char.toLowerCase()+p.flags.Char.toUpperCase() : p.flags.Char, s, pos);
                    }
                    
                    else if ( "Special" == ptype )
                    {
                        if ('D' == p.part)
                        {
                            m = match_non_char_range(DIGITS_RANGE, s, pos);
                        }
                        else if ('W' == p.part)
                        {
                            m = match_non_char_ranges(WORD_RANGES, s, pos);
                        }
                        else if ('S' == p.part)
                        {
                            m = match_non_chars(SPACES, s, pos);
                        }
                        else if ('d' == p.part)
                        {
                            m = match_char_range(DIGITS_RANGE, s, pos);
                        }
                        else if ('w' == p.part)
                        {
                            m = match_char_ranges(WORD_RANGES, s, pos);
                        }
                        else if ('s' == p.part)
                        {
                            m = match_chars(SPACES, s, pos);
                        }
                        else
                        {
                            m = match_chars('\\' + p.part, s, pos);
                        }
                    }
                }
            }
            
            else if ( "String" == type )
            {
                m = match_literal( part.part, s, pos, isCaseInsensitive );
            }
            
            else if ( "Special" == type && !part.flags.MatchStart && !part.flags.MatchEnd )
            {
                if ('D' == part.part)
                {
                    m = match_non_char_range(DIGITS_RANGE, s, pos);
                }
                else if ('W' == part.part)
                {
                    m = match_non_char_ranges(WORD_RANGES, s, pos);
                }
                else if ('S' == part.part)
                {
                    m = match_non_chars(SPACES, s, pos);
                }
                else if ('d' == part.part)
                {
                    m = match_char_range(DIGITS_RANGE, s, pos);
                }
                else if ('w' == part.part)
                {
                    m = match_char_ranges(WORD_RANGES, s, pos);
                }
                else if ('s' == part.part)
                {
                    m = match_chars(SPACES, s, pos);
                }
                else if ('.' == part.part)
                {
                    m = match_chars(ALL, s, pos);
                }
                else
                {
                    m = match_chars('\\' + part.part, s, pos);
                }
            }
                    
            else if ( "UnicodeChar" == type || "HexChar" == type )
            {
                sample += isCaseInsensitive ? case_insensitive( part.flags.Char ) : part.flags.Char;
            }
            
            return m;
        },*/

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
        random_upper_or_lower = function( c ) { return rnd(0,1) ? c.toLowerCase( ) : c.toUpperCase( ); },
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
        generate = function generate( part, isCaseInsensitive ) {
            var sample = '', p, i, l, type;
            
            type = part.type;
            // walk the sequence
            if ( T_ALTERNATION === type )
            {
                sample += generate( part.part[rnd(0, part.part.length-1)], isCaseInsensitive );
            }
            
            else if ( T_GROUP === type )
            {
                sample += generate( part.part, isCaseInsensitive );
            }
            
            else if ( T_SEQUENCE === type )
            {
                var repeat, mmin, mmax;
                l = part.part.length;
                p = part.part[i];
                for (i=0; i<l; i++)
                {
                    p = part.part[i];
                    if ( !p ) continue;
                    repeat = 1;
                    if ( T_QUANTIFIER === p.type )
                    {
                        if ( p.flags.MatchZeroOrMore ) repeat = rnd(0, 10);
                        else if ( p.flags.MatchZeroOrOne ) repeat = rnd(0, 1);
                        else if ( p.flags.MatchOneOrMore ) repeat = rnd(1, 11);
                        else 
                        {
                            mmin = parseInt(p.flags.MatchMinimum, 10);
                            mmax = parseInt(p.flags.MatchMaximum, 10);
                            repeat = rnd(mmin, isNaN(mmax) ? (mmin+10) : mmax);
                        }
                        while ( repeat > 0 ) 
                        {
                            repeat--;
                            sample += generate( p.part, isCaseInsensitive );
                        }
                    }
                    else if ( T_SPECIAL === p.type )
                    {
                        if ( p.flags.MatchAnyChar ) sample += any( );
                    }
                    else
                    {
                        sample += generate( p, isCaseInsensitive );
                    }
                }
            }
            
            else if ( T_CHARGROUP === type )
            {
                var chars = [], ptype;
                
                for (i=0, l=part.part.length; i<l; i++)
                {
                    p = part.part[i];
                    ptype = p.type;
                    if ( T_CHARS === ptype )
                    {
                        chars = chars.concat( isCaseInsensitive ? case_insensitive( p.part, true ) : p.part );
                    }
                    
                    else if ( T_CHARRANGE === ptype )
                    {
                        chars = chars.concat( isCaseInsensitive ? case_insensitive( character_range(p.part), true ) : character_range(p.part) );
                    }
                    
                    else if ( T_UNICODECHAR === ptype || T_HEXCHAR === ptype )
                    {
                        chars.push( isCaseInsensitive ? case_insensitive( p.flags.Char ): p.flags.Char );
                    }
                    
                    else if ( T_SPECIAL === ptype )
                    {
                        var p_part = p.part;
                        if ('D' == p_part)
                        {
                            chars.push( digit( false ) );
                        }
                        else if ('W' == p_part)
                        {
                            chars.push( word( false ) );
                        }
                        else if ('S' == p_part)
                        {
                            chars.push( space( false ) );
                        }
                        else if ('d' == p_part)
                        {
                            chars.push( digit( ) );
                        }
                        else if ('w' == p_part)
                        {
                            chars.push( word( ) );
                        }
                        else if ('s' == p_part)
                        {
                            chars.push( space( ) );
                        }
                        else
                        {
                            chars.push( '\\' + p_part );
                        }
                    }
                }
                sample += character(chars, !part.flags.NotMatch);
            }
            
            else if ( T_STRING === type )
            {
                sample += isCaseInsensitive ? case_insensitive( part.part ) : part.part;
            }
            
            else if ( T_SPECIAL === type && !part.flags.MatchStart && !part.flags.MatchEnd )
            {
                var p_part = part.part;
                if ('D' == p_part)
                {
                    sample += digit( false );
                }
                else if ('W' == p_part)
                {
                    sample += word( false );
                }
                else if ('S' == p_part)
                {
                    sample += space( false );
                }
                else if ('d' == p_part)
                {
                    sample += digit( );
                }
                else if ('w' == p_part)
                {
                    sample += word( );
                }
                else if ('s' == p_part)
                {
                    sample += space( );
                }
                else if ('.' == p_part)
                {
                    sample += any( );
                }
                else
                {
                    sample += '\\' + p_part;
                }
            }
                    
            else if ( T_UNICODECHAR === type || T_HEXCHAR === type )
            {
                sample += isCaseInsensitive ? case_insensitive( part.flags.Char ) : part.flags.Char;
            }
            
            return sample;
        },

        peek_characters = function peek_characters( part ) {
            var peek = {}, negativepeek = {}, current, p, i, l, 
                tmp, done, type, ptype;
            
            type = part.type;
            // walk the sequence
            if ( T_ALTERNATION === type )
            {
                for (i=0, l=part.part.length; i<l; i++)
                {
                    tmp = peek_characters( part.part[i] );
                    peek = concat( peek, tmp.peek );
                    negativepeek = concat( negativepeek, tmp.negativepeek );
                }
            }
            
            else if ( T_GROUP === type )
            {
                tmp = peek_characters( part.part );
                peek = concat( peek, tmp.peek );
                negativepeek = concat( negativepeek, tmp.negativepeek );
            }
            
            else if ( T_SEQUENCE === type )
            {
                i = 0;
                l = part.part.length;
                p = part.part[i];
                done = ( 
                    i >= l || !p || T_QUANTIFIER != p.type || 
                    ( !p.flags.MatchZeroOrMore && !p.flags.MatchZeroOrOne && "0"!=p.flags.MatchMinimum ) 
                );
                while ( !done )
                {
                    tmp = peek_characters( p.part );
                    peek = concat( peek, tmp.peek );
                    negativepeek = concat( negativepeek, tmp.negativepeek );
                    
                    i++;
                    p = part.part[i];
                    
                    done = ( 
                        i >= l || !p || T_QUANTIFIER != p.type || 
                        ( !p.flags.MatchZeroOrMore && !p.flags.MatchZeroOrOne && "0"!=p.flags.MatchMinimum ) 
                    );
                }
                if ( i < l )
                {
                    p = part.part[i];
                    
                    if (T_SPECIAL === p.type && ('^'==p.part || '$'==p.part)) p = part.part[i+1] || null;
                    
                    if (p && T_QUANTIFIER === p.type) p = p.part;
                    
                    if (p)
                    {
                        tmp = peek_characters( p );
                        peek = concat( peek, tmp.peek );
                        negativepeek = concat( negativepeek, tmp.negativepeek );
                    }
                }
            }
            
            else if ( T_CHARGROUP === type )
            {
                current = ( part.flags.NotMatch ) ? negativepeek : peek;
                
                for (i=0, l=part.part.length; i<l; i++)
                {
                    p = part.part[i];
                    ptype = p.type;
                    if ( T_CHARS === ptype )
                    {
                        current = concat( current, p.part );
                    }
                    
                    else if ( T_CHARRANGE === ptype )
                    {
                        current = concat( current, character_range(p.part) );
                    }
                    
                    else if ( T_UNICODECHAR === ptype || T_HEXCHAR === ptype )
                    {
                        current[p.flags.Char] = 1;
                    }
                    
                    else if ( T_SPECIAL === ptype )
                    {
                        var p_part = p.part;
                        if ('D' == p_part)
                        {
                            if (part.flags.NotMatch)
                                peek[ '\\d' ] = 1;
                            else
                                negativepeek[ '\\d' ] = 1;
                        }
                        else if ('W' == p_part)
                        {
                            if (part.flags.NotMatch)
                                peek[ '\\w' ] = 1;
                            else
                                negativepeek[ '\\W' ] = 1;
                        }
                        else if ('S' == p_part)
                        {
                            if (part.flags.NotMatch)
                                peek[ '\\s' ] = 1;
                            else
                                negativepeek[ '\\s' ] = 1;
                        }
                        else
                        {
                            current['\\' + p_part] = 1;
                        }
                    }
                }
            }
            
            else if ( T_STRING === type )
            {
                peek[part.part[CHAR](0)] = 1;
            }
            
            else if ( T_SPECIAL === type && !part.flags.MatchStart && !part.flags.MatchEnd )
            {
                if ('D' == part.part)
                {
                    negativepeek[ '\\d' ] = 1;
                }
                else if ('W' == part.part)
                {
                    negativepeek[ '\\W' ] = 1;
                }
                else if ('S' == part.part)
                {
                    negativepeek[ '\\s' ] = 1;
                }
                else
                {
                    peek['\\' + part.part] = 1;
                }
            }
                    
            else if ( T_UNICODECHAR === type || T_HEXCHAR === type )
            {
                peek[part.flags.Char] = 1;
            }
            
            return { peek: peek, negativepeek: negativepeek };
        },
        
        //hexRegex = /^x([0-9a-fA-F]{2})/,
        match_hex = function( s ) {
            var m = false;
            if ( s.length > 2 && 'x' === s[CHAR](0) )
            {
                if ( match_char_ranges(HEXDIGITS_RANGES, s, 1, 2, 2) ) return [m=s.slice(0,3), m.slice(1)];
            }
            return false;
        },
        //unicodeRegex = /^u([0-9a-fA-F]{4})/,
        match_unicode = function( s ) {
            var m = false;
            if ( s.length > 4 && 'u' === s[CHAR](0) )
            {
                if ( match_char_ranges(HEXDIGITS_RANGES, s, 1, 4, 4) ) return [m=s.slice(0,5), m.slice(1)];
            }
            return false;
        },
        //repeatsRegex = /^\{\s*(\d+)\s*,?\s*(\d+)?\s*\}/,
        match_repeats = function( s ) {
            var l, sl = s.length, pos = 0, m = false;
            if ( sl > 2 && '{' === s[CHAR](pos) )
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
                if ( pos < sl && ',' === s[CHAR](pos) ) pos += 1;
                if ( l=match_chars(SPACES, s, pos) ) pos += l;
                if ( l=match_char_range(DIGITS_RANGE, s, pos) ) 
                {
                    m[2] = s.slice(pos, pos+l);
                    pos += l;
                }
                if ( l=match_chars(SPACES, s, pos) ) pos += l;
                if ( pos < sl && '}' === s[CHAR](pos) )
                {
                    pos++;
                    m[0] = s.slice(0, pos);
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
            var sequence = [], chars = [], flags = {}, flag, ch, lre,
            prevch, range, isRange = false, m, isUnicode, escaped = false;
            
            if ( '^' == re_obj.re[CHAR]( re_obj.pos ) )
            {
                flags[ "NotMatch" ] = 1;
                re_obj.pos++;
            }
                    
            lre = re_obj.len;
            while ( re_obj.pos < lre )
            {
                isUnicode = false;
                prevch = ch;
                ch = re_obj.re[CHAR]( re_obj.pos++ );
                
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped ) ch = re_obj.re[CHAR]( re_obj.pos++ );
                
                if ( escaped )
                {
                    // unicode character
                    if ( 'u' == ch )
                    {
                        m = match_unicode( re_obj.re.substr( re_obj.pos-1 ) );
                        re_obj.pos += m[0].length-1;
                        ch = fromCharCode(parseInt(m[1], 16));
                        isUnicode = true;
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        m = match_hex( re_obj.re.substr( re_obj.pos-1 ) );
                        re_obj.pos += m[0].length-1;
                        ch = fromCharCode(parseInt(m[1], 16));
                        isUnicode = true;
                    }
                }
                
                if ( isRange )
                {
                    if ( chars.length )
                    {
                        sequence.push( { part: chars, flags: {}, typeName: "Chars", type: T_CHARS } );
                        chars = [];
                    }
                    range[1] = ch;
                    isRange = false;
                    sequence.push( { part: range, flags: {}, typeName: "CharRange", type: T_CHARRANGE } );
                }
                else
                {
                    if ( escaped )
                    {
                        if ( !isUnicode && specialCharsEscaped[HAS](ch) && '/' != ch)
                        {
                            if ( chars.length )
                            {
                                sequence.push( { part: chars, flags: {}, typeName: "Chars", type: T_CHARS } );
                                chars = [];
                            }
                            flag = {};
                            flag[ specialCharsEscaped[ch] ] = 1;
                            sequence.push( { part: ch, flags: flag, typeName: "Special", type: T_SPECIAL } );
                        }
                        
                        else
                        {
                            chars.push( ch );
                        }
                    }
                    
                    else
                    {
                        // end of char group
                        if ( ']' == ch )
                        {
                            if ( chars.length )
                            {
                                sequence.push( { part: chars, flags: {}, typeName: "Chars", type: T_CHARS } );
                                chars = [];
                            }
                            return { part: sequence, flags: flags, typeName: "CharGroup", type: T_CHARGROUP };
                        }
                        
                        else if ( '-' == ch )
                        {
                            range = [prevch, ''];
                            chars.pop();
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
                sequence.push( { part: chars, flags: {}, typeName: "Chars", type: T_CHARS } );
                chars = [];
            }
            return { part: sequence, flags: flags, typeName: "CharGroup", type: T_CHARGROUP };
        },
        
        analyze_re = function analyze_re( re_obj ) {
            var lre, ch, m, word = '', wordlen = 0,
                alternation = [], sequence = [], flags = {},
                flag, escaped = false, pre;
            
            if ( re_obj.inGroup > 0 )
            {
                pre = re_obj.re.substr(re_obj.pos, 2);
                
                if ( "?:" == pre )
                {
                    flags[ "NotCaptured" ] = 1;
                    re_obj.pos += 2;
                }
                
                else if ( "?=" == pre )
                {
                    flags[ "LookAhead" ] = 1;
                    re_obj.pos += 2;
                }
                
                else if ( "?!" == pre )
                {
                    flags[ "NegativeLookAhead" ] = 1;
                    re_obj.pos += 2;
                }
                
                flags[ "GroupIndex" ] = ++re_obj.groupIndex;
            }
            
            lre = re_obj.len;
            while ( re_obj.pos < lre )
            {
                ch = re_obj.re[CHAR]( re_obj.pos++ );
                
                //   \\abc
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped ) ch = re_obj.re[CHAR]( re_obj.pos++ );
                
                if ( escaped )
                {
                    // unicode character
                    if ( 'u' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        m = match_unicode( re_obj.re.substr( re_obj.pos-1 ) );
                        re_obj.pos += m[0].length-1;
                        sequence.push( { part: m[0], flags: { "Char": fromCharCode(parseInt(m[1], 16)), "Code": m[1] }, typeName: "UnicodeChar", type: T_UNICODECHAR } );
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        m = match_hex( re_obj.re.substr( re_obj.pos-1 ) );
                        re_obj.pos += m[0].length-1;
                        sequence.push( { part: m[0], flags: { "Char": fromCharCode(parseInt(m[1], 16)), "Code": m[1] }, typeName: "HexChar", type: T_HEXCHAR } );
                    }
                    
                    else if ( specialCharsEscaped[HAS](ch) && '/' != ch)
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        flag = {};
                        flag[ specialCharsEscaped[ch] ] = 1;
                        sequence.push( { part: ch, flags: flag, typeName: "Special", type: T_SPECIAL } );
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
                    if ( re_obj.inGroup > 0 && ')' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        if ( alternation.length )
                        {
                            alternation.push( { part: sequence, flags: {}, typeName: "Sequence", type: T_SEQUENCE } );
                            sequence = [];
                            flag = {};
                            flag[ specialChars['|'] ] = 1;
                            return { part: { part: alternation, flags: flag, typeName: "Alternation", type: T_ALTERNATION }, flags: flags, typeName: "Group", type: T_GROUP };
                        }
                        else
                        {
                            return { part: { part: sequence, flags: {}, typeName: "Sequence", type: T_SEQUENCE }, flags: flags, typeName: "Group", type: T_GROUP };
                        }
                    }
                    
                    // parse alternation
                    else if ( '|' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        alternation.push( { part: sequence, flags: {}, typeName: "Sequence", type: T_SEQUENCE } );
                        sequence = [];
                    }
                    
                    // parse character group
                    else if ( '[' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        sequence.push( chargroup( re_obj ) );
                    }
                    
                    // parse sub-group
                    else if ( '(' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        re_obj.inGroup+=1;
                        sequence.push( analyze_re( re_obj ) );
                        re_obj.inGroup-=1;
                    }
                    
                    // parse num repeats
                    else if ( '{' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        m = match_repeats( re_obj.re.substr( re_obj.pos-1 ) );
                        re_obj.pos += m[0].length-1;
                        flag = { part: m[0], "MatchMinimum": m[1], "MatchMaximum": m[2] || "unlimited" };
                        flag[ specialChars[ch] ] = 1;
                        if ( re_obj.pos < lre && '?' == re_obj.re[CHAR](re_obj.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            re_obj.pos++;
                        }
                        else
                        {
                            flag[ "isGreedy" ] = 1;
                        }
                        var prev = sequence.pop();
                        if ( T_STRING === prev.type && prev.part.length > 1 )
                        {
                            sequence.push( { part: prev.part.slice(0, -1), flags: {}, typeName: "String", type: T_STRING } );
                            prev.part = prev.part.slice(-1);
                        }
                        sequence.push( { part: prev, flags: flag, typeName: "Quantifier", type: T_QUANTIFIER } );
                    }
                    
                    // quantifiers
                    else if ( '*' == ch || '+' == ch || '?' == ch )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        flag = {};
                        flag[ specialChars[ch] ] = 1;
                        if ( re_obj.pos < lre && '?' == re_obj.re[CHAR](re_obj.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            re_obj.pos++;
                        }
                        else
                        {
                            flag[ "isGreedy" ] = 1;
                        }
                        var prev = sequence.pop();
                        if ( T_STRING === prev.type && prev.part.length > 1 )
                        {
                            sequence.push( { part: prev.part.slice(0, -1), flags: {}, typeName: "String", type: T_STRING } );
                            prev.part = prev.part.slice(-1);
                        }
                        sequence.push( { part: prev, flags: flag, typeName: "Quantifier", type: T_QUANTIFIER } );
                    }
                
                    // special characters like ^, $, ., etc..
                    else if ( specialChars[HAS](ch) )
                    {
                        if ( wordlen )
                        {
                            sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                            word = '';
                            wordlen = 0;
                        }
                        flag = {};
                        flag[ specialChars[ch] ] = 1;
                        sequence.push( { part: ch, flags: flag, typeName: "Special", type: T_SPECIAL } );
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
                sequence.push( { part: word, flags: {}, typeName: "String", type: T_STRING } );
                word = '';
                wordlen = 0;
            }
            
            if ( alternation.length )
            {
                alternation.push( { part: sequence, flags: {}, typeName: "Sequence", type: T_SEQUENCE } );
                sequence = [];
                flag = {};
                flags[ specialChars['|'] ] = 1;
                return { part: alternation, flags: flag, typeName: "Alternation", type: T_ALTERNATION };
            }
            return { part: sequence, flags: {}, typeName: "Sequence", type: T_SEQUENCE };
        }
    ;

    // A simple (js-flavored) regular expression analyzer
    var Analyzer = function Analyzer( regex, delim ) {
        if ( !(this instanceof Analyzer) ) return new Analyzer(regex, delim);
        if ( regex ) this.regex( regex, delim );
    };
    Analyzer.VERSION = __version__;
    Analyzer.getCharRange = character_range;
    Analyzer[PROTO] = {
        
        constructor: Analyzer,

        _regex: null,
        _flags: null,
        _parts: null,
        _needsRefresh: false,

        dispose: function( ) {
            var self = this;
            self._regex = null;
            self._flags = null;
            self._parts = null;
            return self;
        },
        
        regex: function( regex, delim ) {
            var self = this;
            if ( regex )
            {
                delim = delim || '/';
                var flags = {}, r = regex.toString( ), l = r.length, ch = r[CHAR](l-1);
                
                // parse regex flags
                while ( delim !== ch )
                {
                    flags[ ch ] = 1;
                    r = r.slice(0, -1);
                    l = r.length;
                    ch = r[CHAR](l-1);
                }
                // remove regex delimiters
                if ( delim == r[CHAR](0) && delim == r[CHAR](l-1) )  r = r.slice(1, -1);
                
                if ( self._regex !== r ) self._needsRefresh = true;
                self._regex = r; self._flags = flags;
            }
            return self;
        },
        
        getRegex: function( ) {
            return new RegExp(this._regex, Keys(this._flags).join(''));
        },
        
        getParts: function( ) {
            var self = this;
            if ( self._needsRefresh ) self.analyze( );
            return self._parts;
        },
        
        analyze: function( ) {
            var self = this;
            if ( self._needsRefresh )
            {
                self._parts = analyze_re( {re: self._regex, len: self._regex.length, pos: 0, groupIndex: 0, inGroup: 0} );
                self._needsRefresh = false;
            }
            return self;
        },
        
        // experimental feature
        sample: function( ) {
            var self = this;
            if ( self._needsRefresh ) self.analyze( );
            return generate( self._parts, self._flags && self._flags.i );
        },
        
        // experimental feature, implement (optimised) RE matching as well
        match: function( str ) {
            //return match( self._parts, str, 0, self._flags && self._flags.i );
            return false;
        },
        
        // experimental feature
        peek: function( ) {
            var self = this, isCaseInsensitive,
                peek, n, c, p, cases;
            
            if ( self._needsRefresh ) self.analyze( );
            
            peek = peek_characters( self._parts );
            isCaseInsensitive = self._flags && self._flags.i;
            
            for (n in peek)
            {
                cases = {};
                // either peek or negativepeek
                p = peek[n];
                for (c in p)
                {
                    if ('\\d' == c)
                    {
                        delete p[c];
                        cases = concat(cases, character_range('0', '9'));
                    }
                    
                    else if ('\\s' == c)
                    {
                        delete p[c];
                        cases = concat(cases, ['\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029']);
                    }
                    
                    else if ('\\w' == c)
                    {
                        delete p[c];
                        cases = concat(cases, ['_'].concat(character_range('0', '9')).concat(character_range('a', 'z')).concat(character_range('A', 'Z')));
                    }
                    
                    else if ('\\.' == c)
                    {
                        delete p[c];
                        cases[ specialChars['.'] ] = 1;
                    }
                    
                    /*else if ('\\^' == c)
                    {
                        delete p[c];
                        cases[ specialChars['^'] ] = 1;
                    }
                    
                    else if ('\\$' == c)
                    {
                        delete p[c];
                        cases[ specialChars['$'] ] = 1;
                    }*/
                    
                    else if ( '\\' != c[CHAR](0) && isCaseInsensitive )
                    {
                        cases[ c.toLowerCase() ] = 1;
                        cases[ c.toUpperCase() ] = 1;
                    }
                    
                    else if ( '\\' == c[CHAR](0) )
                    {
                        delete p[c];
                    }
                }
                peek[n] = concat(p, cases);
            }
            return peek;
        }
    };
    // aliases
    Analyzer[PROTO].getPeekChars = Analyzer[PROTO].peek;
    Analyzer[PROTO].generateSample = Analyzer[PROTO].sample;
    
    /* main code ends here */
    /* export the module */
    return Analyzer;
});