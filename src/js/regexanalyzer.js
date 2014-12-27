/**
*
*   RegExAnalyzer
*   @version: 0.4.3
*
*   A simple Regular Expression Analyzer for PHP, Python, Node/JS
*   https://github.com/foo123/regex-analyzer
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
    /* module name */           "RegExAnalyzer",
    /* module factory */        function( exports, undef ) {
        
    "use strict";
    /* main code starts here */
    var __version__ = "0.4.3",
    
        PROTO = 'prototype', Obj = Object, Arr = Array, /*Str = String,*/ 
        Keys = Obj.keys, to_string = Obj[PROTO].toString, fromCharCode = String.fromCharCode,
        
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

        rnd = function( a, b ){ return Math.round((b-a)*Math.random()+a); },
        
        // http://stackoverflow.com/questions/12376870/create-an-array-of-characters-from-specified-range
        character_range = function(first, last) {
            if ( first && ( first instanceof Arr || "[object Array]" == to_string.call(first) ) )
            {
                last = first[1];
                first = first[0];
            }
            var ch, chars, start = first.charCodeAt(0), end = last.charCodeAt(0);
            
            if ( end == start ) return [ fromCharCode( start ) ];
            
            chars = [];
            for (ch = start; ch <= end; ++ch)
                chars.push( fromCharCode( ch ) );
            
            return chars;
        },
        
        BSPACES = "\r\n",
        SPACES = " \t\v",
        PUNCTS = "~!@#$%^&*()-+=[]{}\\|;:,./<>?",
        DIGITS = "0123456789",
        HEXDIGITS = DIGITS+"abcdef"+"ABCDEF",
        ALPHAS = "_"+(character_range("a", "z").join(""))+(character_range("A", "Z").join("")),
        ALL = SPACES+PUNCTS+DIGITS+ALPHAS, ALL_ARY = ALL.split(""),
        punct = function( ){ 
            return PUNCTS.charAt(rnd(0, PUNCTS.length-1)); 
        },
        space = function( positive ){ 
            return false !== positive 
                ? SPACES.charAt(rnd(0, SPACES.length-1))
                : (punct()+digit()+alpha()).charAt(rnd(0,2))
            ; 
        },
        digit = function( positive ){ 
            return false !== positive 
                ? DIGITS.charAt(rnd(0, DIGITS.length-1))
                : (punct()+space()+alpha()).charAt(rnd(0,2))
            ; 
        },
        alpha = function( positive ){ 
            return false !== positive 
                ? ALPHAS.charAt(rnd(0, ALPHAS.length-1))
                : (punct()+space()+digit()).charAt(rnd(0,2))
            ; 
        },
        word = function( positive ){ 
            return false !== positive 
                ? (ALPHAS+DIGITS).charAt(rnd(0, ALPHAS.length+DIGITS.length-1))
                : (punct()+space()).charAt(rnd(0,1))
            ; 
        },
        any = function( ){ 
            return ALL.charAt(rnd(0, ALL.length-1));
        },
        character = function( chars, positive ){ 
            if ( false !== positive ) return chars.length ? chars[rnd(0, chars.length-1)] : ''; 
            var choices = ALL_ARY.filter(function(c){ return 0 > chars.indexOf(c); }); 
            return choices.length ? choices[rnd(0, choices.length-1)] : '';
        },
        
        eat = function( CHARS, s, pos ) {
            var l = pos || 0;
            while ( l < s.length && -1 < CHARS.indexOf( s.charAt(l) ) ) l++;
            return l-pos;
        },
        
        //hexRegex = /^x([0-9a-fA-F]{2})/,
        match_hex = function( s ) {
            var m = false;
            if ( s.length > 2 && 'x' === s.charAt(0) )
            {
                if ( 2 == eat(HEXDIGITS, s, 1) ) return [m=s.slice(0, 3), m.slice(1)];
            }
            return false
        },
        //unicodeRegex = /^u([0-9a-fA-F]{4})/,
        match_unicode = function( s ) {
            var m = false;
            if ( s.length > 4 && 'u' === s.charAt(0) )
            {
                if ( 4 == eat(HEXDIGITS, s, 1) ) return [m=s.slice(0, 5), m.slice(1)];
            }
            return false
        },
        //repeatsRegex = /^\{\s*(\d+)\s*,?\s*(\d+)?\s*\}/,
        match_repeats = function( s ) {
            var l, pos = 0, m = false;
            if ( s.length > 2 && '{' === s.charAt(pos) )
            {
                m = ['', '', null];
                pos++;
                if ( l = eat(SPACES, s, pos) ) pos += l;
                if ( 1 <= (l=eat(DIGITS, s, pos)) ) 
                {
                    m[1] = s.slice(pos, pos+l);
                    pos += l;
                }
                else
                {
                    return false;
                }
                if ( l = eat(SPACES, s, pos) ) pos += l;
                if ( 1 == eat(',', s, pos) ) pos += 1;
                if ( l = eat(SPACES, s, pos) ) pos += l;
                if ( 1 <= (l=eat(DIGITS, s, pos)) ) 
                {
                    m[2] = s.slice(pos, pos+l);
                    pos += l;
                }
                if ( l = eat(SPACES, s, pos) ) pos += l;
                if ( '}' === s.charAt(pos) )
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
            return false
        },
        
        concat = function(p1, p2) {
            if ( p2 && ( p2 instanceof Arr || "[object Array]" == to_string.call(p2) ) )
            {
                for (var p=0, l=p2.length; p<l; p++)
                {
                    p1[p2[p]] = 1;
                }
            }
            else
            {
                for (var p in p2)
                {
                    p1[p] = 1;
                }
            }
            return p1;
        },
        
        case_insensitive = function( chars, asArray ) {
            if ( asArray )
            {
                if ( chars.charAt ) chars = chars.split('');
                chars = chars.map(function(c){
                    return rnd(0,1) ? c.toLowerCase( ) : c.toUpperCase( );
                });
                if ( !asArray ) chars = chars.join('');
                return chars;
            }
            else
            {
                return rnd(0,1) ? chars.toLowerCase( ) : chars.toUpperCase( );
            }
        },
        
        peek_characters = function peek_characters( part ) {
            var peek = {}, negativepeek = {}, current, p, i, l, 
                tmp, done, type, ptype;
            
            type = part.type;
            // walk the sequence
            if ( "Alternation" == type )
            {
                for (i=0, l=part.part.length; i<l; i++)
                {
                    tmp = peek_characters( part.part[i] );
                    peek = concat( peek, tmp.peek );
                    negativepeek = concat( negativepeek, tmp.negativepeek );
                }
            }
            
            else if ( "Group" == type )
            {
                tmp = peek_characters( part.part );
                peek = concat( peek, tmp.peek );
                negativepeek = concat( negativepeek, tmp.negativepeek );
            }
            
            else if ( "Sequence" == type )
            {
                i = 0;
                l = part.part.length;
                p = part.part[i];
                done = ( 
                    i >= l || !p || "Quantifier" != p.type || 
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
                        i >= l || !p || "Quantifier" != p.type || 
                        ( !p.flags.MatchZeroOrMore && !p.flags.MatchZeroOrOne && "0"!=p.flags.MatchMinimum ) 
                    );
                }
                if ( i < l )
                {
                    p = part.part[i];
                    
                    if ("Special" == p.type && ('^'==p.part || '$'==p.part)) p = part.part[i+1] || null;
                    
                    if (p && "Quantifier" == p.type) p = p.part;
                    
                    if (p)
                    {
                        tmp = peek_characters( p );
                        peek = concat( peek, tmp.peek );
                        negativepeek = concat( negativepeek, tmp.negativepeek );
                    }
                }
            }
            
            else if ( "CharGroup" == type )
            {
                current = ( part.flags.NotMatch ) ? negativepeek : peek;
                
                for (i=0, l=part.part.length; i<l; i++)
                {
                    p = part.part[i];
                    ptype = p.type;
                    if ( "Chars" == ptype )
                    {
                        current = concat( current, p.part );
                    }
                    
                    else if ( "CharRange" == ptype )
                    {
                        current = concat( current, character_range(p.part) );
                    }
                    
                    else if ( "UnicodeChar" == ptype || "HexChar" == ptype )
                    {
                        current[p.flags.Char] = 1;
                    }
                    
                    else if ( "Special" == ptype )
                    {
                        if ('D' == p.part)
                        {
                            if (part.flags.NotMatch)
                                peek[ '\\d' ] = 1;
                            else
                                negativepeek[ '\\d' ] = 1;
                        }
                        else if ('W' == p.part)
                        {
                            if (part.flags.NotMatch)
                                peek[ '\\w' ] = 1;
                            else
                                negativepeek[ '\\W' ] = 1;
                        }
                        else if ('S' == p.part)
                        {
                            if (part.flags.NotMatch)
                                peek[ '\\s' ] = 1;
                            else
                                negativepeek[ '\\s' ] = 1;
                        }
                        else
                        {
                            current['\\' + p.part] = 1;
                        }
                    }
                }
            }
            
            else if ( "String" == type )
            {
                peek[part.part.charAt(0)] = 1;
            }
            
            else if ( "Special" == type && !part.flags.MatchStart && !part.flags.MatchEnd )
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
                    
            else if ( "UnicodeChar" == type || "HexChar" == type )
            {
                peek[part.flags.Char] = 1;
            }
            
            return { peek: peek, negativepeek: negativepeek };
        },
        
        generate = function generate( part, isCaseInsensitive ) {
            var sample = '', p, i, l, type;
            
            type = part.type;
            // walk the sequence
            if ( "Alternation" == type )
            {
                sample += generate( part.part[rnd(0, part.part.length-1)], isCaseInsensitive );
            }
            
            else if ( "Group" == type )
            {
                sample += generate( part.part, isCaseInsensitive );
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
                        chars = chars.concat( isCaseInsensitive ? case_insensitive( p.part, true ) : p.part );
                    }
                    
                    else if ( "CharRange" == ptype )
                    {
                        chars = chars.concat( isCaseInsensitive ? case_insensitive( character_range(p.part), true ) : character_range(p.part) );
                    }
                    
                    else if ( "UnicodeChar" == ptype || "HexChar" == ptype )
                    {
                        chars.push( isCaseInsensitive ? case_insensitive( p.flags.Char ): p.flags.Char );
                    }
                    
                    else if ( "Special" == ptype )
                    {
                        if ('D' == p.part)
                        {
                            chars.push( digit( false ) );
                        }
                        else if ('W' == p.part)
                        {
                            chars.push( word( false ) );
                        }
                        else if ('S' == p.part)
                        {
                            chars.push( space( false ) );
                        }
                        else if ('d' == p.part)
                        {
                            chars.push( digit( ) );
                        }
                        else if ('w' == p.part)
                        {
                            chars.push( word( ) );
                        }
                        else if ('s' == p.part)
                        {
                            chars.push( space( ) );
                        }
                        else
                        {
                            chars.push( '\\' + p.part );
                        }
                    }
                }
                sample += character(chars, !part.flags.NotMatch);
            }
            
            else if ( "String" == type )
            {
                sample += isCaseInsensitive ? case_insensitive( part.part ) : part.part;
            }
            
            else if ( "Special" == type && !part.flags.MatchStart && !part.flags.MatchEnd )
            {
                if ('D' == part.part)
                {
                    sample += digit( false );
                }
                else if ('W' == part.part)
                {
                    sample += word( false );
                }
                else if ('S' == part.part)
                {
                    sample += space( false );
                }
                else if ('d' == part.part)
                {
                    sample += digit( );
                }
                else if ('w' == part.part)
                {
                    sample += word( );
                }
                else if ('s' == part.part)
                {
                    sample += space( );
                }
                else if ('.' == part.part)
                {
                    sample += any( );
                }
                else
                {
                    sample += '\\' + part.part;
                }
            }
                    
            else if ( "UnicodeChar" == type || "HexChar" == type )
            {
                sample += isCaseInsensitive ? case_insensitive( part.flags.Char ) : part.flags.Char;
            }
            
            return sample;
        },

        subgroup = function subgroup( self ) {
            var ch, word = '', alternation = [], sequence = [], flags = {}, flag, match, escaped = false,
                pre = self.regex.substr(self.pos, 2);
            
            if ( "?:" == pre )
            {
                flags[ "NotCaptured" ] = 1;
                self.pos += 2;
            }
            
            else if ( "?=" == pre )
            {
                flags[ "LookAhead" ] = 1;
                self.pos += 2;
            }
            
            else if ( "?!" == pre )
            {
                flags[ "NegativeLookAhead" ] = 1;
                self.pos += 2;
            }
            
            flags[ "GroupIndex" ] = ++self.groupIndex;
            
            while ( self.pos < self.regex.length )
            {
                ch = self.regex.charAt( self.pos++ );
                
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped )  ch = self.regex.charAt( self.pos++ );
                
                if ( escaped )
                {
                    // unicode character
                    if ( 'u' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = match_unicode( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "UnicodeChar" } );
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = match_hex( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "HexChar" } );
                    }
                    
                    else if ( specialCharsEscaped[ch] && '/' != ch)
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        flag = {};
                        flag[ specialCharsEscaped[ch] ] = 1;
                        sequence.push( { part: ch, flags: flag, type: "Special" } );
                    }
                    
                    else
                    {
                        word += ch;
                    }
                }
                
                else
                {
                    // group end
                    if ( ')' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        if ( alternation.length )
                        {
                            alternation.push( { part: sequence, flags: {}, type: "Sequence" } );
                            sequence = [];
                            flag = {};
                            flag[ specialChars['|'] ] = 1;
                            return { part: { part: alternation, flags: flag, type: "Alternation" }, flags: flags, type: "Group" };
                        }
                        else
                        {
                            return { part: { part: sequence, flags: {}, type: "Sequence" }, flags: flags, type: "Group" };
                        }
                    }
                    
                    // parse alternation
                    else if ( '|' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        alternation.push( { part: sequence, flags: {}, type: "Sequence" } );
                        sequence = [];
                    }
                    
                    // parse character group
                    else if ( '[' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        sequence.push( chargroup( self ) );
                    }
                    
                    // parse sub-group
                    else if ( '(' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        sequence.push( subgroup( self ) );
                    }
                    
                    // parse num repeats
                    else if ( '{' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = match_repeats( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        flag = { part: match[0], "MatchMinimum": match[1], "MatchMaximum": match[2] || "unlimited" };
                        flag[ specialChars[ch] ] = 1;
                        if ( '?' == self.regex.charAt(self.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            self.pos++;
                        }
                        else
                        {
                            flag[ "isGreedy" ] = 1;
                        }
                        var prev = sequence.pop();
                        if ( "String" == prev.type && prev.part.length > 1 )
                        {
                            sequence.push( { part: prev.part.slice(0, -1), flags: {}, type: "String" } );
                            prev.part = prev.part.slice(-1);
                        }
                        sequence.push( { part: prev, flags: flag, type: "Quantifier" } );
                    }
                    
                    // quantifiers
                    else if ( '*' == ch || '+' == ch || '?' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        flag = {};
                        flag[ specialChars[ch] ] = 1;
                        if ( '?' == self.regex.charAt(self.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            self.pos++;
                        }
                        else
                        {
                            flag[ "isGreedy" ] = 1;
                        }
                        var prev = sequence.pop();
                        if ( "String" == prev.type && prev.part.length > 1 )
                        {
                            sequence.push( { part: prev.part.slice(0, -1), flags: {}, type: "String" } );
                            prev.part = prev.part.slice(-1);
                        }
                        sequence.push( { part: prev, flags: flag, type: "Quantifier" } );
                    }
                
                    // special characters like ^, $, ., etc..
                    else if ( specialChars[ch] )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        flag = {};
                        flag[ specialChars[ch] ] = 1;
                        sequence.push( { part: ch, flags: flag, type: "Special" } );
                    }
                
                    else
                    {
                        word += ch;
                    }
                }
            }
            if ( word.length )
            {
                sequence.push( { part: word, flags: {}, type: "String" } );
                word = '';
            }
            if ( alternation.length )
            {
                alternation.push( { part: sequence, flags: {}, type: "Sequence" } );
                sequence = [];
                flag = {};
                flag[ specialChars['|'] ] = 1;
                return { part: { part: alternation, flags: flag, type: "Alternation" }, flags: flags, type: "Group" };
            }
            else
            {
                return { part: { part: sequence, flags: {}, type: "Sequence" }, flags: flags, type: "Group" };
            }
        },
        
        chargroup = function chargroup( self ) {
            var sequence = [], chars = [], flags = {}, flag, ch, prevch, range, isRange = false, match, isUnicode, escaped = false;
            
            if ( '^' == self.regex.charAt( self.pos ) )
            {
                flags[ "NotMatch" ] = 1;
                self.pos++;
            }
                    
            while ( self.pos < self.regex.length )
            {
                isUnicode = false;
                prevch = ch;
                ch = self.regex.charAt( self.pos++ );
                
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped )  ch = self.regex.charAt( self.pos++ );
                
                if ( escaped )
                {
                    // unicode character
                    if ( 'u' == ch )
                    {
                        match = match_unicode( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        ch = fromCharCode(parseInt(match[1], 16));
                        isUnicode = true;
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        match = match_hex( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        ch = fromCharCode(parseInt(match[1], 16));
                        isUnicode = true;
                    }
                }
                
                if ( isRange )
                {
                    if ( chars.length )
                    {
                        sequence.push( { part: chars, flags: {}, type: "Chars" } );
                        chars = [];
                    }
                    range[1] = ch;
                    isRange = false;
                    sequence.push( { part: range, flags: {}, type: "CharRange" } );
                }
                else
                {
                    if ( escaped )
                    {
                        if ( !isUnicode && specialCharsEscaped[ch] && '/' != ch)
                        {
                            if ( chars.length )
                            {
                                sequence.push( { part: chars, flags: {}, type: "Chars" } );
                                chars = [];
                            }
                            flag = {};
                            flag[ specialCharsEscaped[ch] ] = 1;
                            sequence.push( { part: ch, flags: flag, type: "Special" } );
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
                                sequence.push( { part: chars, flags: {}, type: "Chars" } );
                                chars = [];
                            }
                            return { part: sequence, flags: flags, type: "CharGroup" };
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
                sequence.push( { part: chars, flags: {}, type: "Chars" } );
                chars = [];
            }
            return { part: sequence, flags: flags, type: "CharGroup" };
        },
        
        analyze = function analyze( regex ) {
            var self = {pos: 0, groupIndex: 0, regex: regex};
            var ch, word = '', alternation = [], sequence = [], flag, match, escaped = false;
            
            while ( self.pos < self.regex.length )
            {
                ch = self.regex.charAt( self.pos++ );
                
                //   \\abc
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped )  ch = self.regex.charAt( self.pos++ );
                
                if ( escaped )
                {
                    // unicode character
                    if ( 'u' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = match_unicode( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "UnicodeChar" } );
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = match_hex( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "HexChar" } );
                    }
                    
                    else if ( specialCharsEscaped[ch] && '/' != ch)
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        flag = {};
                        flag[ specialCharsEscaped[ch] ] = 1;
                        sequence.push( { part: ch, flags: flag, type: "Special" } );
                    }
                    
                    else
                    {
                        word += ch;
                    }
                }
                
                else
                {
                    // parse alternation
                    if ( '|' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        alternation.push( { part: sequence, flags: {}, type: "Sequence" } );
                        sequence = [];
                    }
                    
                    // parse character group
                    else if ( '[' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        sequence.push( chargroup( self ) );
                    }
                    
                    // parse sub-group
                    else if ( '(' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        sequence.push( subgroup( self ) );
                    }
                    
                    // parse num repeats
                    else if ( '{' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = match_repeats( self.regex.substr( self.pos-1 ) );
                        self.pos += match[0].length-1;
                        flag = { part: match[0], "MatchMinimum": match[1], "MatchMaximum": match[2] || "unlimited" };
                        flag[ specialChars[ch] ] = 1;
                        if ( '?' == self.regex.charAt(self.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            self.pos++;
                        }
                        else
                        {
                            flag[ "isGreedy" ] = 1;
                        }
                        var prev = sequence.pop();
                        if ( "String" == prev.type && prev.part.length > 1 )
                        {
                            sequence.push( { part: prev.part.slice(0, -1), flags: {}, type: "String" } );
                            prev.part = prev.part.slice(-1);
                        }
                        sequence.push( { part: prev, flags: flag, type: "Quantifier" } );
                    }
                    
                    // quantifiers
                    else if ( '*' == ch || '+' == ch || '?' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        flag = {};
                        flag[ specialChars[ch] ] = 1;
                        if ( '?' == self.regex.charAt(self.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            self.pos++;
                        }
                        else
                        {
                            flag[ "isGreedy" ] = 1;
                        }
                        var prev = sequence.pop();
                        if ( "String" == prev.type && prev.part.length > 1 )
                        {
                            sequence.push( { part: prev.part.slice(0, -1), flags: {}, type: "String" } );
                            prev.part = prev.part.slice(-1);
                        }
                        sequence.push( { part: prev, flags: flag, type: "Quantifier" } );
                    }
                
                    // special characters like ^, $, ., etc..
                    else if ( specialChars[ch] )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        flag = {};
                        flag[ specialChars[ch] ] = 1;
                        sequence.push( { part: ch, flags: flag, type: "Special" } );
                    }
                
                    else
                    {
                        word += ch;
                    }
                }
            }
            
            if ( word.length )
            {
                sequence.push( { part: word, flags: {}, type: "String" } );
                word = '';
            }
            
            if ( alternation.length )
            {
                alternation.push( { part: sequence, flags: {}, type: "Sequence" } );
                sequence = [];
                flag = {};
                flag[ specialChars['|'] ] = 1;
                return { part: alternation, flags: flag, type: "Alternation" };
            }
            else
            {
                return { part: sequence, flags: {}, type: "Sequence" };
            }
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

        $regex: null,
        $flags: null,
        $parts: null,
        $needsRefresh: true,

        dispose: function( ) {
            var self = this;
            self.$regex = null;
            self.$flags = null;
            self.$parts = null;
            return self;
        },
        
        regex: function( regex, delim ) {
            var self = this;
            if ( regex )
            {
                delim = delim || '/';
                var flags = {}, r = regex.toString( ), l = r.length, ch = r.charAt(l-1);
                
                // parse regex flags
                while ( delim !== ch )
                {
                    flags[ ch ] = 1;
                    r = r.substr(0, l-1);
                    l = r.length;
                    ch = r.charAt(l-1);
                }
                // remove regex delimiters
                if ( delim == r.charAt(0) && delim == r.charAt(l-1) )  r = r.substr(1, l-2);
                
                if ( self.$regex !== r ) self.$needsRefresh = true;
                self.$regex = r; self.$flags = flags;
            }
            return self;
        },
        
        analyze: function( ) {
            var self = this;
            if ( self.$needsRefresh )
            {
                self.$parts = analyze( self.$regex );
                self.$needsRefresh = false;
            }
            return self;
        },
        
        getRegex: function( ) {
            return new RegExp(this.$regex, Keys(this.$flags).join(''));
        },
        
        getParts: function( ) {
            var self = this;
            if ( self.$needsRefresh ) self.analyze( );
            return self.$parts;
        },
        
        // experimental feature
        generateSample: function( ) {
            var self = this;
            if ( self.$needsRefresh ) self.analyze( );
            return generate( self.$parts, self.$flags && self.$flags.i );
        },
        
        // experimental feature
        getPeekChars: function( ) {
            var self = this, isCaseInsensitive,
                peek, n, c, p, cases;
            
            if ( self.$needsRefresh ) self.analyze( );
            
            peek = peek_characters( self.$parts );
            isCaseInsensitive = self.$flags && self.$flags.i;
            
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
                    
                    else if ( '\\' != c.charAt(0) && isCaseInsensitive )
                    {
                        cases[ c.toLowerCase() ] = 1;
                        cases[ c.toUpperCase() ] = 1;
                    }
                    
                    else if ( '\\' == c.charAt(0) )
                    {
                        delete p[c];
                    }
                }
                peek[n] = concat(p, cases);
            }
            return peek;
        }
    };

    /* main code ends here */
    /* export the module */
    return Analyzer;
});