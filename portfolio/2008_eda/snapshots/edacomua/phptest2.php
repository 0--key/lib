<?php
    $algorithms = mcrypt_list_algorithms("/usr/local/lib/libmcrypt");

    foreach ($algorithms as $cipher) {
        echo "$cipher<br />\n";
    }
?> 
