<?php
//
// use as: php -f test.php "your_regex_here" > output.txt

function echo_($s="")
{
    echo $s . PHP_EOL;
}

include('../../src/php/RegexComposer.php');

echo_("Testing Composer.VERSION = " . RegexComposer::VERSION);
echo_("================");

$identifierSubRegex = new RegexComposer();
$identifierSubRegex = $identifierSubRegex                
                ->characterGroup()
                    ->characters('_')
                    ->range('a', 'z')
                ->end()
                
                ->characterGroup()
                    ->characters('_')
                    ->range('a', 'z')
                    ->range('0', '9')
                ->end()
                
                ->zeroOrMore()
            
                ->partial();

$outregex = new RegexComposer();
$outregex = $outregex                    
                    ->startOfInput()
                    
                    ->either()
                        
                        ->sub($identifierSubRegex)
                        
                        ->match('**aabb**')
                        
                        ->any()
                        
                        ->space()
                        
                        ->digit(false)->oneOrMore()
                    
                    ->end()
                    
                    ->zeroOrMore(false)
                    
                    ->endOfInput()
                    
                    ->compose('i');
    
echo_("Partial: " . $identifierSubRegex);
echo_("Composed: " . $outregex);
echo_("Expected: " . "/^([_a-z][_a-z0-9]*|\\*\\*aabb\\*\\*|.|\\s|\\D+)*?$/i");
echo_("================");
echo_();

include('../../src/php/RegexAnalyzer.php');

echo_("Testing Analyzer.VERSION = " . RegexAnalyzer::VERSION);
echo_("=========================================");

$inregex = '/(?P<named_group>[abcde]+)fgh(?P=named_group)(?# a comment)/i';
$anal = new RegexAnalyzer($inregex);
$peekChars = $anal->peek( );
$minLen = $anal->minimum( );
$maxLen = $anal->maximum( );
$regexp = $anal->compile( array('i'=>!empty($anal->fl['i'])?1:0,'u'=>1) );
$groups = $anal->groups();
$sampleStr = $anal->sample( 1, 5 );
for($i=0; $i<5; $i++)
{
    $succ = preg_match($regexp, $sampleStr[$i], $m);
    $sampleStr[$i] = array('sample'=>$sampleStr[$i],'match'=>$succ ? 'yes' : 'no', 'groups'=>array());
    if ( $succ )
    {
        foreach($groups as $group=>$index)
            $sampleStr[$i]['groups'][$group] = isset($m[$index]) ? $m[$index] : null;
    }
}
echo_("Input                                       : " . $inregex);
echo_("Regular Expression                          : " . $anal->input());
echo_("Regular Expression Flags                    : " . implode(',',array_keys($anal->fl)));
echo_("Reconstructed Regular Expression            : " . $anal->source());
echo_("=============================================");
echo_("Regular Expression Syntax Tree              : ");
echo_(print_r($anal->tree(true), true));
echo_("=============================================");
echo_("Regular Expression (Named) Matched Groups   : ");
echo_(print_r($groups, true));
echo_("=============================================");
echo_("Regular Expression Peek Characters          : ");
echo_(print_r(array('positive'=>array_keys($peekChars['positive']),'negative'=>array_keys($peekChars['negative'])), true));
echo_("=============================================");
echo_("Regular Expression Minimum / Maximum Length : ");
echo_(print_r(array('minimum'=>$minLen,'maximum'=>-1===$maxLen?'unlimited':$maxLen), true));
echo_("=============================================");
echo_("Regular Expression Sample Match Strings     : ");
echo_(print_r($sampleStr, true));
echo_("=============================================");
