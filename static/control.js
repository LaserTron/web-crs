function upDate(){
    var msgbox=document.getElementById("message")
    switch(state){
    case "reload":
	history.go(0);
	msgbox.innerHTML=state;
	break;
    default:
	msgbox.innerHTML=state;
    }
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
	    if (state != "reload"){
		syncState();
	    }
	    upDate();
	}
    }
    stateReq.open("GET",qstring,true);
    stateReq.send();
}
