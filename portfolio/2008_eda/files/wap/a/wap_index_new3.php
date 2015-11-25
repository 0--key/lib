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

// Open link to DB
/*$link = mysql_connect("localhost", "webuser", "webby99")
  or die("Could not connect to database!");
mysql_select_db("customers")
  or die("Could not select database!");
*/
// Line feed
$lf = chr(10);

// Make sure that index into DB has value
if (empty($idx)) { $idx = 0; }

if (empty($cmd)) { $cmd = "Menu"; }

switch ($cmd) {

   case "Menu";

      echo "<card id=\"Menu\">\n";
      echo "<p mode=\"nowrap\">".$lf;
      
      // Set up Select menu list 
      echo "<select name=\"Select\" title=\"Select:\">".$lf;

      // Go through results from Query, listing each as a CHOICE entry
      echo "<option onpick=\"?cmd=List\">";
      echo "List Contacts</option>".$lf;
      echo "<option onpick=\"?cmd=Search\">";
      echo "Search Contacts</option>".$lf;
      
      // Close select
      echo "</select>".$lf;

      // Close card
      echo "</p>".$lf."</card>".$lf;

   break;

   case "List";
   	$link = mysql_run();
      // Construct appropriate *count* query
      $query = "select count(*) from runners";
      if (!empty($nick) and !empty($pass))
      {
         $query = $query." where nick=".$nick."and password=".$pass;
         //$query = $query." LastName like \"%".$search."%\"";
      }

      $result = mysql_query($query)
        or die("Query failed:$query");

      $row = mysql_num_rows($result);

      // Construct appropriate query
/*      $query = "select * from Phone";
      if (!empty($search)) {
         $query = $query." where FirstName like \"%".$search."%\" or";
         $query = $query." LastName like \"%".$search."%\"";
      }

      // Get first/next five records
      $query = $query." order by LastName limit ".$idx.",5";

      $result = mysql_query($query,$link)
        or die("Query failed:$query");

      // Advance DB index
      $next = $idx + 5;
*/      
      // Start card
      echo "<card id=\"Contacts\">\n";
      echo "<do type=\"accept\" label=\"View\"> <go href=\"\"/> </do>".$lf;
      
      // Display appropriate full/search heading
      if (empty($nick) or empty($pass))
      {
         echo "<p align=\"center\" mode=\"nowrap\"><b>Неправильный ввод!></b>".$lf;
      } else
      {
         echo "<p mode=\"nowrap\"><b>Search Results</b>".$lf;
      }
      if($row==1)
      {
      echo "Authentification sussess!!!".$lf;
      }
      
      // Set up Select list (list of five records)
/*      echo "<select name=\"View\" title=\"View:\">".$lf;

      // Go through results from Query, listing each as a CHOICE entry
      while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {

        $recordid = $line[Id]; 
        $Name = $line[LastName] . ", " . $line[FirstName];
        $Number = $line[Phone];
        $Prompt = $Name . " (" . $Number . ")";

        // Build URL for option, include DB index and search
        $option = "<option onpick=\"";
        $option = $option."?cmd=Display&amp;id=".$recordid."&amp";
        $option = $option.";idx=".$recordid."&amp;search=".$search."\">";
        $option = $option.$Prompt."</option>".$lf;
        echo $option.$lf;

      }

      // If there are more records to display, set up paging
      //   else mark end of list (to keep Home as same option)
      if ($total_rows >= $next) {

         // Link to next five
         echo "<option title=\"Next\" onpick=\"?cmd=List&amp;idx=$next";

         // Pass Search criteria if exists
         if (!empty($search)) {
            echo "&amp;search=".$search;
         }

         echo "\">[Next Records]".$lf."</option>".$lf;
         
      } else {
      
         echo "<option title=\"End of List\" onpick=\"?cmd=List&amp;idx=$idx";
         
         // Pass Search criteria if exists
         if (!empty($search)) {
            echo "&amp;search=".$search;
         }

         // Close tags
         echo "\">[End of List]".$lf."</option>".$lf;
         
      }         

      // Add option for Home
      echo "<option onpick=\"?cmd=Menu\" title=\"Home\">".$lf;
      echo "[Back to Home]".$lf;
      echo "</option>".$lf;

      // Close select
      echo "</select>".$lf;
*/
      // Close card
      echo "</p>".$lf."</card>".$lf;
      mysql_close($link);
      
   break;
   
   
/*   case "Search";
   
      echo "<card id=\"Search\">\n";
      echo "<do type=\"accept\" label=\"Go\">".$lf;
      echo "<go href=\"?cmd=List&amp;nick=\$nick\&amp;pass=\$pass\">".$lf;
      echo "</go>".$lf;
      echo "</do>".$lf;

      echo "<p align=\"center\">".$lf;
      echo "<b>Phone Book Search</b><br/>Псевдоним:".$lf;
      echo "<input name=\"nick\" title=\"Search\" type=\"text\"";
      echo "  format=\"8M\"/>";
      echo "</p>".$lf;
      echo "<p align=\"center\">".$lf;
      echo "<br/>  Пароль  :".$lf;
      echo "<input name=\"pass\" title=\"Search\" type=\"password\"";
      echo "  format=\"XXXXNN\"/>";
      echo "</p>".$lf;
      echo "</card>".$lf;

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
   
   
   case "Display";
   
      echo "<card>\n";
      
      // Get specific record
      $query = "select * from Phone where Id = \"".$idx."\"";
      
      $result = mysql_query($query,$link)
        or die("Query failed:$query");
   
      // Get data and display
      while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
        $recordid = $line[Idx];

        echo "<p mode=\"wrap\">".$lf;
        echo "$line[LastName], $line[FirstName]<br />".$lf;
        echo "$line[Address]<br />".$lf;
        echo "$line[City], $line[State]  $line[Zip]<br />".$lf;
        echo "<a href=\"wtai://wp/mc;$line[Phone]\" title=\"Dial\">";
        echo "$line[Phone]</a><br />".$lf;
        echo "<a href=\"?cmd=Menu\" title=\"Menu\">";
        echo "[Home Menu]</a><br /><br />".$lf;

        $Date = date("M j, Y", strtotime($line[LastUpdate]));
        echo "Record Updated:<br />$Date";
        
        // Close record display card
        echo $lf."</p></card>".$lf;
        
      }

   
   break;
*/   
}

echo $lf."</wml>".$lf;

//mysql_close($link);

?>
