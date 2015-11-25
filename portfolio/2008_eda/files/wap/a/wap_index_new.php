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

if (empty($cmd)) { $cmd = "Menu"; }

switch ($cmd) {
   case "Menu";

      echo "<card id=\"Menu\">\n";
      echo "<p mode=\"nowrap\">".$lf;
      
      // Set up Select menu list 
      echo "<select name=\"Select\" title=\"Select:\">".$lf;

      // Go through results from Query, listing each as a CHOICE entry
      echo "<option onpick=\"?cmd=ist\">";
      echo "List Contacts</option>".$lf;
      echo "<option onpick=\"?cmd=Search\">";
      echo "Search Contacts</option>".$lf;
      
      // Close select
      echo "</select>".$lf;

      // Close card
      echo "</p>".$lf."</card>".$lf;

   break;
   case "list";

// Open link to DB
$link = mysql_run();



      echo "<card>\n";
      
      // Get specific record
      $query = "select * from runners";
      
      $result = mysql_query($query)
        or die("Query failed:$query");
   
      // Get data and display
      while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) 
      {
        $iv = $line['iv'];

        echo "<p mode=\"wrap\">".$lf;
        echo "$line[nick]", "  ", decrypt_data($line['name'], $iv), "<br />".$lf;
        echo decrypt_data($line['phone_no'], $iv), "<br />".$lf;
        echo decrypt_data($line['e_mail'], $iv), "<br />".$lf;
/*        echo "<a href=\"wtai://wp/mc;$line[Phone]\" title=\"Dial\">";
        echo "$line[Phone]</a><br />".$lf;
        echo "<a href=\"?cmd=Menu\" title=\"Menu\">";
        echo "[Home Menu]</a><br /><br />".$lf;
*/
        $Date = date("M j, Y", strtotime($line['time']));
        echo "Record Updated:<br />$Date</p>";
        }
        
        // Close record display card
        echo $lf."</card>".$lf;
        mysql_close($link);
        break;
      
      case "Search";
   
      echo "<card id=\"Search\">\n";
      echo "<do type=\"accept\" label=\"Go\">".$lf;
      echo "<go href=\"?cmd=List&amp;search=\$searchtext\">".$lf;
      echo "</go>".$lf;
      echo "</do>".$lf;

      echo "<p>".$lf;
      echo "<b>Поиск курьера</b><br/>Искать по:".$lf;
      echo "<input name=\"searchtext\" title=\"Search\" type=\"text\"";
      echo "  format=\"10m\"/>";
      echo "</p>".$lf;
      echo "</card>".$lf;
   
   break;
}

echo $lf."</wml>".$lf;



?>