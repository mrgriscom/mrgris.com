<? header('Content-Type: text/json'); ?>
<?

$PREC = 1;

$raw = file_get_contents('/var/lib/webapp/drewtracker.json');
$pos = json_decode($raw, true);

$pos['lat'] = round($pos['lat'], $PREC);
$pos['lon'] = round($pos['lon'], $PREC);

?>
<?= json_encode($pos); ?>
