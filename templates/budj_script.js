//Jaascript file

//window.addEventListener("DOMContentLoaded",hideAllCFData,true);

function show_data(cfID)
{
//this script will generate all data for the particular cashflow 
//when clicked it will generate and show all of the hidden data points for that item
	var list=document.getElementById(cfID);
	
	if (list.style.display=="none")
	{
	    list.style.display = "block";
	}
	else
	{
	    list.style.display = "none";
	}	
}

function hideAllCFData() {

    var cfS = document.getElementsByClassName("cfData");
    for (cf in cfS) {
        alert("A");
    }
}

//tryign to get this element id/class thing to work so I can hide everything on startup
