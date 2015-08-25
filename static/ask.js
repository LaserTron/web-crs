function clickChoice(ans)
{
    // This function will send the student
    // selection to the server and change the element style
    // to reflect the current state in the database.
    var ansurl = "/submit/"+ans;
    var ansdiv = document.getElementById(ans);
    var response;

    var ansTrans=new XMLHttpRequest();
        ansTrans.onreadystatechange=function()
    {
	if (ansTrans.readyState==4 && ansTrans.status==200){
	    var response = ansTrans.responseText;
	    switch(response){//This updates the response
	    case "1":
		ansdiv.style.background="LightGreen";
		break;
	    case "0":
		ansdiv.style.background="#FFCCCC";
		break;
	    default:
		ansdiv.innerHTML=response;
	    }
	    
	}
    }//END CALLBACK
    ansTrans.open("GET",ansurl,true);
    ansTrans.send();
}

function setTimer(time)
{
    var timeurl = "/setTimer/?time="+time;
    var timeReq=new XMLHttpRequest();
    timeReq.open("GET",timeurl,true);
    timeReq.send();
}
