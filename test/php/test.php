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
echo_("================");

$inregex = '/xyz([abc0-9]){2,3}/i';
$anal = new RegexAnalyzer($inregex);
$peekChars = $anal->peek( );
$sampleStr = $anal->sample( );

echo_("Input: " . $inregex);
echo_();
echo_("Regular Expression: " . $anal->_regex);
echo_();
echo_("Regular Expression Flags: ");
echo_(print_r($anal->_flags, true));
echo_();
echo_("Regular Expression Parts: ");
echo_(print_r($anal->_parts, true));
echo_();
echo_("Regular Expression Peek Characters: ");
echo_(print_r($peekChars, true));
echo_();
echo_("Regular Expression Sample Match String: ");
echo_($sampleStr . ' -> ' . (preg_match($inregex, $sampleStr, $m) ? 'Matched' : 'NOT Matched'));
echo_("================");
echo_();
