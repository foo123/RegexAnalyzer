#!/usr/bin/env python

import os, sys
import pprint

# import the Dromeo.py engine (as a) module, probably you will want to place this in another dir/package
import imp
RAModulePath = os.path.join(os.path.dirname(__file__), '../../src/python/')
try:
    RAFp, RAPath, RADesc  = imp.find_module('regexanalyzer', [RAModulePath])
    RegExAnalyzer = getattr( imp.load_module('regexanalyzer', RAFp, RAPath, RADesc), 'RegExAnalyzer' )
except ImportError as exc:
    RegExAnalyzer = None
    sys.stderr.write("Error: failed to import module ({})".format(exc))
finally:
    if RAFp: RAFp.close()

if not RegExAnalyzer:
    print ('Could not load the RegExAnalyzer Module')
    sys.exit(1)
else:    
    print ('RegExAnalyzer Module loaded succesfully')


def echo_( o='' ):
    print( str(o) + "\n" )

echo_("Testing Analyzer.VERSION = " + RegExAnalyzer.VERSION)
echo_("================");

# test it
inregex = '/xyz[abc0-9]{2,3}/i'
anal = RegExAnalyzer( inregex )
peekChars = anal.getPeekChars( )
sampleStr = anal.generateSample( )
test_regex = anal.getRegex()

echo_("Input: " + inregex)
echo_()
echo_("Regular Expression: " + anal._regex)
echo_()
echo_("Regular Expression Flags: ")
echo_(pprint.pformat(anal._flags, 4))
echo_()
echo_("Regular Expression Parts: ")
echo_(pprint.pformat(anal._parts, 4))
echo_()
echo_("Regular Expression Peek Characters: ")
echo_(pprint.pformat(peekChars, 4))
echo_()
echo_("Regular Expression Sample Match String: ")
echo_(sampleStr + ' -> ' + ('Matched' if test_regex.match(sampleStr) else 'NOT Matched'))
echo_("================")
echo_()
