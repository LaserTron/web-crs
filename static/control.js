function upDate(){
    if (!isNaN(state)){/*Works if true*/
	var msgbox=document.getElementById("message");
	msg = "<strong>Time left:"+state+" seconds</strong>";
	msgbox.innerHTML=msg;
    }
    else if (state != initstate && isNaN(state)){
	/*history.go(0); THIS COMMAND DOESN'T WORK FOR FIREFOX*/
	/*Thanks: http://stackoverflow.com/questions/1536900/force-a-page-refresh-using-javascript-in-firefox*/
	window.location.href = "/" + "?" + Date.parse(new Date());
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
	    if (state == initstate || !isNaN(state)){
		syncState();/* This is what makes the client-side loop*/
	    }
	    upDate();
	}
    }
    stateReq.open("GET",qstring,true);
    stateReq.send();
}
