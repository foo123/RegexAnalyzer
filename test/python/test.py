#!/usr/bin/env python

import os, sys, re
import pprint

# import the module, probably you will want to place this in another dir/package
import imp
RAModulePath = os.path.join(os.path.dirname(__file__), '../../src/python/')
try:
    RAFp, RAPath, RADesc  = imp.find_module('Regex', [RAModulePath])
    Regex = getattr( imp.load_module('Regex', RAFp, RAPath, RADesc), 'Regex' )
except ImportError as exc:
    Regex = None
    sys.stderr.write("Error: failed to import module ({})".format(exc))
finally:
    if RAFp: RAFp.close()

if not Regex:
    print ('Could not load the Regex Module')
    sys.exit(1)
else:    
    print ('Regex Module loaded succesfully')


def echo_( o='' ):
    print( str(o) )

echo_("Regex.VERSION = " + Regex.VERSION)

echo_("Testing Regex.Composer")
echo_("===============================================================")

identifierSubRegex = Regex.Composer( ).characterGroup( ).characters( '_' ).range( 'a', 'z' ).end( ).characterGroup( ).characters( '_' ).range( 'a', 'z' ).range( '0', '9' ).end( ).zeroOrMore( ).partial( )

outregex = Regex.Composer( ).SOL( ).nonCaptureGroup( ).either( ).regexp( identifierSubRegex ).or_( ).namedGroup( 'token' ).literal( '**aabb**' ).end( ).any( ).space( ).or_( ).digit( False ).oneOrMore( ).end( 2 ).zeroOrMore( False ).backReference( 'token' ).EOL( ).compose( re.I )
    
echo_("Partial        : " + identifierSubRegex)
echo_("Composed       : " + outregex['pattern'].pattern)
echo_("Expected       : " + "^(?:[_a-z][_a-z0-9]*|(\\*\\*aabb\\*\\*).\\s|\\D+)*?\\1$")
echo_("Output         : " + pprint.pformat(outregex, 4))
echo_("===============================================================")
echo_()

echo_("Testing Regex.Analyzer")
echo_("===============================================================")

# test it
inregex = '/(?P<named_group>[abcde]+)fgh(?P=named_group)(?# a comment)/i'
anal = Regex.Analyzer( inregex )
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
echo_("===============================================================")
echo_("Regular Expression Syntax Tree              : ")
echo_(pprint.pformat(anal.tree(True), 4))
echo_("===============================================================")
echo_("Regular Expression (Named) Matched Groups   : ")
echo_(pprint.pformat(groups, 4))
echo_("===============================================================")
echo_("Regular Expression Peek Characters          : ")
echo_(pprint.pformat({'positive':list(peekChars['positive'].keys()),'negative':list(peekChars['negative'].keys())}, 4))
echo_("===============================================================")
echo_("Regular Expression Minimum / Maximum Length : ")
echo_(pprint.pformat({'minimum':minLen,'maximum':'unlimited' if -1 == maxLen else maxLen}, 4))
echo_("===============================================================")
echo_("Regular Expression Sample Match Strings     : ")
echo_(pprint.pformat(sampleStr, 4))
echo_("===============================================================")
