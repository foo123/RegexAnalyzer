/**
*
*   RegExComposer
*   @version: 0.4.3
*
*   A simple and intuitive Regular Expression Composer for PHP, Python, Node/JS
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
    /* module name */           "RegExComposer",
    /* module factory */        function( exports, undef ) {
        
    "use strict";
    /* main code starts here */
    var __version__ = "0.4.3", 
        
        PROTO = 'prototype',
        OP = Object[PROTO], AP = Array[PROTO],
        to_string = OP.toString, 
        RE = function(s, f){ return new RegExp(s,f||''); },
        
        slice = function( a ) { return AP.slice.apply(a, AP.slice.call(arguments, 1)); },

        esc = function( s ) { return s.replace(/([.*+?^${}()|[\]\/\\\-])/g, '\\$1'); },
        
        flatten = function( a ) {
            var r = [], i = 0;
            while (i < a.length) r = r.concat(a[i++]);
            return r;
        },
        
        getArgs = function( args, asArray ) {
            /*var a = slice(args);
            if ( asArray && a[0] && 
                ( a[0] instanceof Array || '[object Array]' == to_string.call(a[0]) )
            )
                a = a[0];*/
            return flatten( slice( args ) ); //a;
        },
        
        T_SEQ = 2, T_EITHER = 4, T_GROUP = 8, T_CHARGROUP = 16
    ;


    // A simple (js-flavored) regular expression composer
    var Composer = function Composer( ) {
        if ( !(this instanceof Composer) ) return new Composer( );
        this.$regex = null;
        this.reset( );
    };
    Composer.VERSION = __version__;
    Composer[PROTO] = {
        
        constructor: Composer,

        $level: 0,
        $regex: null,
        $parts: null,

        dispose: function( ) {
            var self = this;
            self.$level = null;
            self.$regex = null;
            self.$parts = null;
            return self;
        },
        
        reset: function( ) {
            var self = this;
            self.$level = 0;
            self.$parts = [{part: [], type: T_SEQ, flag: ''}];
            return self;
        },

        compose: function( /* flags */ ) {
            var self = this;
            self.$regex = RE(self.$parts[0].part.join(''), slice(arguments).join(''));
            self.reset( );
            return self.$regex;
        },

        partial: function( reset ) {
            var self = this, p = self.$parts[0].part.join('');
            if ( false!==reset ) self.reset( );
            return p;
        },

        repeat: function( min, max, greedy ) {
            var self = this;
            if ( undef === min ) return self;
            var repeat = ( undef === max ) ? ('{'+min+'}') : ('{'+min+','+max+'}');
            self.$parts[self.$level].part[self.$parts[self.$level].part.length-1] += (false===greedy) ? (repeat+'?') : repeat;
            return self;
        },
        
        zeroOrOne: function( greedy ) {
            var self = this;
            self.$parts[self.$level].part[self.$parts[self.$level].part.length-1] += (false===greedy) ? '??' : '?';
            return self;
        },
        
        zeroOrMore: function( greedy ) {
            var self = this;
            self.$parts[self.$level].part[self.$parts[self.$level].part.length-1] += (false===greedy) ? '*?' : '*';
            return self;
        },
        
        oneOrMore: function( greedy ) {
            var self = this;
            self.$parts[self.$level].part[self.$parts[self.$level].part.length-1] += (false===greedy) ? '+?' : '+';
            return self;
        },
        
        sub: function( partialRegex, withParen ) {
            var self = this;
            if ( undef !== partialRegex )
            {
                if ( withParen ) partialRegex = '(' + partialRegex + ')';
                self.$parts[self.$level].part.push( partialRegex );
            }
            return self;
        },
        
        literal: function( literalStr, withParen ) {
            var self = this;
            if ( undef !== literalStr )
            {
                literalStr = withParen ? ('(' + esc(literalStr) + ')') : esc(literalStr);
                self.$parts[self.$level].part.push( literalStr );
            }
            return self;
        },
        
        startOfInput: function( ) {
            var self = this;
            self.$parts[self.$level].part.push('^');
            return self;
        },
        
        endOfInput: function( ) {
            var self = this;
            self.$parts[self.$level].part.push('$');
            return self;
        },
        
        any: function( ) {
            var self = this;
            self.$parts[self.$level].part.push('.');
            return self;
        },
        
        space: function( positive ) {
            var self = this;
            self.$parts[self.$level].part.push((false===positive) ? '\\S' : '\\s');
            return self;
        },
        
        digit: function( positive ) {
            var self = this;
            self.$parts[self.$level].part.push((false===positive) ? '\\D' : '\\d');
            return self;
        },
        
        word: function( positive ) {
            var self = this;
            self.$parts[self.$level].part.push((false===positive) ? '\\W' : '\\w');
            return self;
        },
        
        boundary: function( positive ) {
            var self = this;
            self.$parts[self.$level].part.push((false===positive) ? '\\B' : '\\b');
            return self;
        },
        
        LF: function( ) {
            var self = this;
            self.$parts[self.$level].part.push('\\n');
            return self;
        },
        
        CR: function( ) {
            var self = this;
            self.$parts[self.$level].part.push('\\r');
            return self;
        },
        
        TAB: function( ) {
            var self = this;
            self.$parts[self.$level].part.push('\\t');
            return self;
        },
        
        CTRL: function( _char ) {
            var self = this;
            if ( _char ) self.$parts[self.$level].part.push('\\c'+_char);
            return self;
        },
        
        backSpace: function( ) {
            var self = this;
            self.$parts[self.$level].part.push('[\\b]');
            return self;
        },
        
        backReference: function( n ) {
            var self = this;
            self.$parts[self.$level].part.push('\\'+parseInt(n, 10));
            return self;
        },
        
        characters: function( ) {
            var self = this;
            if ( T_CHARGROUP == self.$parts[self.$level].type )
            {
                var chars = getArgs(arguments, 1).map(esc).join('');
                self.$parts[self.$level].part.push( chars );
            }
            return self;
        },
        
        range: function( start, end ) {
            var self = this;
            if ( T_CHARGROUP == self.$parts[self.$level].type )
            {
                if ( undef === start || undef === end ) return self;
                var range = esc(start) + '-' + esc(end);
                self.$parts[self.$level].part.push( range );
            }
            return self;
        },
        
        alternate: function( ) {
            var self = this;
            self.$level++;
            self.$parts.push({part: [], type: T_EITHER, flag: ''});
            return self;
        },
        
        group: function( ) {
            var self = this;
            self.$level++;
            self.$parts.push({part: [], type: T_GROUP, flag: ''});
            return self;
        },
        
        nonCaptureGroup: function( ) {
            var self = this;
            self.$level++;
            self.$parts.push({part: [], type: T_GROUP, flag: '?:'});
            return self;
        },
        
        lookAheadGroup: function( positive ) {
            var self = this;
            self.$level++;
            self.$parts.push({part: [], type: T_GROUP, flag: (false===positive) ? '?!' : '?='});
            return self;
        },
        
        characterGroup: function( positive ) {
            var self = this;
            self.$level++;
            self.$parts.push({part: [], type: T_CHARGROUP, flag: (false===positive) ? '^' : ''});
            return self;
        },
        
        end: function( ) {
            var self = this, prev = self.$parts.pop() || {}, 
                type = prev.type, 
                flag = prev.flag || '',
                part = prev.part || [],
                level
            ;
            
            if (0 < self.$level)
            {
                level = --self.$level;
                
                if ( (T_EITHER|T_GROUP) & type )
                    self.$parts[level].part.push('(' + flag + part.join('|') + ')');
                
                else if ( T_CHARGROUP & type )
                    self.$parts[level].part.push('[' + flag + part.join('') + ']');
            }
            return self;
        }
    };
    // aliases
    var CP = Composer[PROTO];
    CP.startOfLine = CP.startOfInput;
    CP.endOfLine = CP.endOfInput;
    CP.match = CP.literal;
    CP.subRegex = CP.sub;
    CP.lineFeed = CP.LF;
    CP.carriageReturn = CP.CR;
    CP.tabulate = CP.tab = CP.TAB;
    CP.control = CP.CTRL;
    CP.wordBoundary = CP.boundary;
    CP.either = CP.alternate;
    CP.chars = CP.characters;
    CP.charGroup = CP.characterGroup;
    CP.subGroup = CP.subgroup = CP.group;
    CP.nonCaptureSubGroup = CP.nonCaptureGroup;
    CP.lookAheadSubGroup = CP.lookAheadGroup;

    /* main code ends here */
    /* export the module */
    return Composer;
});