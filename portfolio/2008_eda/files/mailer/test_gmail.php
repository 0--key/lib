<?php

//error_reporting(E_ALL);
error_reporting(E_STRICT);

date_default_timezone_set('America/Toronto');

include("class.phpmailer.php");
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
$mail->FromName   = "Your dispatcher";

$mail->Subject    = "PHPMailer Test Subject via gmail";

$mail->Body       = "Hi,<br>This is the HTML BODY<br>И испробуем кириллицу!";                      //HTML Body
$mail->AltBody    = "To view the message, please use an HTML compatible email viewer!"; // optional, comment out and test
$mail->WordWrap   = 50; // set word wrap

//$mail->MsgHTML($body);

$mail->AddAddress("cucumber@oriontv.net", "Antony Kosinoff");

//$mail->AddAttachment("images/phpmailer.gif");             // attachment

$mail->IsHTML(true); // send as HTML

if(!$mail->Send()) {
  echo "Mailer Error: " . $mail->ErrorInfo;
} else {
  echo "Message sent!";
}

?>
