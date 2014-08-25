/**
*
*   RegExComposer
*   @version: 0.3.2
*
*   A simple and intuitive Regular Expression Composer in JavaScript
*   https://github.com/foo123/regex-analyzer
*
**/!function ( root, name, deps, factory, undef ) {

    var isNode = (typeof global !== "undefined" && {}.toString.call(global) == '[object global]') ? 1 : 0,
        isBrowser = (!isNode && typeof navigator !== "undefined") ? 1 : 0, 
        isWorker = (typeof importScripts === "function" && navigator instanceof WorkerNavigator) ? 1 : 0,
        A = Array, AP = A.prototype
    ;
    // Get current filename/path
    var getCurrentPath = function() {
            var file = null;
            if ( isNode ) 
            {
                // http://nodejs.org/docs/latest/api/globals.html#globals_filename
                // this should hold the current file in node
                file = __filename;
                return { path: __dirname, file: __filename };
            }
            else if ( isWorker )
            {
                // https://developer.mozilla.org/en-US/docs/Web/API/WorkerLocation
                // this should hold the current url in a web worker
                file = self.location.href;
            }
            else if ( isBrowser )
            {
                // get last script (should be the current one) in browser
                var scripts;
                if ((scripts = document.getElementsByTagName('script')) && scripts.length) 
                    file  = scripts[scripts.length - 1].src;
            }
            
            if ( file )
                return { path: file.split('/').slice(0, -1).join('/'), file: file };
            return { path: null, file: null };
        },
        thisPath = getCurrentPath(),
        makePath = function(base, dep) {
            if ( isNode )
            {
                //return require('path').join(base, dep);
                return dep;
            }
            if ( "." == dep.charAt(0) ) 
            {
                base = base.split('/');
                dep = dep.split('/'); 
                var index = 0, index2 = 0, i, l = dep.length, l2 = base.length;
                
                for (i=0; i<l; i++)
                {
                    if ( /^\.\./.test( dep[i] ) )
                    {
                        index++;
                        index2++;
                    }
                    else if ( /^\./.test( dep[i] ) )
                    {
                        index2++;
                    }
                    else
                    {
                        break;
                    }
                }
                index = ( index >= l2 ) ? 0 : l2-index;
                dep = base.slice(0, index).concat( dep.slice( index2 ) ).join('/');
            }
            return dep;
        }
    ;
    
    //
    // export the module in a umd-style generic way
    deps = ( deps ) ? [].concat(deps) : [];
    var i, dl = deps.length, ids = new A( dl ), paths = new A( dl ), fpaths = new A( dl ), mods = new A( dl ), _module_, head;
        
    for (i=0; i<dl; i++) { ids[i] = deps[i][0]; paths[i] = deps[i][1]; fpaths[i] = /\.js$/i.test(paths[i]) ? makePath(thisPath.path, paths[i]) : makePath(thisPath.path, paths[i]+'.js'); }
    
    // node, commonjs, etc..
    if ( 'object' == typeof( module ) && module.exports ) 
    {
        if ( undef === module.exports[name] )
        {
            for (i=0; i<dl; i++)  mods[i] = module.exports[ ids[i] ] || require( fpaths[i] )[ ids[i] ];
            _module_ = factory.apply(root, mods );
            // allow factory just to add to existing modules without returning a new module
            module.exports[ name ] = _module_ || 1;
        }
    }
    
    // amd, etc..
    else if ( 'function' == typeof( define ) && define.amd ) 
    {
        define( ['exports'].concat( paths ), function( exports ) {
            if ( undef === exports[name] )
            {
                var args = AP.slice.call( arguments, 1 ), dl = args.length;
                for (var i=0; i<dl; i++)   mods[i] = exports[ ids[i] ] || args[ i ];
                _module_ = factory.apply(root, mods );
                // allow factory just to add to existing modules without returning a new module
                exports[ name ] = _module_ || 1;
            }
        });
    }
    
    // web worker
    else if ( isWorker ) 
    {
        for (i=0; i<dl; i++)  
        {
            if ( !self[ ids[i] ] ) importScripts( fpaths[i] );
            mods[i] = self[ ids[i] ];
        }
        _module_ = factory.apply(root, mods );
        // allow factory just to add to existing modules without returning a new module
        self[ name ] = _module_ || 1;
    }
    
    // browsers, other loaders, etc..
    else
    {
        if ( undef === root[name] )
        {
            /*
            for (i=0; i<dl; i++)  mods[i] = root[ ids[i] ];
            _module_ = factory.apply(root, mods );
            // allow factory just to add to existing modules without returning a new module
            root[name] = _module_ || 1;
            */
            
            // load javascript async using <script> tags in browser
            var loadJs = function(url, callback) {
                head = head || document.getElementsByTagName("head")[0];
                var done = 0, script = document.createElement('script');
                
                script.type = 'text/javascript';
                script.language = 'javascript';
                script.src = url;
                script.onload = script.onreadystatechange = function() {
                    if (!done && (!script.readyState || script.readyState == 'loaded' || script.readyState == 'complete'))
                    {
                        done = 1;
                        script.onload = script.onreadystatechange = null;
                        head.removeChild( script );
                        script = null;
                        if ( callback )  callback();
                    }
                }
                // load it
                head.appendChild( script );
            };

            var loadNext = function(id, url, callback) { 
                    if ( !root[ id ] ) 
                        loadJs( url, callback ); 
                    else
                        callback();
                },
                continueLoad = function( i ) {
                    return function() {
                        if ( i < dl )  mods[ i ] = root[ ids[ i ] ];
                        if ( ++i < dl )
                        {
                            loadNext( ids[ i ], fpaths[ i ], continueLoad( i ) );
                        }
                        else
                        {
                            _module_ = factory.apply(root, mods );
                            // allow factory just to add to existing modules without returning a new module
                            root[ name ] = _module_ || 1;
                        }
                    };
                }
            ;
            if ( dl ) 
            {
                loadNext( ids[ 0 ], fpaths[ 0 ], continueLoad( 0 ) );
            }
            else
            {
                _module_ = factory.apply(root, mods );
                // allow factory just to add to existing modules without returning a new module
                root[ name ] = _module_ || 1;
            }
        }
    }


}(  /* current root */          this, 
    /* module name */           "RegExComposer",
    /* module dependencies */   null, 
    /* module factory */        function(  ) {

        /* custom exports object */
        var EXPORTS = {};
        
        /* main code starts here */

/**
*
*   RegExComposer
*   @version: 0.3.2
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
    
    Composer.VERSION = "0.3.2";
    
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
    
    exports.RegExComposer = Composer;
    
})(EXPORTS);

    /* main code ends here */
    
    /* export the module "RegExComposer" */
    return EXPORTS["RegExComposer"];
});