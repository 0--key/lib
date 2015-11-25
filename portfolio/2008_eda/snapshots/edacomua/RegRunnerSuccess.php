<?php
session_start();
$code = $_SESSION['code']; $code1 = htmlspecialchars($_POST['phonecode']);
$name = $_SESSION['name'];
$nick = $_SESSION['nick'];
$password = $_SESSION['password'];
$phonenum = $_SESSION['phonenum'];
$town = $_SESSION['town'];
$streettype = $_SESSION['streettype'];
$street = $_SESSION['street'];
$buildno = $_SESSION['buildno'];
$store_name = $_SESSION['store_name'];

     // Connecting, selecting database
     // print $nick;
$link = mysql_connect('localhost', 'root', 'hidden')
  or die('Could not connect: ' . mysql_error());
//echo 'Connected successfully';
mysql_select_db('edacomua_meal_store') or die('Could not select database');

// Performing SQL query
$query = "SELECT * FROM runners WHERE nick = '$nick' ";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());

// Printing results in HTML
$num_rows = mysql_num_rows($result);
if ($num_rows == 0) {
$query = "insert into runners values
('$name', '$nick', '$password', '$phonenum', '1', '1', 'offline', 'Антоша', 'user', '$town')";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die('Query failed: ' . mysql_error());
$query = "insert into stores values
('$nick', '$streettype', '$street', 'buildno', 'store_name')";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die('Query failed: ' . mysql_error());
mysql_close($link);
}
else mysql_close($link);
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <title>E-da.com.ua - продукты на дом</title>
  <link rel="SHORTCUT ICON" href="images/favicon.ico">
  <link href="css/styles.css" rel="stylesheet" type="text/css">
  <meta http-equiv="Content-Type"
 content="text/html;charset=windows-1251">
  <meta name="description" content="Завершение регистрации">
  <meta name="keywords" content="e-da.com.ua. Доставка продуктов на дом ">
</head>
<body
 onload="if( self.parent.frames.length != 0 ) self.parent.location = document.location"
 bottommargin="0" topmargin="0" rightmargin="0" leftmargin="0"
 style="background-color: rgb(255, 255, 255); color: rgb(0, 0, 0);">
<small> </small>
<table class="head_grad"
 style="width: 100%; height: 4%; background-color: rgb(255, 204, 153); text-align: left; margin-left: auto; margin-right: auto; font-family: Helvetica,Arial,sans-serif;"
 border="3" cellpadding="0" cellspacing="0">
  <tbody>
    <tr align="center">
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(228, 136, 37);"><small><span
 class="menu_link"><br></span></small></td>
      <td style="background-color: rgb(250, 134, 7);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(228, 136, 37);"><small><span
 class="menu_link"><br></span></small></td>
      <td style="background-color: rgb(223, 143, 56);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(214, 151, 83);"><small><span
 class="menu_link"><br></span></small></td>
      <td style="background-color: rgb(214, 151, 83);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(205, 155, 102);"><small><span
 class="menu_link"><a href="apology.html">Помощь</a></span></small></td>
      <td style="background-color: rgb(205, 155, 102);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(212, 170, 128);"><small><span
 class="menu_link"><a href="AboutUs.html">О нас<br>
      </a></span></small></td>
      <td style="background-color: rgb(212, 170, 128);"><small>&nbsp;</small></td>
      <td class="menu_razdel" width="15%"><small><span class="menu_link"><a
 href="apology.html">Сотрудничество</a></span></small></td>
    </tr>
  </tbody>
</table>
<small> </small><small> </small><small> </small><small> </small><small>
</small><small> </small><small> </small>
<table
 style="width: 100%; height: 40px; font-family: Helvetica,Arial,sans-serif;"
 border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><small> <br>
      </small></td>
      <td class="small_white_text"
 style="text-align: center; background-color: rgb(226, 177, 55); color: rgb(0, 102, 0);"><big>E-da.com.ua
- заказ и доставка
продуктов на дом, в офис, на дачу</big><small><br>
      </small></td>
      <td class="text"
 style="vertical-align: bottom; text-align: center; background-color: rgb(137, 196, 69); color: rgb(153, 51, 0); width: 40%;"><small><span
 style=""><span style="color: rgb(0, 0, 0);"></span><span
 style="color: rgb(0, 0, 0);"></span> </span><br>
      <br>
      </small></td>
    </tr>
  </tbody>
</table>
<table
 style="font-family: Helvetica,Arial,sans-serif; background-color: rgb(220, 220, 122); width: 100%;"
 border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td style="padding: 0px 0px 0px 22px;" valign="top" width="175"><!-- main menu table --><small><br>
      </small>
      <div style="border: 1px solid rgb(232, 219, 63);" align="center"><small><a
 href="apology.html"><b>Вакансия <br>
для региональных представителей</b></a><br>
&nbsp;</small></div>
      <small> <br>
      <br>
      <span style="color: rgb(153, 51, 0);">Наши</span><br
 style="color: rgb(153, 51, 0);">
      <span style="color: rgb(153, 51, 0);">партнёры:<br>
      <br style="color: rgb(153, 51, 0);">
      </span>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 39px; height: 36px;"
 src="images/Ub1small.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a><br>
            </a></span></td>
          </tr>
        </tbody>
      </table>
      <br>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 45px; height: 36px;"
 src="images/Ub2small.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a><br>
            </a></span></td>
          </tr>
        </tbody>
      </table>
      <br>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/Ubdark.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a><br>
            </a></span></td>
          </tr>
        </tbody>
      </table>
      <br>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 39px; height: 36px;"
 src="images/UbTogether.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a><br>
            </a></span></td>
          </tr>
        </tbody>
      </table>
      <br>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 37px; height: 36px;"
 src="images/UbTogether1.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a><br>
            </a></span></td>
          </tr>
        </tbody>
      </table>
      <br>
      </small></td>
      <td style="padding: 0px 22px;" class="text" valign="top"><small> </small>
      <small> </small><small> </small><small> </small><small> </small><small>
      </small> <small> </small>
      <table style="width: 100%;">
        <tbody>
          <tr>
            <th style="background-color: rgb(210, 196, 60);"><small> </small>
            <small> </small><?php
            if ($code1 == $code and $num_rows == 0){
            echo $name; echo ',';
            echo 'вы зарегистрированы в нашем
магазине&nbsp;&nbsp;';}
else echo 'Извините, Вам придётся повторить процедуру
регистрации';
?> <br>
            </th>
          </tr>
        </tbody>
      </table>
      <div style="text-align: left;"><br>
      <ul>
      <?php if ($code1 == $code){ echo '<li>Ваше имя в нашей системе: '; echo $name;
      echo '</li>
        <li>Ваш псевдоним для входа: '; echo $nick;
      echo '</li>
        <li>Ваш пароль для входа: '; echo $password;
      echo '</li>'; 
      //echo '<li>Номер Вашего мобильного: '; echo $phonenum + 38E+10;
      //echo '</li>';
                //echo $code; echo $code1;

        echo '</ul>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; Магазин, из которого 
Вы будете осуществлять доставку: <br>
      <ul>
        <li>Город '; echo $town;
      echo '<br>
        </li>
        <li>'; echo $streettype; echo ' '; echo $street;
      echo '</li>
        <li>Дом №'; echo $buildno;
      echo '</li>';
              echo '<li>Название магазина '; echo $store_name;
      echo '</li>
      </ul>
      <div style="text-align: center;">&nbsp;<br>
      <div style="text-align: left;">
      <div style="text-align: center;"><br>&nbsp;&nbsp;&nbsp; Обязательно
запомните, а лучше запишите Ваш пароль и псевдоним<big
 style="color: rgb(255, 0, 0);"><big>!</big></big><br><big
 style="color: rgb(255, 0, 0);"><big>Внимание!<br>Каждый, знающий ваш псевдо
ним и пароль для входа в нашу систему может осуществлять все манипуляции от Вашего
  имени.</big></big><br> Это хорошо с одной стороны:
 Вы можете поручить делать некоторые операции Вашим близким, но с другой стороны, Вам не
  следует разглашать эти данные посторонним людям. Теперь, при каждом Вашем входе
 на наш сайт (теперь это и Ваше рабочее место), вам следует ввести Ваши псевдоним
 и пароль сотрудника в окошке для входа в левом верхнем углу <br><a href="index.html"><big
 style="color: rgb(102, 0, 204);">
  первой страницы</big></a>. <br>&nbsp;&nbsp;&nbsp;
  Если вы хотите пользоваться услугами нашего магазина в качестве клиента, вам следует
  зарегистрироваться и в этом качестве.<br> 
      &nbsp;&nbsp;&nbsp; В дальнейшем, при возникновении каких бы то ни было
изменений (изменился номер мобильного; вы переехали, и теперь у Вас
другой адрес и т.п.) - убедительная просьба: во избежание обидных
недоразумений пройдите процедуру регистрации заново указав Ваши
данные.<br><a href="index.html"><big
 style="color: rgb(102, 0, 204);"><big>
  Добро пожаловать!</big></big></a> </div>';}
else echo '
      <div style="text-align: center;">
      <br>
      <br>
      <br>
      <br>
      <br>
      <div>
      <big style="color: rgb(204, 0, 0);">Вы ввели неправильный пароль<big
 style="color: rgb(51, 51, 255);"><big>!</big></big><br>
Вам отказано в регистрации.<br>
Если хотите, можете повторить процедуру <a href="RegNewRunner.php">регистрации</a>
сначала.<br>
Постарайтесь быть предельно внимательным<big
 style="color: rgb(51, 204, 255);"><big>!</big></big></big><br>
            </div>';
                        session_destroy();
            ?>
      </td>
    </tr>
  </tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tbody>
    <tr>
      <td class="tovar_m text"><small><br>
      <br>
      </small>
      <table style="background-color: rgb(51, 155, 155); width: 100%;"
 class="text" border="0" cellpadding="0" cellspacing="0">
        <tbody>
          <tr>
            <td style="text-align: center;"><small> e-mail: <a
 href="mailto:info@e-da.com.ua">info@e-da.com.ua</a><br>
200<span style="font-weight: bold;">7</span>-2008 © e-da.com.ua Украина
            </small></td>
            <td> <small> </small><br>
            </td>
          </tr>
        </tbody>
      </table>
      <small> </small></td>
    </tr>
  </tbody>
</table>
<small> <br>
<br>
</small>
</body>
</html>
