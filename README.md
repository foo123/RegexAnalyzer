regex-analyzer and regex-composer
=================================

* A simple Regular Expression Analyzer for JavaScript / PHP / Python
* A simple and intuitive Regular Expression Composer for JavaScript / PHP / Python


*PHP / Python implementations in progress*


These are used mostly as parts of other projects but uploaded here as standalone.

The analyzer needs a couple of extensions but overall works good.


See /test/test.js under /test folder for examples of how to use


**RegExAnalyzer Live Example:**  

[![Live Example](/test/screenshot.png)](https://foo123.github.com/examples/regex-analyzer/)


**RegExComposer Live Example:**  

[![Live Example](/test/screenshot2.png)](https://foo123.github.com/examples/regex-composer/)


**RegExComposer Example:**  (see /test/test.js)

```javascript

// eg. in node

var Composer = require('../build/regexcomposer.js').RegExComposer;
var outregex = new Composer()
                    
                    .startOfLine()
                    
                    .either()
                        
                        .characterGroup(false)
                            .characters('a', 'b', 'c', '.')
                            .range('d', 'f')
                        .end()
                        
                        .match('**aabb**')
                        
                        .any()
                        
                        .space()
                        
                        .digit(false).oneOrMore()
                    
                    .end()
                    
                    .zeroOrMore(false)
                    
                    .endOfLine()
                    
                    .compose('i');
    
echo("Composed: " + outregex.toString());
echo("Expected: " + "/^([^abc\\.d-f]|\\*\\*aabb\\*\\*|.|\\s|\\D+)*?$/i");
    
```

**Result**

```text

Composed: /^([^abc\.d-f]|\*\*aabb\*\*|.|\s|\D+)*?$/i
Expected: /^([^abc\.d-f]|\*\*aabb\*\*|.|\s|\D+)*?$/i

```