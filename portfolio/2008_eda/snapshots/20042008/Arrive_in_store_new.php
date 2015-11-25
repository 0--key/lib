<?php
session_start();
//include (functions/Text.inc)
if($_SESSION['nick']!="" and $_SESSION['auth']=='correct'){
        
// nick - real indentificator in the system
//if($_SESSION['reverse']==$_SESSION['id']){
//echo "You're inputted this id!!! ";
//}
//else {
// Проверим введённые пользователем данные
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
    
    // переменные уже готовы к обработке для проверки правильности
    

// Вставим тело MySQL сюда:


//}

//else echo "Wrong input of the meal id!";
}
else echo "You're must authentificate on the first page!";
?>