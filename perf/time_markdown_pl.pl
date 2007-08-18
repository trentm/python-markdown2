
use Markdown;

my @text_files = <$ARGV[0]/*.text>;
my $file, $content;
for $file (@text_files) {
    local(*INPUT, $/);
    open (INPUT, $file)     || die "can't open $file: $!";
    $content = <INPUT>;
    Markdown::Markdown($content);
}
