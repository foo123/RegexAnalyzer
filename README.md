Regex.Analyzer and Regex.Composer
=================================

A generic, simple &amp; intuitive **Regular Expression Analyzer &amp; Composer** for PHP, Python,  Javascript


**Regex v.1.2.0** (js only)


These were used mostly as parts of other projects but uploaded here as standalone.


See `/test/js/test.js` under `/test` folder for examples of how to use


**Regex.Analyzer Live Playground Example:**

[![Live Playground Example](/test/screenshot.png)](https://foo123.github.com/examples/regex-analyzer/)


**Regex.Composer Live Playground Example:**

[![Live Playground Example](/test/screenshot2.png)](https://foo123.github.com/examples/regex-composer/)


**Example:**  (see `/test/js/test.js`)

```javascript
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
```

**Result**

```text
Regex.VERSION = 1.0.0
Testing Regex.Composer
===============================================================
Partial        : [_a-z][_a-z0-9]*
Composed       : /^(?:[_a-z][_a-z0-9]*|(\*\*aabb\*\*)|.|\s|\D+)*?\1$/i
Expected       : /^(?:[_a-z][_a-z0-9]*|(\*\*aabb\*\*)|.|\s|\D+)*?\1$/i
Output         : {
    "source": "^(?:[_a-z][_a-z0-9]*|(\\*\\*aabb\\*\\*)|.|\\s|\\D+)*?\\1$",
    "flags": "i",
    "groups": {
        "1": 1,
        "token": 1
    },
    "pattern": {}
}
===============================================================

Testing Regex.Analyzer
===============================================================
Input                                       : /(?P<named_group>[abcde]+)fgh(?P=named_group)(?# a comment)/i
Regular Expression                          : (?P<named_group>[abcde]+)fgh(?P=named_group)(?# a comment)
Regular Expression Flags                    : i
Reconstructed Regular Expression            : ([abcde]+)fgh\1
===============================================================
Regular Expression Syntax Tree              :
{
    "type": "Sequence",
    "value": [
        {
            "type": "Group",
            "value": {
                "type": "Sequence",
                "value": [
                    {
                        "type": "Quantifier",
                        "value": {
                            "type": "CharacterGroup",
                            "value": [
                                {
                                    "type": "Characters",
                                    "value": [
                                        "a",
                                        "b",
                                        "c",
                                        "d",
                                        "e"
                                    ]
                                }
                            ]
                        },
                        "flags": {
                            "MatchOneOrMore": 1,
                            "min": 1,
                            "max": -1,
                            "isGreedy": 1
                        }
                    }
                ]
            },
            "flags": {
                "NamedGroup": 1,
                "GroupName": "named_group",
                "GroupIndex": 1
            }
        },
        {
            "type": "String",
            "value": "fgh"
        },
        {
            "type": "Special",
            "value": "1",
            "flags": {
                "BackReference": 1,
                "GroupName": "named_group",
                "GroupIndex": 1
            }
        },
        {
            "type": "Comment",
            "value": " a comment"
        }
    ]
}
===============================================================
Regular Expression (Named) Matched Groups   :
{
    "1": 1,
    "named_group": 1
}
===============================================================
Regular Expression Peek Characters          :
{
    "positive": [
        "a",
        "b",
        "c",
        "d",
        "e",
        "A",
        "B",
        "C",
        "D",
        "E"
    ],
    "negative": []
}
===============================================================
Regular Expression Minimum / Maximum Length :
{
    "minimum": 5,
    "maximum": "unlimited"
}
===============================================================
Regular Expression Sample Match Strings     :
[
    {
        "sample": "AdbFGHAdb",
        "match": "yes",
        "groups": {
            "1": "Adb",
            "named_group": "Adb"
        }
    },
    {
        "sample": "CDfghCD",
        "match": "yes",
        "groups": {
            "1": "CD",
            "named_group": "CD"
        }
    },
    {
        "sample": "CBCfghCBC",
        "match": "yes",
        "groups": {
            "1": "CBC",
            "named_group": "CBC"
        }
    },
    {
        "sample": "BbaAFGHBbaA",
        "match": "yes",
        "groups": {
            "1": "BbaA",
            "named_group": "BbaA"
        }
    },
    {
        "sample": "EfghE",
        "match": "yes",
        "groups": {
            "1": "E",
            "named_group": "E"
        }
    }
]
===============================================================
```

**see also:**

* [Abacus](https://github.com/foo123/Abacus) Computer Algebra and Symbolic Computation System for Combinatorics and Algebraic Number Theory for JavaScript and Python
* [SciLite](https://github.com/foo123/SciLite) Scientific Computing Environment similar to Octave/Matlab in pure JavaScript
* [TensorView](https://github.com/foo123/TensorView) view array data as multidimensional tensors of various shapes efficiently
* [FILTER.js](https://github.com/foo123/FILTER.js) video and image processing and computer vision Library in pure JavaScript (browser and nodejs)
* [HAAR.js](https://github.com/foo123/HAAR.js) image feature detection based on Haar Cascades in JavaScript (Viola-Jones-Lienhart et al Algorithm)
* [HAARPHP](https://github.com/foo123/HAARPHP) image feature detection based on Haar Cascades in PHP (Viola-Jones-Lienhart et al Algorithm)
* [Fuzzion](https://github.com/foo123/Fuzzion) a library of fuzzy / approximate string metrics for PHP, JavaScript, Python
* [Matchy](https://github.com/foo123/Matchy) a library of string matching algorithms for PHP, JavaScript, Python
* [Regex Analyzer/Composer](https://github.com/foo123/RegexAnalyzer) Regular Expression Analyzer and Composer for PHP, JavaScript, Python
* [Xpresion](https://github.com/foo123/Xpresion) a simple and flexible eXpression parser engine (with custom functions and variables support), based on [GrammarTemplate](https://github.com/foo123/GrammarTemplate), for PHP, JavaScript, Python
* [GrammarTemplate](https://github.com/foo123/GrammarTemplate) grammar-based templating for PHP, JavaScript, Python
* [codemirror-grammar](https://github.com/foo123/codemirror-grammar) transform a formal grammar in JSON format into a syntax-highlight parser for CodeMirror editor
* [ace-grammar](https://github.com/foo123/ace-grammar) transform a formal grammar in JSON format into a syntax-highlight parser for ACE editor
* [prism-grammar](https://github.com/foo123/prism-grammar) transform a formal grammar in JSON format into a syntax-highlighter for Prism code highlighter
* [highlightjs-grammar](https://github.com/foo123/highlightjs-grammar) transform a formal grammar in JSON format into a syntax-highlight mode for Highlight.js code highlighter
* [syntaxhighlighter-grammar](https://github.com/foo123/syntaxhighlighter-grammar) transform a formal grammar in JSON format to a highlight brush for SyntaxHighlighter code highlighter
* [MOD3](https://github.com/foo123/MOD3) 3D Modifier Library in JavaScript
* [Geometrize](https://github.com/foo123/Geometrize) Computational Geometry and Rendering Library for JavaScript
* [Plot.js](https://github.com/foo123/Plot.js) simple and small library which can plot graphs of functions and various simple charts and can render to Canvas, SVG and plain HTML
* [CanvasLite](https://github.com/foo123/CanvasLite) an html canvas implementation in pure JavaScript
* [Rasterizer](https://github.com/foo123/Rasterizer) stroke and fill lines, rectangles, curves and paths, without canvas
* [Gradient](https://github.com/foo123/Gradient) create linear, radial, conic and elliptic gradients and image patterns without canvas
* [css-color](https://github.com/foo123/css-color) simple class to parse and manipulate colors in various formats
* [PatternMatchingAlgorithms](https://github.com/foo123/PatternMatchingAlgorithms) library of Pattern Matching Algorithms in JavaScript using [Matchy](https://github.com/foo123/Matchy)
* [SortingAlgorithms](https://github.com/foo123/SortingAlgorithms) library of Sorting Algorithms in JavaScript
