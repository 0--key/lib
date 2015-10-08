<?php
session_start();
include("functions/Text.inc");
//$pri = $_SESSION['oldprices'];
//$data = $_SESSION['data'];
//echo $data[1];
/*$prices = $_SESSION['prices'];
echo $prices[old][1234567891011];
//echo $pri[0];
$local = array($_POST['local']);
echo $local[1234567891017];
$varname = '1234567891017';
$var = $_POST["price$varname"];
echo $var; echo $_POST["local1234567891017"];
*/
// Ща выведем массивы из старых значений:
$id_old = $_SESSION['oldid'];
$prices_old = $_SESSION['oldprices'];
$allocation_old = $_SESSION['oldallocation'];
$presence_old = $_SESSION['oldpresence'];
$i = 0;
foreach($id_old as $item){
$price1 = "price$item";
$allocation1 = "allocation$item";
$presence1 = "presence$item";
print "$item $prices_old[$i] $_POST[$price1]  $allocation_old[$i]  $_POST[$allocation1]
 $presence_old[$i]  $_POST[$presence1] <br>";
if($prices_old[$i]==$_POST[$price1] and
$allocation_old[$i]==$_POST[$allocation1] and
$presence_old[$i]==$_POST[$presence1]){
// строка Id не изменилась
echo "Не изменилась<br> ";

}
else {
// строка изменилась, делаем проверку:
//$price_good = filter_input(INPUT_POST, "price$item", FILTER_SANITIZE_NUMBER_FLOAT);
$price_good = str_replace(",", ".", $_POST[$price1]);
$price_good = str_good_num($price_good, 5);

$allocation_good = str_good($_POST[$allocation1], 5);
$presence_good = str_good($_POST[$presence1], 3);
echo 'строка изменилась, делаем проверку  ', $_POST[$price1], $price_good, $presence_good, '<br>';
if(filter_var($price_good, FILTER_VALIDATE_FLOAT) and
$allocation_good==$_POST[$allocation1] and
$presence_good==$_POST[$presence1]){
//В строке нет запрещённых символов

echo " Символы проверены, строка была изменена, можно записывать в базу <br> 
  $price_good  $allocation_good  $presence_good <br>";
  $link = mysql_run();
  $timestamp = date("Y-m-d H:i:s");
  $nick = $_SESSION['nick'];
  $store_name = $_SESSION['store_name'];
  $query = "UPDATE meal_local SET price_UH='$price_good', 
  allocation='$allocation_good', presence='$presence_good', 
  modify_time='$timestamp' WHERE id='$item' and author_nick='$nick' and 
  store_name='$store_name'";
  mysql_cyr();
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
mysql_close($link);
  
}
else {
//$val_message[] = 
echo "Wrong symbols in string $item !!!";
//echo $val_message[0];
}
}
$i++;
}
//*** a string with tags ***/
$string = "'@#$%^&*foo</script><br><p /><li />";

/*** sanitize the string ***/
echo filter_var($string, FILTER_SANITIZE_STRING), "<br>";
echo $string;
?>
