//
// use as: node test.js "your_regex_here" > output.txt

var echo = console.log;

echo("Testing Composer");
echo("================");

var Composer = require('../../build/js/regexcomposer.js').RegExComposer;
var identifierSubRegex = new Composer()
                
                .characterGroup()
                    .characters('_')
                    .range('a', 'z')
                .end()
                
                .characterGroup()
                    .characters('_')
                    .range('a', 'z')
                    .range('0', '9')
                .end()
                
                .zeroOrMore()
            
                .partial();

var outregex = new Composer()
                    
                    .startOfLine()
                    
                    .either()
                        
                        .sub(identifierSubRegex)
                        
                        .match('**aabb**')
                        
                        .any()
                        
                        .space()
                        
                        .digit(false).oneOrMore()
                    
                    .end()
                    
                    .zeroOrMore(false)
                    
                    .endOfLine()
                    
                    .compose('i');
    
echo("Partial: " + identifierSubRegex);
echo("Composed: " + outregex.toString());
echo("Expected: " + "/^([_a-z][_a-z0-9]*|\\*\\*aabb\\*\\*|.|\\s|\\D+)*?$/i");
echo("================");
echo();

echo("Testing Analyzer");
echo("================");

var Analyzer = require('../../build/js/regexanalyzer.js').RegExAnalyzer;
var inregex = process.argv[2] || /^(?:[^\u0000-\u1234a-zA-Z\d\-\.\*\+\?\^\$\{\}\(\)\|\[\]\/\\]+)|abcdef\u1234{1,}/gmi;
var anal = new Analyzer(inregex);

// test it
anal.analyze();

echo("Input: " + inregex.toString());
echo();
echo("Regular Expression: " + anal.regex);
echo();
echo("Regular Expression Flags: ");
echo(anal.flags);
echo();
echo("Regular Expression Parts: ");
echo(JSON.stringify(anal.parts, null, 4));
echo("================");
echo();
