/**
*
*   RegExComposer
*   @version: @@VERSION@@
*
*   A simple and intuitive Regular Expression Composer in JavaScript
*   https://github.com/foo123/regex-analyzer
*
**/
(function( exports, undef ) {
    
    var OP = Object.prototype, AP = Array.prototype,
        to_string = OP.toString, 
        
        slice = function(a) { return AP.slice.apply(a, AP.slice.call(arguments, 1)); },
    
        esc = function(s) {
            return s.replace(/([.*+?^${}()|[\]\/\\\-])/g, '\\$1');
        },
        
        flatten = function(a) {
            var r = [], i = 0;
            while (i < a.length) r = r.concat(a[i++]);
            return r;
        },
        
        getArgs = function(args, asArray) {
            /*var a = slice(args);
            if ( asArray && a[0] && 
                ( a[0] instanceof Array || '[object Array]' == to_string.call(a[0]) )
            )
                a = a[0];*/
            return flatten(slice(args)); //a;
        },
        
        T_SEQ = 2, T_EITHER = 4, T_GROUP = 8, T_CHARGROUP = 16
    ;
    
    
    // A simple (js-flavored) regular expression composer
    var Composer = function( ) {
        this.regex = null;
        this.reset();
    };
    
    Composer.VERSION = "@@VERSION@@";
    
    Composer.prototype = {
        
        constructor : Composer,

        VERSION : Composer.VERSION,
        
        level: 0,
        regex : null,
        parts: null,

        compose: function(/* flags */) {
            this.regex = new RegExp(this.parts[0].part.join(''), slice(arguments).join(''));
            this.reset();
            return this.regex;
        },

        partial: function(reset) {
            var p = this.parts[0].part.join('');
            if (false!==reset) this.reset();
            return p;
        },

        reset: function() {
            this.level = 0;
            this.parts = [{part: [], type: T_SEQ, flag: ''}];
            return this;
        },

        repeat: function(min, max, greedy) {
            if ( undef === min ) return this;
            var repeat = ( undef === max ) ? ('{'+min+'}') : ('{'+min+','+max+'}');
            
            this.parts[this.level].part[this.parts[this.level].part.length-1] += (false===greedy) ? (repeat+'?') : repeat;
            return this;
        },
        
        zeroOrOne: function(greedy) {
            this.parts[this.level].part[this.parts[this.level].part.length-1] += (false===greedy) ? '??' : '?';
            return this;
        },
        
        zeroOrMore: function(greedy) {
            this.parts[this.level].part[this.parts[this.level].part.length-1] += (false===greedy) ? '*?' : '*';
            return this;
        },
        
        oneOrMore: function(greedy) {
            this.parts[this.level].part[this.parts[this.level].part.length-1] += (false===greedy) ? '+?' : '+';
            return this;
        },
        
        sub: function(partialRegex, withParen) {
            if ( undef !== partialRegex )
            {
                if ( withParen )
                    this.parts[this.level].part.push( '(' + partialRegex + ')' );
                else
                    this.parts[this.level].part.push( partialRegex );
            }
            return this;
        },
        
        match: function(part) {
            if ( undef !== part )
                this.parts[this.level].part.push( esc(part) );
            return this;
        },
        
        startOfInput: function() {
            this.parts[this.level].part.push('^');
            return this;
        },
        
        endOfInput: function() {
            this.parts[this.level].part.push('$');
            return this;
        },
        
        any: function() {
            this.parts[this.level].part.push('.');
            return this;
        },
        
        space: function(positive) {
            this.parts[this.level].part.push((false===positive) ? '\\S' : '\\s');
            return this;
        },
        
        digit: function(positive) {
            this.parts[this.level].part.push((false===positive) ? '\\D' : '\\d');
            return this;
        },
        
        word: function(positive) {
            this.parts[this.level].part.push((false===positive) ? '\\W' : '\\w');
            return this;
        },
        
        boundary: function(positive) {
            this.parts[this.level].part.push((false===positive) ? '\\B' : '\\b');
            return this;
        },
        
        LF: function() {
            this.parts[this.level].part.push('\\n');
            return this;
        },
        
        CR: function() {
            this.parts[this.level].part.push('\\r');
            return this;
        },
        
        TAB: function() {
            this.parts[this.level].part.push('\\t');
            return this;
        },
        
        CTRL: function(_char) {
            if ( _char )
                this.parts[this.level].part.push('\\c'+_char);
            return this;
        },
        
        backSpace: function() {
            this.parts[this.level].part.push('[\\b]');
            return this;
        },
        
        backReference: function(n) {
            this.parts[this.level].part.push('\\'+parseInt(n, 10));
            return this;
        },
        
        characters: function() {
            if ( T_CHARGROUP == this.parts[this.level].type )
            {
                var chars = getArgs(arguments, 1).map(esc).join('');
                this.parts[this.level].part.push( chars );
            }
            return this;
        },
        
        range: function(start, end) {
            if ( T_CHARGROUP == this.parts[this.level].type )
            {
                if ( undef === start || undef === end ) return this;
                var range = esc(start) + '-' + esc(end);
                this.parts[this.level].part.push( range );
            }
            return this;
        },
        
        alternate: function() {
            this.level++;
            this.parts.push({part: [], type: T_EITHER, flag: ''});
            return this;
        },
        
        group: function() {
            this.level++;
            this.parts.push({part: [], type: T_GROUP, flag: ''});
            return this;
        },
        
        nonCaptureGroup: function() {
            this.level++;
            this.parts.push({part: [], type: T_GROUP, flag: '?:'});
            return this;
        },
        
        lookAheadGroup: function(positive) {
            this.level++;
            this.parts.push({part: [], type: T_GROUP, flag: (false===positive) ? '?!' : '?='});
            return this;
        },
        
        characterGroup: function(positive) {
            this.level++;
            this.parts.push({part: [], type: T_CHARGROUP, flag: (false===positive) ? '^' : ''});
            return this;
        },
        
        end: function() {
            var prev = this.parts.pop() || {}, 
                type = prev.type, 
                flag = prev.flag || '',
                part = prev.part || [],
                level
            ;
            
            if (0 < this.level)
            {
                level = --this.level;
                
                if ( (T_EITHER|T_GROUP) & type )
                    this.parts[level].part.push('(' + flag + part.join('|') + ')');
                
                else if ( T_CHARGROUP & type )
                    this.parts[level].part.push('[' + flag + part.join('') + ']');
            }
            return this;
        }
    };
    // aliases
    var CP = Composer.prototype;
    CP.startOfLine = CP.startOfInput;
    CP.endOfLine = CP.endOfInput;
    CP.subRegex = CP.sub;
    CP.lineFeed = CP.LF;
    CP.carriageReturn = CP.CR;
    CP.tabulate = CP.tab = CP.TAB;
    CP.control = CP.CTRL;
    CP.wordBoundary = CP.boundary;
    CP.either = CP.alternate;
    CP.subGroup = CP.group;
    CP.nonCaptureSubGroup = CP.nonCaptureGroup;
    CP.lookAheadSubGroup = CP.lookAheadGroup;
    
    exports['@@MODULE_NAME@@'] = Composer;
    
})(@@EXPORTS@@);