function incA(amount){if(amount.value<999){amount.value++
return(0)
}return(-1)}


function decA(amount){if(amount.value>0){amount.value--
return(0)
}return(-1)}

/*-------------------------------------------------------------------------*/
// Set DIV ID to hide
/*-------------------------------------------------------------------------*/

function my_hide_div(itm)
{
	if ( ! itm ) return;
	
	itm.style.display = "none";
}

/*-------------------------------------------------------------------------*/
// Set DIV ID to show
/*-------------------------------------------------------------------------*/

function my_show_div(itm)
{
	if ( ! itm ) return;
	
	itm.style.display = "";
}

/*-------------------------------------------------------------------------*/
// Change cell colour
/*-------------------------------------------------------------------------*/

function change_cell_color( id, cl )
{
	itm = my_getbyid(id);
	
	if ( itm )
	{
		itm.className = cl;
	}
}

/*-------------------------------------------------------------------------*/
// Toggle category
/*-------------------------------------------------------------------------*/

function togglecategory( fid, add )
{
	saved = new Array();
	clean = new Array();

	//-----------------------------------
	// Get any saved info
	//-----------------------------------
	
	if ( tmp = my_getcookie('collapseprefs') )
	{
		saved = tmp.split(",");
	}
	
	//-----------------------------------
	// Remove bit if exists
	//-----------------------------------
	
	for( i = 0 ; i < saved.length; i++ )
	{
		if ( saved[i] != fid && saved[i] != "" )
		{
			clean[clean.length] = saved[i];
		}
	}
	
	//-----------------------------------
	// Add?
	//-----------------------------------
	
	if ( add )
	{
		clean[ clean.length ] = fid;
		my_show_div( my_getbyid( 'fc_'+fid  ) );
		my_hide_div( my_getbyid( 'fo_'+fid  ) );
		my_show_div( my_getbyid( 'ftm_'+fid  ) );
		my_hide_div( my_getbyid( 'ftp_'+fid  ) );
		
	}
	else
	{
		my_show_div( my_getbyid( 'fo_'+fid  ) );
		my_hide_div( my_getbyid( 'fc_'+fid  ) );
		my_hide_div( my_getbyid( 'ftm_'+fid  ) );
		my_show_div( my_getbyid( 'ftp_'+fid  ) );
	}
	
	my_setcookie( 'collapseprefs', clean.join(','), 1 );
}


/*-------------------------------------------------------------------------*/
// Get cookie
/*-------------------------------------------------------------------------*/

function my_getcookie( name )
{
	cname = ssri_cookieid + name + '=';
	cpos  = document.cookie.indexOf( cname );
	
	if ( cpos != -1 )
	{
		cstart = cpos + cname.length;
		cend   = document.cookie.indexOf(";", cstart);
		
		if (cend == -1)
		{
			cend = document.cookie.length;
		}
		
		return unescape( document.cookie.substring(cstart, cend) );
	}
	
	return null;
}

/*-------------------------------------------------------------------------*/
// Set cookie
/*-------------------------------------------------------------------------*/

function my_setcookie( name, value, sticky )
{
	expire = "";
	domain = "";
	path   = "/";
	
	if ( sticky )
	{
		expire = "; expires=Wed, 1 Jan 2020 00:00:00 GMT";
	}
	
	if ( ssri_cookie_domain != "" )
	{
		domain = '; domain=' + ssri_cookie_domain;
	}
	
	if ( ssri_cookie_path != "" )
	{
		path = ssri_cookie_path;
	}
	
	document.cookie = ssri_cookieid + name + "=" + value + "; path=" + path + expire + domain + ';';
}

/*-------------------------------------------------------------------------*/
// Get element by id
/*-------------------------------------------------------------------------*/

function my_getbyid(id)
{
	itm = null;
	
	if (document.getElementById)
	{
		itm = document.getElementById(id);
	}
	else if (document.all)
	{
		itm = document.all[id];
	}
	else if (document.layers)
	{
		itm = document.layers[id];
	}
	
	return itm;
}
