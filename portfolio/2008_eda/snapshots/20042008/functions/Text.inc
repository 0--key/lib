<?php
function str_good($string, $lenght){
$string = substr($string, 0, $lenght);
$string = preg_replace("/[^\w\x7F-\xFF\s]/", " ", $string);
return $string;
}

function str_good_num($string, $lenght){
$string = substr($string, 0, $lenght);
$string = $string/100*100;//preg_replace("/[^\w\x7F-\xFF\sA-z]/", " ", $string);
//$string = ereg_replace("A-z", " ", $string);
return $string;
}

function mysql_run(){

    // Connecting, selecting database
$link = mysql_connect('localhost', 'edacomua_toxa', 'musiqpusiq')
    or die('Could not connect: ' . mysql_error());
echo 'Connected successfully';
mysql_select_db('edacomua_meal_store') or die('Could not select database');

// Performing SQL query
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
return $link;
}


function mysql_cyr(){
mysql_query ("set character_set_client='cp1251'"); 
mysql_query ("set character_set_results='cp1251'"); 
mysql_query ("set collation_connection='cp1251_general_ci'");
}

function get_section_name($section_code){
if ($section_code == 1){
$section_name = '������ �� ����������� �����';}
if ($section_code == 2){
$section_name = '����������� �������';}
if ($section_code == 3){
$section_name = '�������� � �����';}
if ($section_code == 4){
$section_name = '�������������� �������';}
if ($section_code == 5){
$section_name = '���, ����, �����';}
if ($section_code == 6){
$section_name = '���� � ������������� �������';}
if ($section_code == 7){
$section_name = '�������';}
if ($section_code == 8){
$section_name = '���� � ������������';}
if ($section_code == 9){
$section_name = '���� � ������������';}
if ($section_code == 10){
$section_name = '������������ �������';}
if ($section_code == 11){
$section_name = '��������';}
if ($section_code == 12){
$section_name = '������ � �������� ��������';}
if ($section_code == 13){
$section_name = '��������� � ������� ������������';}
if ($section_code == 14){
$section_name = '�����, ������, �����';}
if ($section_code == 15){
$section_name = '������� ����� � �������������';}
if ($section_code == 16){
$section_name = '������� ������';}
if ($section_code == 17){
$section_name = '����� ��� ��������';}
if ($section_code == 18){
$section_name = '�������, ������, �����';}
if ($section_code == 19){
$section_name = '�������� �������, ����������, ���������';}
if ($section_code == 20){
$section_name = '������������� ������';}
if ($section_code == 21){
$section_name = '���������� ������, �������� ��� ��������';}
if ($section_code == 22){
$section_name = '����������� ������������';}
if ($section_code < 1 or $section_code > 22){
$section_name = 'wrong';}
return $section_name;}
?>