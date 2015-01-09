#!/usr/bin/env python

import os, sys
import pprint

# import the Dromeo.py engine (as a) module, probably you will want to place this in another dir/package
import imp
RAModulePath = os.path.join(os.path.dirname(__file__), '../../src/python/')
try:
    RAFp, RAPath, RADesc  = imp.find_module('RegexAnalyzer', [RAModulePath])
    RegexAnalyzer = getattr( imp.load_module('RegexAnalyzer', RAFp, RAPath, RADesc), 'RegexAnalyzer' )
except ImportError as exc:
    RegexAnalyzer = None
    sys.stderr.write("Error: failed to import module ({})".format(exc))
finally:
    if RAFp: RAFp.close()

if not RegexAnalyzer:
    print ('Could not load the RegExAnalyzer Module')
    sys.exit(1)
else:    
    print ('RegExAnalyzer Module loaded succesfully')


def echo_( o='' ):
    print( str(o) + "\n" )

echo_("Testing Analyzer.VERSION = " + RegexAnalyzer.VERSION)
echo_("================");

# test it
inregex = '/xyz([abc0-9]){2,3}/i'
anal = RegexAnalyzer( inregex )
peekChars = anal.peek( )
sampleStr = anal.sample( )
test_regex = anal.getRegex()

echo_("Input: " + inregex)
echo_()
echo_("Regular Expression: " + anal._regex)
echo_()
echo_("Regular Expression Flags: ")
echo_(pprint.pformat(anal._flags, 4))
echo_()
echo_("Regular Expression Parts: ")
echo_(pprint.pformat(anal._parts.toObject(), 4))
echo_()
echo_("Regular Expression Peek Characters: ")
echo_(pprint.pformat(peekChars, 4))
echo_()
echo_("Regular Expression Sample Match String: ")
echo_(sampleStr + ' -> ' + ('Matched' if test_regex.match(sampleStr) else 'NOT Matched'))
echo_("================")
echo_()
