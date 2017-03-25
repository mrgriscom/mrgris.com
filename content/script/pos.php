<?php header('Content-Type: text/json'); ?>
<?php

$PREC = 1;

$raw = file_get_contents('/var/lib/webapp/drewtracker.json');
$pos = json_decode($raw, true);

$pos['lat'] = round($pos['lat'], $PREC);
$pos['lon'] = round($pos['lon'], $PREC);

?>
<?= json_encode($pos); ?>
