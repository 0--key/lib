<?php 
echo "(<a href=encode.php>шифровка</a> | <a href=decode.php>расшифровка</a>)
</center><hr>"; 

if(empty($_POST['text'])) 
echo 
"<form method=post> 
<center> 
<textarea name=text cols=50 rows=20></textarea> 
<br><br><input type=submit value=Расшифровать> 
</center> 
</form>"; 

else 
{ 
$array=explode(chr(50),$_POST['text']); 
$decoded=null; 

    while(list(,$char)=each($array)) 
    $decoded.=chr(base_convert($char,2,10)); 

echo "Результат расшифровки:<hr><font style=background-color:#f2f2f2>"
.HtmlSpecialChars($decoded)."</font>"; 
} 
?>
