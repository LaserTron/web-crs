function upDate(){
    if (state != initstate){
	history.go(0);
    }
    
    var msgbox=document.getElementById("message");
    msgbox.innerHTML=state;
    
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
	    if (state == initstate){
		syncState();/* This is what makes the client-side loop*/
	    }
	    upDate();
	}
    }
    stateReq.open("GET",qstring,true);
    stateReq.send();
}
