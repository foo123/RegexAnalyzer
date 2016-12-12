//
// use as: node test.js "your_regex_here" > output.txt
"use strict";

var echo = console.log;


var Regex = require('../../src/js/Regex.js');

echo("Regex.VERSION = " + Regex.VERSION);

echo("Testing Regex.Composer");
echo("===============================================================");

var identifierSubRegex = Regex.Composer( )
                
                .characterGroup( )
                    .characters( '_' )
                    .range( 'a', 'z' )
                .end( )
                
                .characterGroup( )
                    .characters( '_' )
                    .range( 'a', 'z' )
                    .range( '0', '9' )
                .end( ).zeroOrMore( )
            
                .partial( );

var outregex = Regex.Composer( )
                    
                .SOL( )
                
                .nonCaptureGroup( ).either( )
                    .regexp( identifierSubRegex )
                    .namedGroup( 'token' ).literal( '**aabb**' ).end( )
                    .any( )
                    .space( )
                    .digit( false ).oneOrMore( )
                .end( 2 ).zeroOrMore( false )
                
                .backReference( 'token' )
                
                .EOL( )
                
                .compose( 'i' );
    
echo("Partial        : " + identifierSubRegex);
echo("Composed       : " + outregex.pattern.toString());
echo("Expected       : " + "/^(?:[_a-z][_a-z0-9]*|(\\*\\*aabb\\*\\*)|.|\\s|\\D+)*?\\1$/i");
echo("Output         : " + JSON.stringify(outregex, null, 4));
echo("===============================================================");
echo();

var anal, peekChars, sampleStr, minLen, maxLen, groups, regexp,
    inregex = "/(?P<named_group>[abcde]+)fgh(?P=named_group)(?# a comment)/i";
    /*process.argv[2] || /xyz([abc0-9]){2,3}/i*/

echo("Testing Regex.Analyzer");
echo("===============================================================");

// test it
anal = Regex.Analyzer( inregex );
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
    if ( m )
    {
        for(var g in groups)
            if ( Object.prototype.hasOwnProperty.call(groups,g) )
                sampleStr[i].groups[g] = m[groups[g]];
    }
}

echo("Input                                       : " + inregex.toString( ));
echo("Regular Expression                          : " + anal.input());
echo("Regular Expression Flags                    : " + Object.keys(anal.fl).join(','));
echo("Reconstructed Regular Expression            : " + anal.source());
echo("===============================================================");
echo("Regular Expression Syntax Tree              : ");
echo(JSON.stringify(anal.tree(true), null, 4));
echo("===============================================================");
echo("Regular Expression (Named) Matched Groups   : ");
echo(JSON.stringify(groups, null, 4));
echo("===============================================================");
echo("Regular Expression Peek Characters          : ");
echo(JSON.stringify({positive:Object.keys(peekChars.positive||{}),negative:Object.keys(peekChars.negative||{})}, null, 4));
echo("===============================================================");
echo("Regular Expression Minimum / Maximum Length : ");
echo(JSON.stringify({minimum:minLen,maximum:-1===maxLen?'unlimited':maxLen}, null, 4));
echo("===============================================================");
echo("Regular Expression Sample Match Strings     : ");
echo(JSON.stringify(sampleStr, null, 4));
echo("===============================================================");
