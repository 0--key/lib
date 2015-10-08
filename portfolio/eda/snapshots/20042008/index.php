<?php
echo '<form action="login.php" method="post">
        <table class="text" style="text-align: center; width: 90%;"
 border="1" cellpadding="2" cellspacing="2">
          <tbody>
            <tr>
              <td>&nbsp;Nick<br>
&nbsp;<input maxlength="10" size="10" class="inputbox" name="pseudo"><br>
              </td>
            </tr>
            <tr>
              <td>&nbsp;Pseudo<br>
&nbsp;<input maxlength="8" size="8" class="inputbox" name="parol"><br>
              </td>
            </tr>
          </tbody>
        </table>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; <input
 src="images/okblue.gif" alt="Send It In!" align="absmiddle" height="20"
 type="image" width="30"> </form>';

/*************/

    // Connecting, selecting database
$link = mysql_connect('localhost', 'edacomua_toxa', 'musiqpusiq')
    or die('Could not connect: ' . mysql_error());
echo 'Connected successfully';
mysql_select_db('edacomua_meal_store') or die('Could not select database');

// Performing SQL query
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$query = 'SELECT * FROM runners'; //Это запрос таблицы курьеров
$result = mysql_query($query) or die('Query failed: ' . mysql_error());

// Printing results in HTML
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
echo '<br> This is output table of runners <br>',"<table>\n";
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
$query = 'SELECT * FROM stores';//Это запрос из таблицы магазинов
$result = mysql_query($query) or die('Query failed: ' . mysql_error());

// Printing results in HTML
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
echo"<br> <br>", 'This is output table of stores <br>', "<table>\n";
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
$query = 'SELECT * FROM customers';//Это запрос из таблицы клиентов
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die('Query failed: ' . mysql_error());

// Printing results in HTML
echo "<br> <br>", 'This is output table of customers <br>', "<table>\n";
while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
    echo "\t<tr>\n";
    foreach ($line as $col_value) {
        echo "\t\t<td>$col_value</td>\n";
    }
    echo "\t</tr>\n";
}
echo "</table>\n";

// Free resultset
mysql_free_result($result);

// Performing SQL query
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$query = 'SELECT * FROM meal_global';//Это запрос глобальной таблицы продуктов
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
$query = 'SELECT * FROM meal_local';//Это запрос локальной таблицы продуктов
$result = mysql_query($query) or die('Query failed: ' . mysql_error());

// Printing results in HTML
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
echo "<br> <br>This is output table of meal_local <br>","<table>\n";
while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
    echo "\t<tr>\n";
    foreach ($line as $col_value) {
        echo "\t\t<td>$col_value</td>\n";
    }
    echo "\t</tr>\n";
}
$timestamp = date("Y-m-d % H:i:s");
echo $timestamp;
echo "</table>\n";

// Free resultset
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
mysql_free_result($result);

// Closing connection
mysql_close($link);    
    ?>