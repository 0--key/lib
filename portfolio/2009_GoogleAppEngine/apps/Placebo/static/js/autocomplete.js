/**
 * @author gemini
 */
 
 $(document).ready(function(){
 	
 	$('input[name=concept]').autocomplete({
 		source: '/autocomplete/?name=concept',
 		minLength: 2,
 	});
 	
 	 $('input[name=category]').autocomplete({
 		source: '/autocomplete/?name=category',
 		minLength: 2,
 	});
 	
 	 $('input[name=taxonomy]').autocomplete({
 		source: '/autocomplete/?name=taxonomy',
 		minLength: 2,
 	});
 })
