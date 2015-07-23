// var answerString;
// function updateAnswers(){
//     var answerStack = [];
//     var nonAnswers = [];
//     check = document.getElementsByName("ansChoice");
//     for (var c = 0; c < check.length;c++){
// 	var ans = check[c].value;
// 	if(check[c].checked){
// 	    answerStack .push(ans);
// 	}//if selected
// 	else{
// 	    nonAnswers .push(ans);
// 	}
//     }//forloop
//     nonAnswers = nonAnswers .join("/");
//     answerStack = answerStack .join("/");
//     answerString = answerStack + "/XXX/"+nonAnswers;
    
// }

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
		ansdiv.style.background="Yellow";
		break;
	    case "0":
		ansdiv.style.background="White";
		break;
	    default:
		ansdiv.innerHTML=response;
	    }
	    
	}
    }//END CALLBACK
    ansTrans.open("GET",ansurl,true);
    ansTrans.send();
}

// function sendAnswer()
// {
//     var qstring = "/submit/"
//     var ansTrans;
//     ansTrans=new XMLHttpRequest();
    
//     ansTrans.onreadystatechange=function()
//     {
// 	if (ansTrans.readyState==4 && ansTrans.status==200){
// 	    var response = ansTrans.responseText;
// 	    document.getElementById("debug").innerHTML=response;
// 	}
//     }
//     qstring=qstring+answerString;
//     ansTrans.open("GET",qstring,true);
//     ansTrans.send();
// }

// function buttonizer(){
//     updateAnswers();
//     sendAnswer();
// }
