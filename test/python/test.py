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
inregex = '/(?P<named_group>[abcde]+)fgh(?P=named_group)(?# a comment)/i'
anal = RegexAnalyzer( inregex )
peekChars = anal.peek( )
minLen = anal.minimum( )
maxLen = anal.maximum( )
regexp = anal.compile( {'i':1 if 'i' in anal.fl else 0} )
sampleStr = anal.sample( 1, 5 )
groups = anal.groups()
for i in range(5):
    m = regexp.match(sampleStr[i])
    sampleStr[i] = {'sample':sampleStr[i], 'match':'yes' if m else 'no', 'groups': {}}
    if m:
        for group,index in groups.items(): sampleStr[i]['groups'][group] = m.group(index)

echo_("Input                                       : " + inregex)
echo_("Regular Expression                          : " + anal.input())
echo_("Regular Expression Flags                    : " + ','.join(anal.fl.keys()))
echo_("Reconstructed Regular Expression            : " + anal.source())
echo_("=============================================")
echo_("Regular Expression Syntax Tree              : ")
echo_(pprint.pformat(anal.tree(True), 4))
echo_("=============================================")
echo_("Regular Expression (Named) Matched Groups   : ")
echo_(pprint.pformat(groups, 4))
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
