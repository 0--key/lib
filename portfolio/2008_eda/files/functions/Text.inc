<?php
function str_good($string, $lenght){
$string = substr($string, 0, $lenght);
$string = preg_replace("/[^\w\x7F-\xFF\s]/", " ", $string);
return $string;
}

function str_good_num($string, $lenght){
$string = substr($string, 0, $lenght);
$string = $string/100*100;//preg_replace("/[^\w\x7F-\xFF\sA-z]/", " ", $string);
//$string = ereg_replace("A-z", " ", $string);
return $string;
}

function mysql_run(){

    // Connecting, selecting database
$link = mysql_connect('localhost', 'edacomua_toxa', 'musiqpusiq')
    or die('Could not connect: ' . mysql_error());
//echo 'Connected successfully';
mysql_select_db('edacomua_meal_store') or die('Could not select database');

// Performing SQL query
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
return $link;
}


function mysql_cyr(){
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
}

function get_section_name($section_code){
if ($section_code == 1){
$section_name = 'Товары по специальным ценам';}
if ($section_code == 2){
$section_name = 'Алкогольные напитки';}
if ($section_code == 3){
$section_name = 'Сигареты и табак';}
if ($section_code == 4){
$section_name = 'Безалкагольные напитки';}
if ($section_code == 5){
$section_name = 'Чай, кофе, какао';}
if ($section_code == 6){
$section_name = 'Хлеб и хлебобулочные изделия';}
if ($section_code == 7){
$section_name = 'Бакалея';}
if ($section_code == 8){
$section_name = 'Мясо и мясопродукты';}
if ($section_code == 9){
$section_name = 'Рыба и морепродукты';}
if ($section_code == 10){
$section_name = 'Кондитерские изделия';}
if ($section_code == 11){
$section_name = 'Консервы';}
if ($section_code == 12){
$section_name = 'Молоко и молочные продукты';}
if ($section_code == 13){
$section_name = 'Мороженое и десерты замороженные';}
if ($section_code == 14){
$section_name = 'Овощи, фрукты, орехи';}
if ($section_code == 15){
$section_name = 'Готовые блюда и полуфабрикаты';}
if ($section_code == 16){
$section_name = 'Детские товары';}
if ($section_code == 17){
$section_name = 'Корма для животных';}
if ($section_code == 18){
$section_name = 'Журналы, газеты, книги';}
if ($section_code == 19){
$section_name = 'Средства гигиены, парфюмерия, косметика';}
if ($section_code == 20){
$section_name = 'Хозяйственные товары';}
if ($section_code == 21){
$section_name = 'Подарочные наборы, упаковка для подарков';}
if ($section_code == 22){
$section_name = 'Собственное производство';}
if ($section_code < 1 or $section_code > 22){
$section_name = 'wrong';}
return $section_name;}
//
// 	Сделаем всё для шифрования:
//	сначала - симметричное
//
function sym_encrypt_data($string){
    $key = "This is a very secret key";
    $iv = '#iq!&+teqxгцхйЪл';
    $crypttext = mcrypt_encrypt(MCRYPT_RIJNDAEL_128, $key, $string, MCRYPT_MODE_CFB, $iv);
    
    return $crypttext;

}

//
//
//	Затем - симметричное дешифрование:

function sym_decrypt_data($string){
    $key = "This is a very secret key";
    $iv = '#iq!&+teqxгцхйЪл';
    $decrypttext = mcrypt_decrypt(MCRYPT_RIJNDAEL_128, $key, $string, MCRYPT_MODE_CFB, $iv);
    
    return $decrypttext;
}

//
//	Теперь - сильное:
//
/*												Это для первого раза
*/
function encrypt_data_first($string){
    $iv_size = mcrypt_get_iv_size(MCRYPT_RIJNDAEL_128, MCRYPT_MODE_CFB);
    $iv = mcrypt_create_iv($iv_size, MCRYPT_RAND);
    $key = "Hi&xq){kle##dkj oq!<*sx=+";
    $crypttext = mcrypt_encrypt(MCRYPT_RIJNDAEL_128, $key, $string, MCRYPT_MODE_CFB, $iv);
    return array ($crypttext, $iv);

}

/*										Это для всех последующих, когда уже определён вектор инициализации
*/
function encrypt_data($string, $iv){
    $key = "Hi&xq){kle##dkj oq!<*sx=+";
    $crypttext = mcrypt_encrypt(MCRYPT_RIJNDAEL_128, $key, $string, MCRYPT_MODE_CFB, $iv);
    return $crypttext;

}

//
//	Теперь - дешифрование из сильного:
//

function decrypt_data($string, $iv){
    $key = "Hi&xq){kle##dkj oq!<*sx=+";
    $decrypttext = mcrypt_decrypt(MCRYPT_RIJNDAEL_128, $key, $string, MCRYPT_MODE_CFB, $iv);



    return $decrypttext;
}

function get_bg_color($priority){
switch ($priority) {
case 'not_valid':
    echo "#eea762";
    break;
case 'first':
    echo "#a7e5ae";
    break;
case 'low':
    echo "#89f095";
    break;
case 'high':
    echo "#67df75";
    break;
case 'deny':
    echo "#f26748";
    break;
}

}

/*											Функция для рассылки почтовых сообщений
*/
function mail_to($email, $name, $from, $subject, $body){

error_reporting(E_STRICT);

date_default_timezone_set('America/Toronto');

include("/home/edacomua/public_html/mailer/class.phpmailer.php");
//include("class.smtp.php"); // optional, gets called from within class.phpmailer.php if not already loaded

$mail             = new PHPMailer();

//$body             = $mail->"Hi,<br>This is the HTML BODY<br>";//le('contents.html');
//$body             = eregi_replace("[\]",'',$body);

$mail->IsSMTP();
$mail->SMTPAuth   = true;                  // enable SMTP authentication
$mail->SMTPSecure = "ssl";                 // sets the prefix to the servier
$mail->Host       = "smtp.gmail.com";      // sets GMAIL as the SMTP server
$mail->Port       = 465;                   // set the SMTP port for the GMAIL server

$mail->Username   = "systemeda@gmail.com";  // GMAIL username
$mail->Password   = "rtyeiopq";            // GMAIL password

//$mail->AddReplyTo("systemeda@gmail.com","");

//$mail->From       = "system@e-da.com.ua";
$mail->FromName   = $from;

$mail->Subject    = $subject;

$mail->Body       = $body;                      //HTML Body
//$mail->AltBody    = "To view the message, please use an HTML compatible email viewer!"; // optional, comment out and test
$mail->WordWrap   = 50; // set word wrap

//$mail->MsgHTML($body);

$mail->AddAddress($email, $name);

//$mail->AddAttachment("images/phpmailer.gif");             // attachment

$mail->IsHTML(true); // send as HTML

if(!$mail->Send()) {
  $message = "Mailer Error: " . $mail->ErrorInfo;
} else {
  $message = "Message sent!";
}
return $message;
}

?>
