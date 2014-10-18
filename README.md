regex-analyzer and regex-composer
=================================

* A simple Regular Expression Analyzer for PHP, Python, Node/JS, ActionScript (TODO)
* A simple and intuitive Regular Expression Composer for PHP, Python, Node/JS, ActionScript (TODO)


*PHP / Python / ActionScript implementations in progress*


These are used mostly as parts of other projects but uploaded here as standalone.

The analyzer needs a couple of extensions but overall works good.


See /test/js/test.js under /test folder for examples of how to use


**RegExAnalyzer Live Example:**  

[![Live Example](/test/screenshot.png)](https://foo123.github.com/examples/regex-analyzer/)


**RegExComposer Live Example:**  

[![Live Example](/test/screenshot2.png)](https://foo123.github.com/examples/regex-composer/)


**RegExComposer Example:**  (see /test/js/test.js)

```javascript
var echo = console.log;

echo("Testing Composer");
echo("================");

var Composer = require('../../src/js/regexcomposer.js');
var identifierSubRegex = new Composer( )
                
                .characterGroup( )
                    .characters( '_' )
                    .range( 'a', 'z' )
                .end( )
                
                .characterGroup( )
                    .characters( '_' )
                    .range( 'a', 'z' )
                    .range( '0', '9' )
                .end( )
                
                .zeroOrMore( )
            
                .partial( );

var outregex = new Composer( )
                    
                    .startOfLine( )
                    
                    .either( )
                        
                        .sub( identifierSubRegex )
                        
                        .match( '**aabb**' )
                        
                        .any( )
                        
                        .space( )
                        
                        .digit( false ).oneOrMore( )
                    
                    .end( )
                    
                    .zeroOrMore( false )
                    
                    .endOfLine( )
                    
                    .compose( 'i' );
    
echo("Partial: " + identifierSubRegex);
echo("Composed: " + outregex.toString());
echo("Expected: " + "/^([_a-z][_a-z0-9]*|\\*\\*aabb\\*\\*|.|\\s|\\D+)*?$/i");
echo("================");
echo();
    
```

**Result**

```text

Composed: /^([^abc\.d-f]|\*\*aabb\*\*|.|\s|\D+)*?$/i
Expected: /^([^abc\.d-f]|\*\*aabb\*\*|.|\s|\D+)*?$/i

```