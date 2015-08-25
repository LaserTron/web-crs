function imgUpload(){
    var multi=document.getElementById("multibox");
    multi.innerHTML="<iframe style=\"width:100%\" height=\"400\" frameBorder=\"0\" src=\"/uploadImg/\"></iframe>";
}

function preview(ID){
    var multi=document.getElementById("multibox");
    multi.innerHTML="<iframe style=\"width:100%\" height=\"400\" frameBorder=\"0\" src=\"/viewQuestion/?ID="+ID+"\"></iframe>";
}
