<?php

header("Content-type: text/vnd.wap.wml");  

header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");              
// expires in the past
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");   
// Last modified, right now
header("Cache-Control: no-cache, must-revalidate");              
// Prevent caching, HTTP/1.1
header("Pragma: no-cache");                                
// Prevent caching, HTTP/1.0

include("/home/edacomua/functions/Text.inc");

/*											Сделаем смену статуса курьера  												offline ---> ready:
*/
if($_SESSION['auth']=='correct' and $func=='get_ready')
{
	$link = mysql_run();
	$nick = $_SESSION['nick'];
	$query_to_runners = mysql_query("update runners set status='ready' where nick='$nick'") 
	or die ('Query to runners failed: ' . mysql_error());
	mysql_close($link);
}

print "<?xml version=\"1.0\" encoding=\"cp1251\"?>\n";  
print "<!DOCTYPE wml PUBLIC \"-//WAPFORUM//DTD WML 1.1//EN\""  
   . " \"http://www.wapforum.org/DTD/wml_1.1.xml\">\n"; 
print "<wml>\n";
// Line feed
$lf = chr(10);

if (empty($cmd) and empty($func)) { $cmd = "login"; }

switch ($cmd)
{

   case "auth";
	print "<card id=\"Search\">\n";
	$nick = $_POST['nick']; $password = $_POST['pass'];
         if (!empty($nick) and !empty($password) and strlen($nick)>5 and strlen($password)==6) 
      {
	// Open link to DB
	$link = mysql_run();
    
        $query = "select name, nick, password, e_mail, phone_no, iv, time from runners  where nick='$nick' and password='$password'";
        $result = mysql_query($query)
        or die("Query failed:$query");
        $num_rows = mysql_num_rows($result);
        if($num_rows==1) 
        	{
        	$line = mysql_fetch_array($result, MYSQL_ASSOC);
        	print "<p align=\"center\">\n";
        	print "Приветствую Вас, "; echo decrypt_data($line['name'], $line['iv']);
        	print "</p>\n";
        	$_SESSION['nick'] = $nick; $_SESSION['auth'] = 'success';
        	}
        else 
        	{
        	print "<p align=\"center\"><br />Authentification<br />failrue!</p>\n";
        	}
        mysql_close($link);	
        		
       		/*$iv = $line['iv'];
        	print "<p mode=\"wrap\">\n";
        	print "$line[nick]", "  ", decrypt_data($line['name'], $iv), "<br />\n";
        	print decrypt_data($line['phone_no'], $iv), "<br />
";
        	print decrypt_data($line['e_mail'], $iv), "<br />
";
        	$Date = date("M j, Y", strtotime($line['time']));
        	print "Record Updated:<br />$Date</p>";*/
        	//	print '<p mode="wrap">';
	}       		
      	else print "<p align=\"center\"><br />Authentification<br />failrue!</p>\n";
      //print '<p>', $_POST['nick'], $_POST['pass'], $_SESSION['auth'], '</p>';
        print "</card>\n";
        break;
      
      case "login";
   
      print "<card>\n";
      print "<p align=\"center\">Hello, welcome to our System.</p>\n"
      print "<p align=\"center\">Введите Ваш псевдоним:\n";
      print "<input name=\"nick\" maxlength=\"8\"/>\n";
      print "Введите Ваш пароль:\n";
      print "<input name=\"pass\" type=\"PASSWORD\" maxlength=\"6\"/><br/>\n";
      print "</p>";
      print "<anchor>\n";
      print "<go method=\"post\" href=\"?cmd=auth\">\n";
      print "<postfield name=\"nick\" value=\"$(nick)\"/>\n";
      print "<postfield name=\"pass\" value=\"$(pass)\"/>\n";
      print "</go>\n";
      print "Submit Data\n";
      print "</anchor>\n";
      print "</p>\n";
      print "</card>\n";
   break;
}

print "</wml>";



?>
