function upDate(){
    if (!isNaN(state)){/*Works if true*/
	var msgbox=document.getElementById("message");
	msg = "Time left:"+state+" seconds";
	msgbox.innerHTML=msg;
    }
    if (state =="-1"){
	window.location="/conduct/?action=closed";
    }
    /*else if (state != initstate && isNaN(state)){
	history.go(0);
    }*/
}


function syncState()
{
    var qstring = "/comet/?state="+state+"&page="+page;
    var stateReq;
    stateReq=new XMLHttpRequest();
    
    stateReq.onreadystatechange=function()
    {
	if (stateReq.readyState==4 && stateReq.status==200)
	{
	    var response = stateReq.responseText;
	    state = response;
	    if (state == "open" || !isNaN(state)){
		syncState();/* This is what makes the client-side loop*/
	    }
	    upDate();
	}
    }
    stateReq.open("GET",qstring,true);
    stateReq.send();
}
