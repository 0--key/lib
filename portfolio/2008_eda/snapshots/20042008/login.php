<?php
session_start();
include("functions/Text.inc");
// Выложим все функции сюда:
/*function add_some_extra(&$string)
{
    $string .= 'and something extra.';
}
$str = 'This is a string, ';
add_some_extra($str);
echo $str;    // outputs 'This is a string, and something extra.'
function str_good($string, $lenght)
{
$string = substr($string, 0, $lenght);
$string = preg_replace("/[^\w\x7F-\xFF\s]/", " ", $string);
return $string;
}*/
// ****************************************** 
if(isset($_SESSION['views']))
    $_SESSION['views'] = $_SESSION['views']+ 1;
else
    $_SESSION['views'] = 1;
    
    // let's make insurance
    if($_POST['pseudo']!="" and $_POST['parol']!="")
    {
    $pseudo = $_POST['pseudo']; $parol = $_POST['parol'];
    $pseudo1 = htmlspecialchars($_POST['pseudo']); $parol1 = htmlspecialchars($_POST['parol']);
    $nick = str_good($pseudo1, 8);//substr($pseudo1, 0, 8);
    //$nick = preg_replace("/[^\w\x7F-\xFF\s]/", " ", $nick);
    $pass = str_good($parol1, 8);//substr($parol1, 0, 8);
    //$pass = preg_replace("/[^\w\x7F-\xFF\s]/", " ", $pass);
    echo $pseudo, '<br>', $pseudo1, '<br>', $parol, '<br>', 
    $parol1, '<br>', $nick, '<br>', $pass, '<br>';
    if($nick==$pseudo and $pass==$parol){
    echo 'Nick&pass correct <br>';
    $auth = 'correct';
    $_SESSION['auth'] = $auth;
    echo $auth, '<br>', '<br>';
    }
    else {echo "You'r wanna data? <br>"; $auth = 'danger';
    echo $auth, '<br>', '<br>';
    }
    // Let's make MySQL identification
    if($auth=='correct' and strlen($nick)>4 and
    strlen($pass)==6)
    {
    //The lengh of strings is good
    echo "Let's do MySQL querie! <br>";
    $link = mysql_run();
// Performing SQL query
$query = "SELECT pass FROM customers WHERE nick = '$nick' ";
mysql_cyr();
$result_cu = mysql_query($query) or die ('Query failed: ' . mysql_error());
$num_rows_cu = mysql_num_rows($result_cu);

// Performing SQL query
$query = "SELECT password FROM runners WHERE nick = '$nick' ";
mysql_cyr();
$result_ru = mysql_query($query) or die ('Query failed: ' . mysql_error());
$num_rows_ru = mysql_num_rows($result_ru);

echo 'runners=', $num_rows_ru, '<br>', 'customers=', $num_rows_cu, '<br>';
//Extract passwords for runner
if($num_rows_ru==1){
$pass1 = mysql_fetch_array($result_ru);
}
if($pass1[0]!=$pass) echo 'Wrong pass, mister runner! <br>';
else {
echo 'Authentification success! <br>';
// Это данные пользователя проверены, он зарегистрирован, как курьер
//Workspace&variables for runner
$query = "SELECT * FROM runners WHERE nick = '$nick' ";
mysql_cyr();
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
$runner = mysql_fetch_array($result); 
$_SESSION['nick'] = $nick;
$_SESSION['name'] = $runner[0];
if($runner[8]=='deny'){
echo $runner[0], '! <br> The service denyed <br> 
Please, contact whith supervisor on ICQ 309164009. <br>';
}
else {
//It's a real workspace:
echo '<form action="Arrive_in_store.php" method="post">
              <table class="text"
 style="text-align: center; width: 100%;" border="1" cellpadding="2"
 cellspacing="2">
                <tbody>
                  <tr>
                    <td>&nbsp; Input the name of store:<br>
&nbsp;<input maxlength="15" size="15" class="inputbox" name="store_name"><br>
                    </td>
                  </tr>
                </tbody>
              </table>
              <input src="images/okblue.gif" align="absmiddle" alt="Send It In!"
 align="center" height="20" type="image" width="30"> </form>';
 echo $_SESSION['name'];

}

if($num_rows_cu==1) {
$pass1 = mysql_fetch_array($result_cu);
//echo $pass1[0], '<br>';
//Workspace&variables for customer
$query = "SELECT * FROM customers WHERE nick = '$nick' ";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
$customer = mysql_fetch_array($result); 
$_SESSION['nick'] = $nick;
$_SESSION['name'] = $customer[3];
if($customer[14]=='deny'){
echo 'Dear ', $customer[3], '! <br> The service denyed <br> 
Please, contact whith supervisor on ICQ 309164009. <br>';
}
else {
//It's for customers:
}

// It's a pearl! 



}

}







mysql_close($link);
    }
    else echo "It's so short!";
    
    
    
    
    
    }
    
    
    
    
 else echo "You're not auth login&password!";      
?>