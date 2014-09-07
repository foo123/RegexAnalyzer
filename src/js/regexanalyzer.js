/**
*
*   RegExAnalyzer
*   @version: @@VERSION@@
*
*   A simple Regular Expression Analyzer in JavaScript
*   https://github.com/foo123/regex-analyzer
*
**/
(function( exports, undef ) {
    
    var escapeChar = '\\',
    
        repeatsRegex = /^\{\s*(\d+)\s*,?\s*(\d+)?\s*\}/,
    
        unicodeRegex = /^u([0-9a-fA-F]{4})/,
    
        hexRegex = /^x([0-9a-fA-F]{2})/,
    
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
        }
    ;
    
    var to_string = Object.prototype.toString;
    
    var concat = function(p1, p2) {
        if ( p2 && ( p2 instanceof Array || "[object Array]" == to_string.call(p2) ) )
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
    };
    
    // http://stackoverflow.com/questions/12376870/create-an-array-of-characters-from-specified-range
    var getCharRange = function(first, last) {
        if ( first && ( first instanceof Array || "[object Array]" == to_string.call(first) ) )
        {
            last = first[1];
            first = first[0];
        }
        var ch, chars, start = first.charCodeAt(0), end = last.charCodeAt(0);
        
        if ( end == start ) return [ String.fromCharCode( start ) ];
        
        chars = [];
        for (ch = start; ch <= end; ++ch)
            chars.push( String.fromCharCode( ch ) );
        
        return chars;
    };
    
    var getPeekChars = function(part) {
        var peek = {}, negativepeek = {}, current, p, i, l, 
            tmp, done, type, ptype;
        
        type = part.type;
        // walk the sequence
        if ( "Alternation" == type )
        {
            for (i=0, l=part.part.length; i<l; i++)
            {
                tmp = getPeekChars( part.part[i] );
                peek = concat( peek, tmp.peek );
                negativepeek = concat( negativepeek, tmp.negativepeek );
            }
        }
        
        else if ( "Group" == type )
        {
            tmp = getPeekChars( part.part );
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
                tmp = getPeekChars( p.part );
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
                    tmp = getPeekChars( p );
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
                    current = concat( current, getCharRange(p.part) );
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
    };
    
    // A simple (js-flavored) regular expression analyzer
    var Analyzer = function( regex, delim ) {
        
        if ( regex ) this.setRegex(regex, delim);
    };
    
    Analyzer.VERSION = "@@VERSION@@";
    Analyzer.getCharRange = getCharRange;
    
    Analyzer.prototype = {
        
        constructor : Analyzer,

        VERSION : Analyzer.VERSION,
        
        regex : null,
        groupIndex : null,
        pos : null,
        flags : null,
        parts : null,

        getCharRange : Analyzer.getCharRange,
        
        // experimental feature
        getPeekChars : function() {
        
            var isCaseInsensitive = this.flags && this.flags.i;
            var peek = getPeekChars(this.parts), n, c, p, cases;
            
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
                        cases = concat(cases, getCharRange('0', '9'));
                    }
                    
                    else if ('\\s' == c)
                    {
                        delete p[c];
                        cases = concat(cases, ['\f','\n','\r','\t','\v','\u00A0','\u2028','\u2029']);
                    }
                    
                    else if ('\\w' == c)
                    {
                        delete p[c];
                        cases = concat(cases, ['_'].concat(getCharRange('0', '9')).concat(getCharRange('a', 'z')).concat(getCharRange('A', 'Z')));
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
        },
        
        setRegex : function(regex, delim) {
            if ( regex )
            {
                this.flags = {};
                
                delim = delim || '/';
                var r = regex.toString(); 
                var l = r.length;
                var ch = r.charAt(l-1);
                
                // parse regex flags
                while ( delim != ch )
                {
                    this.flags[ ch ] = 1;
                    r = r.substr(0, l-1);
                    l = r.length;
                    ch = r.charAt(l-1);
                }
                // remove regex delimiters
                if ( delim == r.charAt(0) && delim == r.charAt(l-1) )  r = r.substr(1, l-2);
                
                this.regex = r;
            }
            return this;
        },
        
        analyze : function() {
            var ch, word = '', alternation = [], sequence = [], flag, match, escaped = false;
            
            this.pos = 0;
            this.groupIndex = 0;
            
            while ( this.pos < this.regex.length )
            {
                ch = this.regex.charAt( this.pos++ );
                
                //   \\abc
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped )  ch = this.regex.charAt( this.pos++ );
                
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
                        match = unicodeRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": String.fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "UnicodeChar" } );
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = hexRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": String.fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "HexChar" } );
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
                        sequence.push( this.chargroup() );
                    }
                    
                    // parse sub-group
                    else if ( '(' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        sequence.push( this.subgroup() );
                    }
                    
                    // parse num repeats
                    else if ( '{' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = repeatsRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        flag = { part: match[0], "MatchMinimum": match[1], "MatchMaximum": match[2] || "unlimited" };
                        flag[ specialChars[ch] ] = 1;
                        if ( '?' == this.regex.charAt(this.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            this.pos++;
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
                        if ( '?' == this.regex.charAt(this.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            this.pos++;
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
                this.parts = { part: alternation, flags: flag, type: "Alternation" };
            }
            else
            {
                this.parts = { part: sequence, flags: {}, type: "Sequence" };
            }
            
            return this;
        },

        subgroup : function() {
            
            var ch, word = '', alternation = [], sequence = [], flags = {}, flag, match, escaped = false;
            
            var pre = this.regex.substr(this.pos, 2);
            
            if ( "?:" == pre )
            {
                flags[ "NotCaptured" ] = 1;
                this.pos += 2;
            }
            
            else if ( "?=" == pre )
            {
                flags[ "LookAhead" ] = 1;
                this.pos += 2;
            }
            
            else if ( "?!" == pre )
            {
                flags[ "NegativeLookAhead" ] = 1;
                this.pos += 2;
            }
            
            flags[ "GroupIndex" ] = ++this.groupIndex;
            
            while ( this.pos < this.regex.length )
            {
                ch = this.regex.charAt( this.pos++ );
                
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped )  ch = this.regex.charAt( this.pos++ );
                
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
                        match = unicodeRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": String.fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "UnicodeChar" } );
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = hexRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        sequence.push( { part: match[0], flags: { "Char": String.fromCharCode(parseInt(match[1], 16)), "Code": match[1] }, type: "HexChar" } );
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
                        sequence.push( this.chargroup() );
                    }
                    
                    // parse sub-group
                    else if ( '(' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        sequence.push( this.subgroup() );
                    }
                    
                    // parse num repeats
                    else if ( '{' == ch )
                    {
                        if ( word.length )
                        {
                            sequence.push( { part: word, flags: {}, type: "String" } );
                            word = '';
                        }
                        match = repeatsRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        flag = { part: match[0], "MatchMinimum": match[1], "MatchMaximum": match[2] || "unlimited" };
                        flag[ specialChars[ch] ] = 1;
                        if ( '?' == this.regex.charAt(this.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            this.pos++;
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
                        if ( '?' == this.regex.charAt(this.pos) )
                        {
                            flag[ "isGreedy" ] = 0;
                            this.pos++;
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
        
        chargroup : function() {
            
            var sequence = [], chars = [], flags = {}, flag, ch, prevch, range, isRange = false, match, isUnicode, escaped = false;
            
            if ( '^' == this.regex.charAt( this.pos ) )
            {
                flags[ "NotMatch" ] = 1;
                this.pos++;
            }
                    
            while ( this.pos < this.regex.length )
            {
                isUnicode = false;
                prevch = ch;
                ch = this.regex.charAt( this.pos++ );
                
                escaped = (escapeChar == ch) ? true : false;
                if ( escaped )  ch = this.regex.charAt( this.pos++ );
                
                if ( escaped )
                {
                    // unicode character
                    if ( 'u' == ch )
                    {
                        match = unicodeRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        ch = String.fromCharCode(parseInt(match[1], 16));
                        isUnicode = true;
                    }
                    
                    // hex character
                    else if ( 'x' == ch )
                    {
                        match = hexRegex.exec( this.regex.substr( this.pos-1 ) );
                        this.pos += match[0].length-1;
                        ch = String.fromCharCode(parseInt(match[1], 16));
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
        }
    };
    
    
    exports['@@MODULE_NAME@@'] = Analyzer;
    
})(@@EXPORTS@@);