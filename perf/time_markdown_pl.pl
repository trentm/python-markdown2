
use Markdown;

my @text_files = <$ARGV[0]/*.text>;
my $file, $content;
$| = 1;
for $file (@text_files) {
    local(*INPUT, $/);
    open (INPUT, $file)     || die "can't open $file: $!";
    $content = <INPUT>;
    Markdown::Markdown($content);
    if ($ARGV[1] ne "mute") {
        print ".";
    }
}
