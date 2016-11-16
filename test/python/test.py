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
    print ('RegexAnalyzer Module loaded succesfully')


def echo_( o='' ):
    print( str(o) + "\n" )

echo_("Testing Analyzer.VERSION = " + RegexAnalyzer.VERSION)
echo_("=========================================")

# test it
inregex = '/xyz([abc0-9]){2,3}/i'
anal = RegexAnalyzer( inregex )
peekChars = anal.peek( )
minLen = anal.minimum( )
maxLen = anal.maximum( )
sampleStr = anal.sample( 1, 5 )
test_regex = anal.compile( )
for i in range(5):
    sampleStr[i] = {'sample':sampleStr[i], 'match':'yes' if test_regex.match(sampleStr[i]) else 'no'}

echo_("Input                                       : " + inregex)
echo_("Regular Expression                          : " + anal.re)
echo_("Regular Expression Flags                    : " + ','.join(anal.fl.keys()))
echo_("=============================================")
echo_("Regular Expression Syntax Tree              : ")
echo_(pprint.pformat(anal.tree(True), 4))
echo_("=============================================")
echo_("Regular Expression Peek Characters          : ")
echo_(pprint.pformat({'positive':list(peekChars['positive'].keys()),'negative':list(peekChars['negative'].keys())}, 4))
echo_("=============================================")
echo_("Regular Expression Minimum / Maximum Length : ")
echo_(pprint.pformat({'minimum':minLen,'maximum':'unlimited' if -1 == maxLen else maxLen}, 4))
echo_("=============================================")
echo_("Regular Expression Sample Match Strings     : ")
echo_(pprint.pformat(sampleStr, 4))
echo_("=============================================")
