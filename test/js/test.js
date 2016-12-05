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
    anal, peekChars, sampleStr, minLen, maxLen, groups, regexp, inregex = /*process.argv[2] || /xyz([abc0-9]){2,3}/i*/"/(?<named_group>[ab\\u0012cde]+)\\x12/gi"
;

echo("Testing Analyzer.VERSION = " + Analyzer.VERSION);
echo("=========================================");

// test it
anal = Analyzer( inregex );
peekChars = anal.peek( );
minLen = anal.minimum( );
maxLen = anal.maximum( );
regexp = anal.compile( {i:anal.fl.i?1:0} );
sampleStr = anal.sample( 1, 5 );
groups = anal.groups();
for(var i=0; i<5; i++)
{
    var m = sampleStr[i].match(regexp);
    sampleStr[i] = {sample:sampleStr[i], match:(m ? 'yes' : 'no'), groups: {}};
    for(var g in groups)
        if ( groups.hasOwnProperty(g) )
            sampleStr[i].groups[g] = m[regexp.group(g)];
}

echo("Input                                       : " + inregex.toString( ));
echo("Regular Expression                          : " + anal.input());
echo("Regular Expression Flags                    : " + Object.keys(anal.fl).join(','));
echo("Regular Expression Reconstructed            : " + anal.source());
echo("=============================================");
echo("Regular Expression Syntax Tree              : ");
echo(JSON.stringify(anal.tree(true), null, 4));
echo("=============================================");
echo("Regular Expression (Named) Matched Groups   : ");
echo(JSON.stringify(groups, null, 4));
echo("=============================================");
echo("Regular Expression Peek Characters          : ");
echo(JSON.stringify({positive:Object.keys(peekChars.positive||{}),negative:Object.keys(peekChars.negative||{})}, null, 4));
echo("=============================================");
echo("Regular Expression Minimum / Maximum Length : ");
echo(JSON.stringify({minimum:minLen,maximum:-1===maxLen?'unlimited':maxLen}, null, 4));
echo("=============================================");
echo("Regular Expression Sample Match Strings     : ");
echo(JSON.stringify(sampleStr, null, 4));
echo("=============================================");
