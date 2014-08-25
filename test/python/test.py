#
#
# use as: node test.js "your_regex_here" > output.txt

function echo_($s="")
{
    echo $s . PHP_EOL;
}

echo_("Testing Composer");
echo_("================");

include('../../src/php/regexcomposer.php');

$identifierSubRegex = new RegExComposer();
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

$outregex = new RegExComposer();
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

echo_("Testing Analyzer");
echo_("================");

include('../../src/php/regexanalyzer.php');

$inregex = '/^(?:[^\\u0000-\\u1234a-zA-Z\\d\\-\\.\\*\\+\\?\\^\\$\\{\\}\\(\\)\\|\\[\\]\\/\\\\]+)|abcdef\\u1234{1,}/gmi';
$anal = new RegExAnalyzer($inregex);

// test it
$anal->analyze();

echo_("Input: " . $inregex);
echo_();
echo_("Regular Expression: " . $anal->regex);
echo_();
echo_("Regular Expression Flags: ");
echo_(print_r($anal->flags, true));
echo_();
echo_("Regular Expression Parts: ");
echo_(print_r($anal->parts, true));
echo_("================");
echo_();
