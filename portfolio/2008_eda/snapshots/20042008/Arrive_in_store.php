<?php
session_start();
include("functions/Text.inc");  
         //Щас сделаем условие если это реверс
        //после ввода всех данных в формы meal
        if(strlen($_SESSION['id'])==13 and
    htmlspecialchars($_POST['price'])!="" and   
    isset($_SESSION['store_name']) and
    isset($_SESSION['nick']) and
    isset($_SESSION['name']) and
    isset($_SESSION['town']) and
    isset($_SESSION['section_code'])){
    
    $id = $_SESSION['id'];
    $store_name = $_SESSION['store_name'];
    $name = $_SESSION['name'];
    $nick = $_SESSION['nick'];
    $town = $_SESSION['town'];
    $section_code = $_SESSION['section_code'];
    $section_name = $_SESSION['section_name'];
    $num_rows_global = $_SESSION['num_rows_global'];
    $num_rows_local = $_SESSION['num_rows_local'];
    $meal_name = htmlspecialchars($_POST['meal_name']);
    $meal_name = str_good($meal_name, 40);
    $manufacturer = htmlspecialchars($_POST['manufacturer']);
    $features = htmlspecialchars($_POST['features']);
    $weight = htmlspecialchars($_POST['weight']);
    $weight = str_replace(",", ".", $weight);
    $size = htmlspecialchars($_POST['size']);
    $size = str_replace(",", ".", $size);
    $price = htmlspecialchars($_POST['price']);
    $price = str_replace(",", ".", $price);
    $allocation = htmlspecialchars($_POST['allocation']);
    $capacity = htmlspecialchars($_POST['capacity']);
    $capacity = str_replace(",", ".", $capacity);
        
    /* ща вот условие для предотвращения дублирования
    инфы о товарах*/
  
//$_SESSION['num_rows_global'] = 1;
    $link = mysql_run();
 if ($num_rows_global==0){
// Performing SQL query
$timestamp = date("Y-m-d H:i:s");
$query = "insert into meal_global  values
('$id', '$section_code', '$meal_name', '$manufacturer', '$features',
'$capacity', '$weight',
'$size', '$nick', '$timestamp', '0001')";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
$message1 = "Данные о товаре с идентификатором $id, <br> занесены в базу данных <br>";
}
 if ($num_rows_local==0){ 
// и для meal_local тоже:
$timestamp = date("Y-m-d H:i:s");
$query = "insert into meal_local values
('$id', '$price', '$town', '$store_name', '$allocation', 'yes',
'$nick', '$timestamp')";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
$message2 = "Данные занесены в магазин $store_name <br>";
}
//А это на случай редактирования уже существующей записи:
if ($num_rows_local==1 and $price>0 and $allocation!=""){
$timestamp = date("Y-m-d H:i:s");
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query("UPDATE meal_local SET price_UH='$price', 
allocation='$allocation' WHERE store_name='$store_name' and
id='$id'") 
or die(mysql_error());
$message3 = "Сведения о товаре с идентификатором  $id <br>обновлены в магазине $store_name <br>";
}
mysql_close($link);
    
    }
    
    if(htmlspecialchars($_POST['store_name'])!="") {
        $nick = $_SESSION['nick'];
    $name = $_SESSION['name'];
    //$town = $_SESSION['town'];
    //$name = $_SESSION['name'];
    $store_name = htmlspecialchars($_POST['store_name']);
    $_SESSION['store_name'] = $store_name;}
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <title>E-da.com.ua - продукты на дом</title>
  <link rel="SHORTCUT ICON" href="images/favicon.ico">
  <link href="css/styles.css" rel="stylesheet" type="text/css">
  <meta http-equiv="Content-Type"
 content="text/html;charset=windows-1251">
  <meta name="description" content="Выбирайте!">
  <meta name="keywords" content="Заказ и доставка продуктов на дом">
</head>
<body style="background-color: rgb(255, 255, 255); color: rgb(0, 0, 0);">
<table class="head_grad"
 style="width: 100%; height: 4%; background-color: rgb(255, 204, 153); text-align: left; margin-left: auto; margin-right: auto; font-family: Helvetica,Arial,sans-serif;"
 border="3" cellpadding="0" cellspacing="0">
  <tbody>
    <tr align="center">
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(250, 134, 7);"><small><span
 class="menu_link"><span
 style="color: rgb(255, 255, 255); background-color: rgb(89, 122, 67); font-size: 12px;"><br>
      <br>
      </span></span></small></td>
      <td style="background-color: rgb(250, 134, 7);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(228, 136, 37);"><small><span
 class="menu_link"><a href="Terms.html">Условия<br>
      </a></span></small></td>
      <td style="background-color: rgb(223, 143, 56);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(214, 151, 83);"><small><span
 class="menu_link"><a href="Payment.html">Оплата</a></span></small></td>
      <td style="background-color: rgb(214, 151, 83);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(205, 155, 102);"><small><span
 class="menu_link"><a href="Help.html">Помощь</a></span></small></td>
      <td style="background-color: rgb(205, 155, 102);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(212, 170, 128);"><small><span
 class="menu_link"><a href="AboutUs.html">О нас<br>
      </a></span></small></td>
      <td style="background-color: rgb(212, 170, 128);"><small>&nbsp;</small></td>
      <td class="menu_razdel" width="15%"><small><span class="menu_link"><a
 href="Partnership.html">Сотрудничество</a></span></small></td>
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
      <td
 style="text-align: center; background-color: rgb(226, 177, 55); color: rgb(255, 255, 51);"><big
 style="color: rgb(153, 0, 0);">E-da.com.ua - заказ и доставка
продуктов на дом, в офис, на дачу</big><small><br>
      </small></td>
      <td class="text"
 style="vertical-align: bottom; text-align: center; background-color: rgb(137, 196, 69); color: rgb(153, 51, 0);"><small><span
 style=""><span style="color: rgb(0, 0, 0);"></span><span
 style="color: rgb(0, 0, 0);"></span> </span><br>
      <br>
      </small></td>
    </tr>
  </tbody>
</table>
<!-- the body of the page begins -->
<small> </small><small> </small><small> </small><small> </small>
<table
 style="font-family: Helvetica,Arial,sans-serif; background-color: rgb(220, 220, 122); width: 100%;"
 border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td
 style="padding: 0px 0px 0px 22px; vertical-align: top; width: 20%;"><!-- main menu table --><small><br>
      </small> <small> <span style="color: rgb(153, 51, 0);">Наши</span><br
 style="color: rgb(153, 51, 0);">
      <span style="color: rgb(153, 51, 0);">партнёры:<br>
      <br style="color: rgb(153, 51, 0);">
      </span> </small>
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
      </td>
      <td style="padding: 0px 22px;" class="text" valign="top"><small> </small>
      <small> </small><small> </small><small> </small><small> </small>
      <small> </small>
      <table style="width: 100%;">
        <small> </small><tbody>
          <small> </small><tr>
            <small> </small><th
 style="background-color: rgb(51, 204, 0);"> <small> 
 <?php
 if($nick!=""){
 $link = mysql_run();

// Performing SQL query
$query = "SELECT * FROM runners WHERE nick = '$nick' ";
mysql_cyr();
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
$row_runner = mysql_fetch_array($result);
$town_runner = $row_runner[9];
$_SESSION['town'] = $town_runner;
//Извлекаем и город из таблицы stores
$query = "SELECT * FROM stores WHERE town = '$town_runner' and store_name = '$store_name'";
mysql_cyr();
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
$num_rows = mysql_num_rows($result);
mysql_close($link);
if ($num_rows!=0){
 if ($name!=""){
 echo $name, ', - заполняйте
и редактируйте<br>товары в магазине<br><big style="color: rgb(204, 0, 0);"><big>', $store_name, '<br>', $town_runner, '</big></big>';}}
if($name==""){
echo 'Пройдите процедуру аутентификации <br><a href="index.php">на главной странице.</a>';}
if($num_rows==0){
echo  $name,'!<br>Магазин с названием ', $store_name, '<br>', $id,
'<br>не зарегистрирован в городе ', $town_runner, '<br> следует сначала
зарегистрировать магазин!';}}
?></small> <big><br>
            </big></th>
            <small> </small></tr>
          <small> </small>
        </tbody><small> </small>
      </table>
      <small> </small> <small> </small><small> </small><small> </small><small>
      </small><small> </small> <small> </small>
      <table style="background-color: rgb(220, 220, 122); width: 100%;"
 class="text" border="0" cellpadding="10" cellspacing="0">
        <tbody>
          <tr>
            <td style="color: rgb(102, 102, 0); width: 50%;"><small> </small>
            <small> </small>
            <div style="text-align: center;"><small><b>E-da.com.ua</b>
- локальная служба доставки.<br>
            <br>
E-da.com.ua - новый он-лайновый магазин с доставкой продуктов на
дом.<br>
            </small>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <br
 style="font-style: italic;">
            <small> </small>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<?php
if($num_rows!=0){
if ($name!=""){
echo 'Сейчас Вы находитесь в магазине <big style="color: rgb(204, 0, 0);"><big>', $store_name, '</big></big><br>
Ознакомьтесь с доступным ассортиментом,<br>
добавляйте новые товары,<br>
изменяйте устаревшие данные.<br>';}}
else
echo '<br><br><br><br>Вернитесь на предыдущую страницу и введите название магазина правильно';
?>
            </div>
            <small></small></td>
          </tr>
        </tbody>
      </table>
      <small> <br>
      </small> <small> </small><small> </small><small> </small><small>
      </small><small> </small> <small> </small>
      <table style="width: 100%;" border="0" cellpadding="0"
 cellspacing="0">
      </table>
      <?php
      if ($name!="" and $num_rows!=0){
      echo '<div style="text-align: center;">', $message1, $message2, $message3,'<br>
<small> </small></div>
<small> </small><small> </small><small> </small><small> </small><small>
</small> <small> </small>
<table style="width: 100%;" border="0" cellpadding="0"
cellspacing="0">
</table>
      
          <table class="sectoring"
 style="border-style: none solid solid; border-color: -moz-use-text-color rgb(204, 204, 204) rgb(204, 204, 204); border-width: medium 1px 1px;"
 width="100%">
        <tbody>
          <tr>
            <td style="padding: 0px 10px 0px 5px;" valign="top"
 width="33%">
            <div style="padding-bottom: 10px;"> </div>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/special.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory" id="red"><a href="Manage_section.php?section=1" class="category">Товары по специальным
 ценам</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/alcohol.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=2" class="category">Алкогольные
напитки</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/tabacco.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=3" class="category">Сигареты
и табак</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/juices.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=4" class="category">Безалкогольные
напитки</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/teaandcoffe.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=5" class="category">Чай,
кофе, какао</a></span></td>
                </tr>
              </tbody>
            </table>
            <div style="padding-bottom: 10px;"><a href="apology520/"
 class="catalog"><br>
            </a> </div>
            </td>
            <td
 style="border-left: 1px solid rgb(204, 204, 204); padding: 0px 5px 0px 10px;"
 valign="top" width="33%">
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/bread.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=6" class="category">Хлеб и
хлебобулочные изделия</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/bacalea.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=7" class="category">Бакалея</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/meat.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=8" class="category">Мясо и
мясопродукты</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/fish.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=9" class="category">Рыба и
морепродукты</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/cakes.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=10" class="category">Кондитерские
изделия</a></span></td>
                </tr>
              </tbody>
            </table>
            <table class="sectoring" style="margin: 5px 0px;">
              <tbody>
                <tr>
                  <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/concerve.gif" alt=""></td>
                  <td style="padding-left: 5px;"><span
 class="mainCategory"><a href="Manage_section.php?section=11" class="category">Консервы</a></span></td>
                </tr>
              </tbody>
            </table>
            <div style="padding-bottom: 10px;"><a href="apology616/"
 class="catalog"><br>
            </a> </div>
            </td>
          </tr>
        </tbody>
      </table>
      </td>
      <td
 style="border-left: 1px solid rgb(204, 204, 204); padding: 0px 5px 0px 10px;"
 valign="top" width="33%">
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/milk.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=12" class="category">Молоко и
молочные продукты</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/icecream.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=13" class="category">Мороженое
и десерты замороженные</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/fruitsandveg.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=14" class="category">Овощи,
фрукты, орехи</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/dishes.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=15" class="category">Готовые
блюда и полуфабрикаты</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/babie.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=16" class="category">Детские
товары</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/pets.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=17" class="category">Корма
для животных</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/newspapers.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=18" class="category">Журналы,
газеты, книги</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/hygienics.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=19" class="category">Средства
гигиены, парфюмерия, косметика</a></span></td>
          </tr>
        </tbody>
      </table>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/home.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=20" class="category">Хозяйственные
товары</a></span></td>
          </tr>
        </tbody>
      </table>
      <div style="padding-bottom: 10px;"> </div>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 36px; height: 36px;"
 src="images/gifts.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=21" class="category">Подарочные
наборы, упаковка для подарков</a></span></td>
          </tr>
        </tbody>
      </table>
      <div style="padding-bottom: 10px;"> </div>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 68px; height: 36px;"
 src="images/salad.gif" alt=""></td>
            <td style="padding-left: 5px;"><span class="mainCategory"><a
 href="Manage_section.php?section=22" class="category">Собственное
производство</a></span></td>
          </tr>
        </tbody>
      </table>
      </td>
    </tr>
  </tbody>
</table>';}
?>
<table class="sectoring" border="0" width="100%">
  <tbody>
    <tr><?php/*
    // Connecting, selecting database
$link = mysql_connect('localhost', 'edacomua_toxa', 'hidden')
    or die('Could not connect: ' . mysql_error());
echo 'Connected successfully';
mysql_select_db('edacomua_meal_store') or die('Could not select database');

// Performing SQL query
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$query = 'SELECT * FROM meal_global';
$result = mysql_query($query) or die('Query failed: ' . mysql_error());

// Printing results in HTML
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
echo "<br> <br>This is output table of meal_global <br>","<table>\n";
while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
    echo "\t<tr>\n";
    foreach ($line as $col_value) {
        echo "\t\t<td>$col_value</td>\n";
    }
    echo "\t</tr>\n";
}
echo "</table>\n";

// Free resultset
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
mysql_free_result($result);

// Performing SQL query
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$query = 'SELECT * FROM meal_local';
$result = mysql_query($query) or die('Query failed: ' . mysql_error());

// Printing results in HTML
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
echo "<br> <br>This is output table of meal_local <br>","<table>\n";
while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
    echo "\t<tr>\n";
    foreach ($line as $col_value) {
        echo "\t\t<td>$col_value\t</td>\n";
    }
    echo "\t</tr>\n";
}
echo "</table>\n";

// Free resultset
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
mysql_free_result($result);

// Closing connection
mysql_close($link);*/    
    ?>
      <td width="100%"><br>
      </td>
    </tr>
  </tbody>
</table>
<span style="font-family: Tahoma,Arial,Helvetica,sans-serif;"><span
 style="font-weight: bold;"></span></span><br>
<table class="text" border="0" cellpadding="0" cellspacing="0"
 width="100%">
  <tbody>
    <tr>
      <td><small> <br>
      </small>
      <div style="text-align: center;"><small>e-mail: <a
 href="mailto:info@e-da.com.ua">info@e-da.com.ua</a></small><br>
      <small>2007-2008 © e-da.com.ua&nbsp; Украина </small></div>
      </td>
      <td> <small> </small><br>
      </td>
    </tr>
  </tbody>
</table>
<small> </small>
<small> <br>
<br>
</small>
</body>
</html>
