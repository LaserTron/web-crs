function upDate(){
   var subBut=document.getElementById("subButt")
   if (state == "closed"){
	subBut.style.visibility = "hidden";
   }
   else{
	subBut.style.visibility = "visible";
   }
}


function syncState()
{
    var qstring = "/comet/"+state;
    var stateReq;
    stateReq=new XMLHttpRequest();
    
    stateReq.onreadystatechange=function()
    {
	if (stateReq.readyState==4 && stateReq.status==200)
	{
	    var response = stateReq.responseText;
	    state = response;
	    syncState();
	    upDate();
	}
    }
    stateReq.open("GET",qstring,true);
    stateReq.send();
}
