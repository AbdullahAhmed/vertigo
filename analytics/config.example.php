<?php
// Copy to config.php during deployment. Never commit the real configuration.
return [
    'password_hash' => 'REPLACE_WITH_PASSWORD_HASH',
    'secret' => 'REPLACE_WITH_64_RANDOM_HEX_CHARACTERS',
    'origin' => 'https://vertigo.alphasquaredgames.com',
    // Must be outside every public web directory.
    'data_dir' => dirname(__DIR__, 3) . '/.vertigo-analytics',
];
