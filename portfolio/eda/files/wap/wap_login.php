<?php
session_start();  
include("/home/edacomua/functions/Text.inc");
if(isset($_SESSION['views']))
    $_SESSION['views'] = $_SESSION['views']+ 1;
else
    $_SESSION['views'] = 1;
    
/*											Сделаем смену статуса заказа на тот случай, когда курьер 												подтвердил получение заказа и готовность его выполнения:
*/
if($_SESSION['auth']=='correct' and $_GET['func']=='take_order')
{
	$link = mysql_run();
	$ord_no = $_SESSION['or_no'];
	$time = date("Y-m-d H:i:s");
	$query_to_orders = mysql_query("update orders set status='with_ru', cr_time3='$time' where or_no='$ord_no'") 
	or die ('Query to runners failed: ' . mysql_error());
	mysql_close($link);
}
/*											Сделаем смену статуса заказа на тот случай, когда курьер 												подтвердил успешное выполнение заказа:
*/
if($_SESSION['auth']=='correct' and $_GET['func']=='order_success')
{
	$link = mysql_run();
	$ord_no = $_SESSION['or_no']; $nick = $_SESSION['nick'];
	$time = date("Y-m-d H:i:s");
	$query_to_orders = mysql_query("update orders set status='game_over', delivery='$time' where or_no='$ord_no'") 
	or die ('Query to runners failed: ' . mysql_error());
	$query_to_runners = mysql_query("update runners set status='offline' where nick='$nick'") 
	or die ('Query to runners failed: ' . mysql_error());
	mysql_close($link);
}
/*											Сделаем смену статуса заказа на тот случай, когда курьер 												подтвердил отказ от оплаты заказа:
*/
if($_SESSION['auth']=='correct' and $_GET['func']=='order_deny')
{
	$link = mysql_run();
	$ord_no = $_SESSION['or_no']; $nick = $_SESSION['nick'];
	$time = date("Y-m-d H:i:s");
	$query_to_orders = mysql_query("update orders set status='game_over', delivery='$time', quality='wrong' where or_no='$ord_no'") 
	or die ('Query to runners failed: ' . mysql_error());
	$query_to_runners = mysql_query("update runners set status='offline' where nick='$nick'") 
	or die ('Query to runners failed: ' . mysql_error());//					Надо наколбасить и обновление таблицы customers:
	$query_to_find_customer = mysql_query("select cu_nick from orders where or_no='$ord_no'") 
	or die ('Query to find customer failed: ' . mysql_error());
	$cu_nick = mysql_fetch_row($query_to_find_customer);
	$cu_nick_deny = $cu_nick[0];
	$query_to_deny_customer = mysql_query("update customers set priority='deny' where nick='$cu_nick_deny'") 
	or die ('Query to update&deny customer failed: ' . mysql_error());
	mysql_close($link);
}
/*											Сделаем смену статуса курьера  												offline ---> ready:
*/
if($_SESSION['auth']=='correct' and $_GET['func']=='get_ready')
{
	$link = mysql_run();
	$nick = $_SESSION['nick'];
	$query_to_runners = mysql_query("update runners set status='ready' where nick='$nick'") 
	or die ('Query to runners failed: ' . mysql_error());
	mysql_close($link);
}
/*											Сделаем смену статуса курьера  												ready ---> offline:
*/
if($_SESSION['auth']=='correct' and $_GET['func']=='get_offline')
{
	$link = mysql_run();
	$nick = $_SESSION['nick'];
	$query_to_runners = mysql_query("update runners set status='offline' where nick='$nick'") 
	or die ('Query to runners failed: ' . mysql_error());
	mysql_close($link);
}
echo '<?xml version="1.0" encoding="windows-1251"?>
<!DOCTYPE wml PUBLIC "-//WAPFORUM//DTD WML 1.1//EN" "http://www.wapforum.org/DTD/wml_1.1.xml">
<wml>
<card id="main" title="E-da.com.ua WAP">';


    
    // let's make insurance
    if($_POST['wap_pseudo']!="" and $_POST['wap_parol']!="")
{
    $pseudo = $_POST['wap_pseudo']; $parol = $_POST['wap_parol'];
    $pseudo1 = htmlspecialchars($_POST['wap_pseudo']); $parol1 = htmlspecialchars($_POST['wap_parol']);
    $nick = str_good($pseudo1, 8);
    $pass = str_good($parol1, 6);
    if($nick==$pseudo and $pass==$parol) $_SESSION['auth'] = 'correct';
    else $auth = 'danger';
}
    else $auth='null';
    
echo ' 
<p>
<div style="text-align: center">';
//echo $nick, $pass;
if($_SESSION['auth']=='correct')
{
	$link = mysql_run();
	$query = mysql_query("SELECT password, status, type FROM runners WHERE nick = '$nick' ") 
	or die ('Query to runners failed: ' . mysql_error());
	$num_rows = mysql_num_rows($query);
		if($num_rows==1)
		{
		$row = mysql_fetch_row($query);
			if($row[0]==$pass)
			{
			$_SESSION['nick'] = $nick;
			$_SESSION['runners_type'] = $row[2];
			 echo 'Authentification success!!!<br>', $row[2], '<br>', $row[1], '<br>';
			} 
		}


	mysql_close($link);
}

if($_SESSION['nick']!="" and $_SESSION['auth']=='correct')
{	
	$nick = $_SESSION['nick'];
	$link = mysql_run();
	$query = mysql_query("SELECT status, type, town, iv  FROM runners WHERE nick = '$nick' ") 
	or die ('Query to runners failed: ' . mysql_error());
	$row = mysql_fetch_row($query);
			 echo 'Ваше текущее состояние в нашей системе: ';
			 	switch($row[0])
			 	{
			 	case 'offline':
				    echo '"не готов"<br><a href="wap_login.php?func=get_ready">Сообщить о готовности====></a><br><a href="wap_login.php?func=view_stat">Посмотреть статистику====></a>';
   				 break;
				case 'ready':
  				  echo '<br>"готов к получению заказов"<br><a href="wap_login.php?func=get_offline">Сообщить о перерыве в готовности====></a>';
 				   break;
				case 'busy':
				$query_to_orders = mysql_query("SELECT or_no, status, cr_time2 FROM orders WHERE ru_nick = '$nick' and 									quality='well' order by cr_time2 DESC") 
				or die ('Query to orders failed: ' . mysql_error());
				$order_row = mysql_fetch_row($query_to_orders);
					switch($order_row[1])
					{
					case 'with_ru':
						echo '<br>занят выполнением заказа<br>№ ', $order_row[0];
						/*								сделаем вывод содержимого корзины
															заказа	
															*/		
						$ord_no = $order_row[0];
						    
						$link_to_output = mysql_run();
						$query = "SELECT id, pcs FROM baskets where order_no='$ord_no'"; //Это запрос таблицы baskets
						$result = mysql_query($query) or die('Query failed: ' . mysql_error());
						$i=0; echo '<br>';
						while ($line_from_basket = mysql_fetch_array($result, MYSQL_ASSOC))
						{
						if($line_from_basket['pcs']!=0)//				 Уберём бесополезный нулевой вывод:
							{
						$i++; echo $i, '<br>', $line_from_basket['id'], '<br>';
						/*							Сделаем запрос в meal_global&local для
															получения доп инфы*/
						$meal_id = $line_from_basket['id'];
						$query_to_global = mysql_query("select meal_name, manufacturer, capacity from meal_global where 						id='$meal_id'")
						or die('Could not select from table meal_global ' . mysql_error());
						$g_result = mysql_fetch_row($query_to_global);
						echo $g_result[0], '  ', $g_result[2], '  ', $g_result[1], '<br>';
						$query_to_local = mysql_query("select price_UH, allocation from meal_local where id='$meal_id'")
						or die('Could not select from table meal_local ' . mysql_error());
						$l_result = mysql_fetch_row($query_to_local);
						echo $l_result[0], ' * ', $line_from_basket['pcs'], '<br>', $l_result[1], '<br>-*--*---*----*-----						*-----*<br>';
							}
						}
						mysql_close($link_to_output);
						echo '<a href="wap_login.php?func=order_success">Доставку совершил, оплату получил ---></a><br><br><a href="wap_login.php?func=order_deny"><-----Клиент отказался от оплаты!</a>';
   				 		break;
   				 	case 'in_process':
   				 		echo '<br>', $order_row[2], '<br>Вам поступил заказ под номером ', $order_row[0], '!!!<br><a href="wap_login.php?func=take_order">Приступить к выполнению===></a><br><br><br><a href="wap_login.php?func=deny_order"><====Отказаться от выполнения</a>'; $_SESSION['or_no'] = $order_row[0];
   				 		break;
					}
   				 //echo '<br>занят выполнением заказа<br>№ ', $order_row[0];
   				 break;
			 	}
			 		mysql_close($link);
}
echo '
</div>	
</p>';
echo $_POST['wap_pseudo'], '<br/>', $_POST['wap_parol'];
?>

</card>
</wml>