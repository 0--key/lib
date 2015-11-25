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
echo "<?xml version=\"1.0\" encoding=\"cp1251\"?>\n";  
echo "<!DOCTYPE wml PUBLIC \"-//WAPFORUM//DTD WML 1.1//EN\""  
   . " \"http://www.wapforum.org/DTD/wml_1.1.xml\">\n"; 
echo "<wml>\n";
// Line feed
$lf = chr(10);
	$link = mysql_run();
	if(!empty($_POST['func']))
	{
	$nick = $_POST['nick'];// $name = $_POST['name'];
	switch ($_POST['func'])
		{
		case "success":
		$time = date("Y-m-d H:i:s"); $ord_no = $_POST['ord_no'];
		$query_to_orders = mysql_query("update orders set status='game_over', delivery='$time' where or_no='$ord_no'") 
		or die ('Query to runners failed: ' . mysql_error());
		$query_to_runners = mysql_query("update runners set status='offline' where nick='$nick'") 
		or die ('Query to runners failed: ' . mysql_error());
		break;
		case "deny":
		$time = date("Y-m-d H:i:s"); $ord_no = $_POST['ord_no']; $cu_nick = $_POST['cu_nick'];
		$query_to_orders = mysql_query("update orders set status='game_over', delivery='$time', quality='wrong' where or_no='$ord_no'") 
		or die ('Query to runners failed: ' . mysql_error());
		$query_to_runners = mysql_query("update runners set status='offline' where nick='$nick'") 
		or die ('Query to runners failed: ' . mysql_error());
		$query_to_deny_customer = mysql_query("update customers set priority='deny' where nick='$cu_nick'") 
		or die ('Query to update&deny customer failed: ' . mysql_error());
		break;
		case "take_order":
		$time = date("Y-m-d H:i:s"); $ord_no = $_POST['ord_no'];
		$query_to_orders = mysql_query("update orders set status='with_ru', cr_time3='$time' where or_no='$ord_no'") 
		or die ('Query to runners failed: ' . mysql_error());
		break;
		
		case "get_ready":
		$query_to_runners = mysql_query("update runners set status='ready' where nick='$nick'") 
		or die ('Query to runners failed: ' . mysql_error());
		break;
		
		case "get_offline":
		$query_to_runners = mysql_query("update runners set status='offline' where nick='$nick'") 
		or die ('Query to runners failed: ' . mysql_error());
		}
	}

$nick = $_POST['nick']; $pass = $_POST['pass']; 
$query = "select * from runners where nick='$nick' and password='$pass'";
$result = mysql_query($query)
or die("Query failed:$query");
$num_rows = mysql_num_rows($result);

echo '<card id="Auth" title="';
if($num_rows==1) echo "WorkSpace";
else echo "Wrong pass!";
echo "\">\n";
echo "<p align=\"center\">".$lf;
if($num_rows==1)
	{
	$row = mysql_fetch_array($result, MYSQL_ASSOC);
	$iv = $row['iv']; $name = decrypt_data($row['name'], $iv);
	}
	else echo "<br/><br/><b>Wrong pass!</b>\n";
if($num_rows==1)
	{
	echo "<b>Welcome, $name!</b><br/>\n";
	switch ($row['status'])
		{
			case "offline":
			echo "Ваше состояние в нашей системе - <br/><b>\"НЕ ГОТОВ\"</b><br/>\n";
			echo "<anchor> Изменить--->\n<go method=\"post\" href=\"login.php\">\n<postfield name=\"func\" value=\"get_ready\"/>\n<postfield name=\"nick\" value=\"$nick\"/>\n<postfield name=\"pass\" value=\"$pass\"/>\n</go>\n</anchor>\n";
			break;
			case "ready":
			echo "Ваше состояние в нашей системе - <br/><b>\"ГОТОВ\"</b><br/>\n";
			echo "<anchor> Изменить--->\n<go method=\"post\" href=\"login.php\">\n<postfield name=\"func\" value=\"get_offline\"/>\n<postfield name=\"nick\" value=\"$nick\"/>\n<postfield name=\"pass\" value=\"$pass\"/>\n</go>\n</anchor>\n";
			break;
			case "busy":
			echo "Ваше состояние в нашей системе<br/><b>\"ЗАНЯТ\"</b>\n";
				$query_to_orders = mysql_query("SELECT or_no, status, cr_time2, cu_nick FROM orders WHERE ru_nick = '$nick' and 									quality='well' order by cr_time2 DESC") 
				or die ('Query to orders failed: ' . mysql_error());
				$order_row = mysql_fetch_row($query_to_orders);
				$ord_no = $order_row[0]; $cu_nick = $order_row[3];
					switch($order_row[1])
					{
					case 'with_ru':
						echo "<br/>выполнением заказа<br/><b>".$ord_no."</b> ".$order_row[2]."\n";
						//echo '4820000123456<br/>Халва<br/>0.14%<br/>3шт.*2<br/>***-***';
						$query = "SELECT id, pcs FROM baskets where order_no='$ord_no'"; //Это запрос таблицы baskets
						$result = mysql_query($query) or die('Query failed: ' . mysql_error());
						$i=0; echo '<br/>';
						while ($line_from_basket = mysql_fetch_array($result, MYSQL_ASSOC))
						{
						if($line_from_basket['pcs']!=0)//				 Уберём бесополезный нулевой вывод:
							{
						$i++; echo '<b>', $i, '</b> ', $line_from_basket['id'], '<br/>';
						/*							Сделаем запрос в meal_global&local для
															получения доп инфы*/
						$meal_id = $line_from_basket['id'];
						$query_to_global = mysql_query("select meal_name, manufacturer, capacity from meal_global where 						id='$meal_id'")
						or die('Could not select from table meal_global ' . mysql_error());
						$g_result = mysql_fetch_row($query_to_global);
						echo htmlspecialchars($g_result[0]), '**', $g_result[2], '<br/>', htmlspecialchars($g_result[1]), '<br/>';
						$query_to_local = mysql_query("select price_UH, allocation from meal_local where id='$meal_id'")
						or die('Could not select from table meal_local ' . mysql_error());
						$l_result = mysql_fetch_row($query_to_local);
						echo $l_result[0], ' * ', $line_from_basket['pcs'], '#', $l_result[1], '<br/>***-***<br/>';
							}
						}
						echo '<b>Адрес доставки:</b>';
						$query_customer = mysql_query("select * from customers where nick='$cu_nick'")
						or die('Could not select from table cusotmers ' . mysql_error());
						$customer_row = mysql_fetch_array($query_customer, MYSQL_ASSOC);
						echo decrypt_data($customer_row['town'], $customer_row['iv']), '<br/>';
						echo decrypt_data($customer_row['streettype'], $customer_row['iv']), ' ', decrypt_data($customer_row['streetname'], $customer_row['iv']), '<br/>';
						echo decrypt_data($customer_row['build_no'], $customer_row['iv']);
						if($customer_row['korpus']!=0) echo '/', $customer_row['korpus'];
						//if($customer_row['flat_no']!=0) 
						echo '-', decrypt_data($customer_row['flat_no'], $customer_row['iv']), '<br/>';
						if($customer_row['floor']!=0) echo $customer_row['floor'], '-й этаж,<br/>';
						if(decrypt_data($customer_row['access_mode'], $customer_row['iv'])=="кодовый") echo 'Код замка:', decrypt_data($customer_row['door_code'], $customer_row['iv']), '<br/>';
						switch ($customer_row['priority'])
						{
						case "first":
						echo 'НОВИЧЕК';
						break;
						case "low":
						echo 'БЫВАЛЫЙ';
						break;
						case "high":
						echo 'ПОСТОЯННЫЙ';
						break;
						}
						echo '<br/>';
						echo '<anchor>Ok<go method="post" href="login.php" ><postfield name="func" value="success"/><postfield name="nick" value="', $nick, '"/><postfield name="pass" value="', $pass, '"/><postfield name="ord_no" value="', $ord_no, '"/></go></anchor>';
						echo '<br/><br/><anchor>Deny<go method="post" href="login.php" ><postfield name="func" value="deny"/><postfield name="nick" value="', $nick, '"/><postfield name="pass" value="', $pass, '"/><postfield name="ord_no" value="', $ord_no, '"/><postfield name="cu_nick" value="', $cu_nick, '"/></go></anchor>';
						break;
   				 	case 'in_process':
   				 	echo "<br/>Вам поступил заказ No ";
   				 	//.."";
   				 	echo '<anchor>', $ord_no, '<go method="post" href="login.php" ><postfield name="func" value="take_order"/><postfield name="nick" value="', $nick, '"/><postfield name="pass" value="', $pass, '"/><postfield name="ord_no" value="', $ord_no, '"/></go></anchor>';
   				 		break;
					}
					break;
		}	
	}
echo "</p>".$lf."</card>".$lf;
echo $lf."</wml>".$lf;
	//echo $_POST['nick'], $_POST['pass'];
mysql_close($link);	
?>
		

