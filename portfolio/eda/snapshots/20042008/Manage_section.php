<?php
session_start();
include("functions/Text.inc");
$section_code = (int)htmlspecialchars($_GET['section']);
if ($section_code>=1 or $section_code<=22){
$nick = $_SESSION['nick'];
$name = $_SESSION['name'];
$town =$_SESSION['town'];
$store_name = $_SESSION['store_name'];
$section_name = get_section_name($section_code);}
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <title>E-da.com.ua - продукты на дом</title>
  <link rel="SHORTCUT ICON" href="images/favicon.ico">
  <link href="css/styles.css" rel="stylesheet" type="text/css">
  <meta http-equiv="Content-Type"
 content="text/html;charset=windows-1251">
  <meta name="description" content="Управление содержимым отдела">
  <meta name="keywords" content="О e-da.com.ua. Доставка по Украине">
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
 class="menu_link"></span></small><br>
      </td>
      <td style="background-color: rgb(250, 134, 7);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(228, 136, 37);"><small><span
 class="menu_link"><a href="apology.html">Условия<br>
      </a></span></small></td>
      <td style="background-color: rgb(223, 143, 56);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(214, 151, 83);"><small><span
 class="menu_link"><a href="apology.html">Оплата</a></span></small></td>
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
      </small> <small> <br>
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
            <small> </small>
            <?php
            if ($name!=""){ 
            echo 'Уважаемый(ая), ', $name,
           '!<br>
Вы находитесь в магазине ', $store_name, ',<br>', $town,
',<br>
в отделе "', $section_name,
'"';}
else echo '<br><br><br><br><br>Пройдите процедуру аутентификации <br><a href="index.php">на главной странице.</a>';
?><br>
            </th>
          </tr>
        </tbody>
      </table>
      <div style="text-align: center;"><br>
Тут вся инфа о товарах в этом отделе<br>

<?php
if($name!="" and $section_name!='wrong'){
$link = mysql_run();
$query = "SELECT id, meal_name FROM meal_global WHERE meal_type='$section_code'";
$result = mysql_query("SELECT id, meal_name, manufacturer FROM meal_global 
where author = '$nick' and
meal_type = '$section_code' ");
 //echo $section_code;

// Printing results in HTML
//mysql_cyr();
/*echo "<br> <br>This is output table of meal_global <br>","<table>\n";
while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
    echo "\t<tr>\n";
    foreach ($line as $col_value) {
        echo "\t\t<td>$col_value</td>\n";
    }
    //echo "\t\t<td>$line[id]</td>\n";
    
    $query2 = mysql_query("select allocation, price_UH, modify_time, author_nick from meal_local 
    where author_nick='$nick' and id='$line[id]' and store_name='$store_name'");
    //$result1 = mysql_query($query);
    $num_rows_in_store_autority = mysql_num_rows($query2);
    
    $row1 = mysql_fetch_row($query2);
    if($num_rows_in_store_autority==1){
    
    echo "\t\t<td>$row1[0]\t$row1[1]\t$row1[2]\t$line[id]\t$row1[3]\t$num_rows_in_store_autority</td>\n";
    echo "\t";}
    else echo "</tr>\n";
}*/
//echo "</table>\n";

// Free resultset
mysql_cyr();
mysql_free_result($result);


// Closing connection

$_SESSION['section_code'] = $section_code;
$_SESSION['section_name'] = $section_name;}    
    ?>
          <br>
      <br>
      <br>
      <br>
      <?php
      if ($name!="" and $section_name!='wrong'){ 
      echo '<form action="Manage_list.php" method="post">
<table
style="text-align: left; width: 100%; margin-left: auto; margin-right: auto;"
class="text" cellpadding="2" cellspacing="2">
<tbody>
<tr>
<td style="text-align: center;">Id<br>
</td>
<td style="text-align: center;">Название<br>
</td>
<td style="vertical-align: top;">Производитель<br>
</td>
<td style="vertical-align: top;">Ёмкость <br>
упаковки<br>
</td>
<td style="vertical-align: top;">Вес, брутто<br>
(с упаковкой)</td>
<td style="vertical-align: top;">Объём<br>
(тр.)<br>
</td>
<td style="text-align: center;">Регистратор<br>
</td>
<td style="vertical-align: top;">Цена в магазине<br>
<div style="text-align: center;">', $store_name, '<br>
</div>
</td>
<td style="vertical-align: top;">
<div style="text-align: center;">Место<br>
</div>
<div style="text-align: center;">расположения<br>
</div>
</td>
<td style="vertical-align: top;">Есть?<br>
</td>
<td style="vertical-align: top;">Описание:<br>
</td>
</tr>';
//Шапка прошла, теперь делаем построчный вывод
/*******************************************/
//echo '<tr>';
//$query = "SELECT id, meal_name, FROM meal_global WHERE meal_type='$section_code'";
$result = mysql_query("SELECT id, meal_name, manufacturer, capacity, weight_brutto_kg, 
size_L, author FROM meal_global 
where meal_type = '$section_code' order by manufacturer ");
while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
$man_new = $line['manufacturer'];
if($_SESSION['man']==$man_new){

$man_status = 'old'; $col = '153, 150, 255';
}
else {
$man_status = 'new'; $col = '153, 255, 255';
}
$_SESSION['man'] = $man_new;
    echo '<tr>';
    foreach ($line as $col_value) {
            echo "<td
style=\"text-align: center; background-color: rgb($col);\">$col_value <br>
</td>";
    }
    $query2 = mysql_query("select price_UH, allocation, presence, author_nick from meal_local 
    where id='$line[id]' and store_name='$store_name' and town='$town'");
    //$result1 = mysql_query($query);
    //$num_rows_in_store_autority = mysql_num_rows($query2);
    
    $row1 = mysql_fetch_row($query2);
    //if($num_rows_in_store_autority==1){
    
                echo "<td
style=\"text-align: center; background-color: rgb($col);\">";
if($row1[3]==$nick){
//Output form:
//$data = array("cockie", "muckie");
//$_SESSION['data'] = $data;
//$prices[old][1234567891011] = 1.2;
//$_SESSION['prices'] = $prices;
echo '<input maxlength="6" size="6" class="inputbox" 
name="price', $line['id'], '" value="', $row1[0], '">';
$id_old[] = $line['id'];
$prices_old[] = $row1[0];
}
else echo "$row1[0]<br>
</td>";
echo "<td
style=\"text-align: center; background-color: rgb($col);\">";
if($row1[3]==$nick){
//Output form:
echo '<input maxlength="6" size="6" class="inputbox" 
name="allocation', $line['id'], '" value="', $row1[1], '">';
$allocation_old[] = $row1[1];
}
else echo "$row1[1]<br>
</td>";
echo "<td
style=\"text-align: center; background-color: rgb($col);\">";
if($row1[3]==$nick){
//Output form:
echo '<input maxlength="6" size="6" class="inputbox" 
name="presence', $line['id'], '" value="', $row1[2], '">';
$presence_old[] = $row1[2];
}
else echo "$row1[2]<br>
</td>";
echo '<td
style="vertical-align: top; background-color: rgb($col);">'; 
if($line[author]==$nick) {
echo '<a href="Redact_id_features.php?id=', $line[id], '">Редактировать</a>';}
echo "<br> $price </td>";
    //echo "\t\t<td>$row1[0]\t$row1[1]\t$row1[2]\t$line[id]\t$row1[3]\t$num_rows_in_store_autority</td>\n";
    //echo "\t";
    //}
    //else echo "</tr>\n";
   // echo "</tr>\n";
}
echo "</table>\n";
/*echo '<td
style="vertical-align: top; background-color: rgb(153, 255, 255);">1234567891011<br>
</td>
<td
style="vertical-align: top; background-color: rgb(153, 255, 255); text-align: center;">Кетчуп
"Балтимор"</td>
<td
style="text-align: center; background-color: rgb(153, 255, 255);">Балтимор<br>
</td>
<td
style="text-align: center; background-color: rgb(153, 255, 255);">0.3<br>
</td>
<td
style="text-align: center; background-color: rgb(153, 255, 255);">0.35<br>
</td>
<td
style="text-align: center; background-color: rgb(153, 255, 255);">0.4<br>
</td>
<td
style="text-align: center; background-color: rgb(153, 255, 255);">4.4<br>
</td>
<td
style="text-align: center; background-color: rgb(153, 255, 255);">ASDFG<br>
</td>
<td
style="text-align: center; background-color: rgb(153, 255, 255);">да<br>
</td>
<td
style="vertical-align: top; background-color: rgb(153, 255, 255);">'; 
if($author=='y') echo '<a href="Redact_id_features.php">Редактировать</a>';
echo '<br>
</td>
</tr>
<tr>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);">1234567891012<br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 204, 204);"><br>
</td>
</tr>
<tr>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);">1234567891013<br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(102, 255, 153);"><br>
</td>
</tr>
<tr>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);">1234567891014<br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(51, 255, 51);"><br>
</td>
</tr>
<tr>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);">1234567891015<br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 204, 255);"><br>
</td>
</tr>
<tr>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);">1234567891016<br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
<td
style="vertical-align: top; background-color: rgb(255, 153, 255);"><br>
</td>
</tr>
*/
$_SESSION['oldprices'] = $prices_old;
$_SESSION['oldallocation'] = $allocation_old;
$_SESSION['oldpresence'] = $presence_old;
$_SESSION['oldid'] = $id_old;
echo '
<input src="images/okblue.gif" alt="Send It In!" 
align="absmiddle" height="40" type="image" width="60"> </form>
<br><br>
', //</tbody>
/*</table>
<br>

      */'<table style="text-align: left; width: 100%;" border="1"
 cellpadding="2" cellspacing="2">
        <tbody>
          <tr>
            <td style="vertical-align: middle; text-align: center;">Наполни
свой магазин товаром, следи за ним
            <form action="Input_id.php" method="post">
              <table class="text"
 style="text-align: center; width: 100%;" border="1" cellpadding="2"
 cellspacing="2">
                <tbody>
                  <tr>
                    <td>&nbsp;Введите цифровой штрих-код товара, который
ты хотел бы добавить в этот отдел:<br>
&nbsp;<input maxlength="13" size="13" class="inputbox" name="meal_id"><br>
                    </td>
                  </tr>
                </tbody>
              </table>
              <input src="images/okblue.gif" alt="Send It In!"
 align="absmiddle" height="20" type="image" width="30"> </form>
            </td>
          </tr>
        </tbody>
      </table>';}
            else {
      echo '<br><br>Вы пытаетесь проникнуть в отдел, которого ещё нет
      в этом магазине! <br><br> Нехорошо!!!';}
      mysql_close($link);
      ?>
      <small> </small></div>
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
      <table class="text" border="0" cellpadding="0" cellspacing="0"
 width="100%">
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
