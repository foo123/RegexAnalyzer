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

$inregex = '/xyz([abc0-9]){2,3}/i';
$anal = new RegexAnalyzer($inregex);
$peekChars = $anal->peek( );
$minLen = $anal->minimum( );
$sampleStr = $anal->sample( 1, 5 );
for($i=0; $i<5; $i++)
    $sampleStr[$i] = array('sample'=>$sampleStr[$i],'match'=>preg_match($inregex, $sampleStr[$i], $m) ? 'yes' : 'no');
echo_("Input                                   : " . $inregex);
echo_("Regular Expression                      : " . $anal->re);
echo_("Regular Expression Flags                : " . implode(',',array_keys($anal->fl)));
echo_("=========================================");
echo_("Regular Expression Syntax Tree          : ");
echo_(print_r($anal->tree(true), true));
echo_("=========================================");
echo_("Regular Expression Peek Characters      : ");
echo_(print_r(array('positive'=>array_keys($peekChars['positive']),'negative'=>array_keys($peekChars['negative'])), true));
echo_("=========================================");
echo_("Regular Expression Minimum Length       : ");
echo_($minLen);
echo_("=========================================");
echo_("Regular Expression Sample Match Strings : ");
echo_(print_r($sampleStr, true));
echo_("=========================================");
