<?
  function db_err($handle, $message) {
  printf("%s: %d: %s\n", $message,
  mysql_errno($handle),mysql_error($handle));
  die();
  }
function db_connect() {

global $dbName,$dbUser,$dbPass,$dbServer;
  $dbh = mysql_connect($dbServer,$dbUser,$dbPass);
  if(!$dbh) { db_err($dbh, "mysql_connect"); }
  $res = mysql_select_db($dbName);
  if(!$res) { db_err($dbh, "mysql_select_db"); }
  return($dbh);

}
