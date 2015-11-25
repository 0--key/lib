<?php 
echo "<center>(<a href=encode.php>шифровка</a> | <a href=decode.php>расшифровка</a>)
</center><hr>"; 

if(empty($_POST['text'])) 
echo 
"<form method=post> 
<center> 
<textarea name=text cols=50 rows=20></textarea> 
<br><br><input type=submit value=Зашифровать> 
</center> 
</form>"; 

else 
{ 
$_POST['text']=StripSlashes($_POST['text']); 
$size=StrLen($_POST['text']); 
$encoded=null; 

    for($i=0;$i<$size;$i++) 
    $encoded.=base_convert(ord($_POST['text'][$i]),10,2).chr(50); 

echo "Результат шифровки:<hr><center><textarea cols=50 rows=20>"
.$encoded."</textarea></center>"; 
} 
?>
