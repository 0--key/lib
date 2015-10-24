<?php  
# Отсылаем заголовок который "обьясняет" клиенту ,что это wml документ  
header("Content-type: text/vnd.wap.wml");  
#Выводим саму страницу  
print  '  
<?xml version="1.0" encoding="cp1251"?>  
<!DOCTYPE wml PUBLIC "-//WAPFORUM//DTD WML 1.1//EN" "http://www.wapforum.org/DTD/wml_1.1.xml">  
';  
print  '  
<wml>  
<card id="id1" title="Card1">  
Hello! People This is My first wml  page!  
</card>  
</wml>  
';  
?>