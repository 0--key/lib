<?php
session_start();
$id = htmlspecialchars($_POST['meal_id']);
//$SESSION['id'] = $id;
$section_code = $_SESSION['section_code'];
$section_name = $_SESSION['section_name'];
$nick = $_SESSION['nick'];
$name = $_SESSION['name'];
$town = $_SESSION['town'];
$store_name = $_SESSION['store_name'];
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <title>E-da.com.ua - �������� �� ���</title>
  <link rel="SHORTCUT ICON" href="images/favicon.ico">
  <link href="css/styles.css" rel="stylesheet" type="text/css">
  <meta http-equiv="Content-Type"
 content="text/html;charset=windows-1251">
  <meta name="description" content="�����������">
  <meta name="keywords" content="� e-da.com.ua. �������� �� �������">
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
 class="menu_link"><a href="apology.html">�������<br>
      </a></span></small></td>
      <td style="background-color: rgb(223, 143, 56);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(214, 151, 83);"><small><span
 class="menu_link"><a href="apology.html">������</a></span></small></td>
      <td style="background-color: rgb(214, 151, 83);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(205, 155, 102);"><small><span
 class="menu_link"><a href="apology.html">������</a></span></small></td>
      <td style="background-color: rgb(205, 155, 102);"><small>&nbsp;</small></td>
      <td class="menu_razdel"
 style="width: 15%; background-color: rgb(212, 170, 128);"><small><span
 class="menu_link"><a href="AboutUs.html">� ���<br>
      </a></span></small></td>
      <td style="background-color: rgb(212, 170, 128);"><small>&nbsp;</small></td>
      <td class="menu_razdel" width="15%"><small><span class="menu_link"><a
 href="apology.html">��������������</a></span></small></td>
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
- ����� � ��������
��������� �� ���, � ����, �� ����</big><small><br>
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
      <span style="color: rgb(153, 51, 0);">����</span><br
 style="color: rgb(153, 51, 0);">
      <span style="color: rgb(153, 51, 0);">�������:<br>
      <br style="color: rgb(153, 51, 0);">
      </span>
      <table class="sectoring" style="margin: 5px 0px;">
        <tbody>
          <tr>
            <td><img
 style="border: 0px solid ; width: 39px; height: 36px;"
 src="Ub1small.gif" alt=""></td>
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
 src="Ub2small.gif" alt=""></td>
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
 style="border: 0px solid ; width: 36px; height: 36px;" src="Ubdark.gif"
 alt=""></td>
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
 src="UbTogether.gif" alt=""></td>
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
 src="UbTogether1.gif" alt=""></td>
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
                        if (strlen($id)==13){
            if ($name!="" and $nick!=""){ 
            echo '���������(��),', $name,
           '!<br>
�� ���������� � �������� ', $store_name, ',<br>', $town,
',<br>
� ������ "', $section_name, '"';
$_SESSION['id'] = $id;
$link = mysql_connect('localhost', 'edacomua_toxa', 'musiqpusiq')
  or die('Could not connect: ' . mysql_error());
//echo 'Connected successfully';
mysql_select_db('edacomua_meal_store') or die('Could not select database');

// Performing SQL query
$query = "SELECT * FROM meal_global WHERE id = '$id' ";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result = mysql_query($query) or die ('Query failed: ' . mysql_error());
$num_rows_id = mysql_num_rows($result);
$_SESSION['num_rows_global'] = $num_rows_id;
if ($num_rows_id==1){
//��������� ������ �� ������� meal_global
$meal_row = mysql_fetch_array($result);
$meal_section = $meal_row[1];
$meal_name = $meal_row[2]; $meal_manufacturer = $meal_row[3];
//� �� meal_local
$query1 = "SELECT * FROM meal_local WHERE id='$id' AND store_name='$store_name'";
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
$result1 = mysql_query($query1) or die ('Query failed: ' . mysql_error());
$num_rows_id_in_store = mysql_num_rows($result1);
//if ($num_rows_id_in_store==""){
//$num_rows_id_in_store = 0;}
$_SESSION['num_rows_local'] = $num_rows_id_in_store;
}
mysql_close($link);
}
else echo '<br><br><br><br><br>�������� ��������� �������������� <br>
<a href="index.php">�� ������� ��������.</a><br><br><br><br><br>';}
else echo '<br><br><br><br><br>�����-��� ����� �����������!<br>
� �� ������ ���� 13 ����!<br>
��������� �� ���������� ��������.<br><br><br><br>';
?><br>
            </th>
          </tr>
        </tbody>
      </table>
      <?php
      if ($num_rows_id==1){ echo '
      <div style="text-align: center;"><br>
����� �� �����-����� ', $id, ' ��� �������� ����� �������, ���:<br>
      <div style="text-align: left;">
      <ul style="color: rgb(0, 153, 0);">
        <li>', $meal_name, ';</li>
        <li>', $meal_manufacturer, '.</li>
      </ul>';
      if ($meal_section!=$section_code){ echo '
      <div style="text-align: center;">�� ���� ����� �� ������� ������
(<big style="color: rgb(153, 51, 0);">';
if ($meal_section == 1){
$section_name_truth = '������ �� ����������� �����';}
if ($meal_section == 2){
$section_name_truth = '����������� �������';}
if ($meal_section == 3){
$section_name_truth = '�������� � �����';}
if ($meal_section == 4){
$section_name_truth = '�������������� �������';}
if ($meal_section == 5){
$section_name_truth = '���, ����, �����';}
if ($meal_section == 6){
$section_name_truth = '���� � ������������� �������';}
if ($meal_section == 7){
$section_name_truth = '�������';}
if ($meal_section == 8){
$section_name_truth = '���� � ������������';}
if ($meal_section == 9){
$section_name_truth = '���� � ������������';}
if ($meal_section == 10){
$section_name_truth = '������������ �������';}
if ($meal_section == 11){
$section_name_truth = '��������';}
if ($meal_section == 12){
$section_name_truth = '������ � �������� ��������';}
if ($meal_section == 13){
$section_name_truth = '��������� � ������� ������������';}
if ($meal_section == 14){
$section_name_truth = '�����, ������, �����';}
if ($meal_section == 15){
$section_name_truth = '������� ����� � �������������';}
if ($meal_section == 16){
$section_name_truth = '������� ������';}
if ($meal_section == 17){
$section_name_truth = '����� ��� ��������';}
if ($meal_section == 18){
$section_name_truth = '�������, ������, �����';}
if ($meal_section == 19){
$section_name_truth = '�������� �������, ����������, ���������';}
if ($meal_section == 20){
$section_name_truth = '������������� ������';}
if ($meal_section == 21){
$section_name_truth = '���������� ������, �������� ��� ��������';}
if ($meal_section == 22){
$section_name_truth = '����������� ������������';}
echo '</big>)!<br>
��������� � ��� �������������� ����� �������� � <br>
����� "<span style="color: rgb(153, 51, 0);">', $section_name_truth, '</span>".<br>
      <br>';}
      }
      ?>
&nbsp;
      </div>
      </div>
&nbsp;<br>
      <br>
      <?php
      if ($num_rows_id==0 and $num_rows_id_in_store==0
      and $id!=0 and strlen($id)==13){
      echo '
����� �� �����-����� <big><big><span style="color: rgb(0, 0, 153);">', $id, '
      </span></big></big> ��� �� �������� ����� �������, ';
       echo '������� ���
������:<br><form action="Arrive_in_store.php" method="post">
        <table class="text" style="text-align: center; width: 90%;"
 align="center" border="1" cellpadding="2" cellspacing="2">
          <tbody>';}
                if ($num_rows_id==1 and $num_rows_id_in_store==0
      and $id!=0 and strlen($id)==13 and $nick!=""){
      echo '
����� �� �����-����� <big><big><span style="color: rgb(0, 0, 153);">', $id, '
      </span></big></big> ��� �������� ����� �������, ';
       echo '������� ���
������:<br><form action="Arrive_in_store.php" method="post">
        <table class="text" style="text-align: center; width: 90%;"
 align="center" border="1" cellpadding="2" cellspacing="2">
          <tbody>';}
                if ($num_rows_id==1 and $num_rows_id_in_store==1
      and $id!=0 and strlen($id)==13){
      echo '
����� �� �����-����� <big><big><span style="color: rgb(0, 0, 153);">', $id, '
      </span></big></big> ��� ������ � �������  ', $store_name, ' �����';
       echo '<br>�������������� ���
������:<br><form action="Arrive_in_store.php" method="post">
        <table class="text" style="text-align: center; width: 90%;"
 align="center" border="1" cellpadding="2" cellspacing="2">
          <tbody>';}
          
           if ($num_rows_id==0){
          echo '
                                 <tr>
              <td>&nbsp;��������:<br>
&nbsp;<input maxlength="35" size="35" class="inputbox" name="meal_name"><br>
              </td>
            </tr>
            <tr>
              <td>&nbsp;������������� (��):<br>
&nbsp;<input maxlength="15" size="15" class="inputbox"
 name="manufacturer"><br>
              </td>
            </tr>
            <tr>
              <td>&nbsp;��������:<br>
&nbsp;<textarea name="features" COLS=50 ROWS=8>
</textarea><br>
              </td>
            </tr>
                        <tr>
              <td>&nbsp;����� ����� � �����������,<br>
              ��� ����� �������� � ������:<br>
&nbsp;<input maxlength="5" size="5" class="inputbox" name="capacity"><br>
              </td>
            </tr>
            <tr>
              <td>&nbsp;����� ������ � �����������:<br>
&nbsp;<input maxlength="5" size="5" class="inputbox" name="weight"><br>
              </td>
            </tr>
            <tr>
              <td>&nbsp;�����, ���������� ���������, �����:<br>
&nbsp;<input maxlength="5" size="5" class="inputbox" name="size"><br>
              </td>
            </tr>';
            }
            if (($num_rows_id_in_store==0 or $num_rows_id_in_store==1)
            and $id!=0 and strlen($id)==13){
            echo '
            <tr>
              <td>&nbsp;����������������� � ��������', $store_name,':<br>
&nbsp;<input maxlength="5" size="5" class="inputbox" name="allocation"><br>
              </td>
            </tr>
            <tr>
              <td>&nbsp;���� � ��������', $store_name, ':<br>
&nbsp;<input maxlength="5" size="5" class="inputbox" name="price"><br>
              </td>
            </tr>
          </tbody>
        </table>
        <input src="okblue.gif" alt="Send It In!" align="absmiddle"
height="20" type="image" width="30"> </form>';}

 ?>
      <br>
      <br>
      <br>
      <br>
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
200<span style="font-weight: bold;">7</span>-2008 � e-da.com.ua �������
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
