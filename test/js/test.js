//
// use as: node test.js "your_regex_here" > output.txt
"use strict";

var echo = console.log;


var Composer = require('../../src/js/RegexComposer.js');

echo("Testing Composer.VERSION = " + Composer.VERSION);
echo("================");

var identifierSubRegex = Composer( )
                
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

var outregex = Composer( )
                    
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

var Analyzer = require('../../src/js/RegexAnalyzer.js'),
    anal, peekChars, sampleStr, minLen, inregex = process.argv[2] || /xyz([abc0-9]){2,3}/i
;

echo("Testing Analyzer.VERSION = " + Analyzer.VERSION);
echo("================");

// test it
anal = Analyzer( inregex );
peekChars = anal.peek( );
sampleStr = anal.sample( );
minLen = anal.minimum( );

echo("Input                         : " + inregex.toString( ));
echo("Regular Expression            : " + anal._regex);
echo("Regular Expression Flags      : " + Object.keys(anal._flags).join(','));
echo("Regular Expression Structure :");
echo(JSON.stringify(anal._parts.toObject(), null, 4));
echo();
echo("Regular Expression Peek Characters: ");
echo(JSON.stringify({positive:Object.keys(peekChars.positive||{}),negative:Object.keys(peekChars.negative||{})}, null, 4));
echo();
echo("Regular Expression Minimum Length: ");
echo(minLen);
echo();
echo("Regular Expression Sample Match String: ");
echo(sampleStr + ' -> ' + (inregex.test(sampleStr) ? 'Matched' : 'NOT Matched'));
echo("================");
echo();
