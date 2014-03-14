function submit(){
q=document.getElementById('q').value;
a1=document.getElementById('a1').value;
a2=document.getElementById('a2').value;
a3=document.getElementById('a3').value;
a4=document.getElementById('a4').value;
c1=document.getElementById('c1').checked;
c2=document.getElementById('c2').checked;
c3=document.getElementById('c3').checked;
c4=document.getElementById('c4').checked;
if(q.length==0 || a1.length==0 || a2.length==0 || a3.length==0 || a4.length==0){
	window.alert("Empty fields!");
	return;
}
$.ajax({
	type: "POST",
	url: "add",
	data:{q:q,a1:a1,a2:a2,a3:a3,a4:a4,c1:c1,c2:c2,c3:c3,c4:c4}
}).done(
	function(x){
		if(x=="S"){
			window.alert("Posted!");
			document.getElementById('a1').value
			=document.getElementById('a2').value
			=document.getElementById('a3').value
			=document.getElementById('a4').value
			=document.getElementById('q').value
			=""
			return;
		}
		if(x=="F"){
			window.alert("Failed");
			return;
		}
		else{
			window.alert("x:"+x);
		}
	});
}
var a_key="";
function setAnswer(k){
	a_key=k;
}
function submitAnswer(){
k=a_key;
if(k.length==0 || k==0){ //one should actually validate using regexp TODO
	window.alert("Cannot submit such a null answer");
	return;
}else{
	$.ajax({
		type: "POST",
		url: document.location.pathname,
		data: {answer:k}
	}).done(function(x){
				if(x=="S"){
					window.alert("Answered successfully");
				}
				else if(x=="R"){
					window.alert("You've already answered this once");
				}
				else if(x=="F"){
					window.alert("Failed.. for some reason.");
				}
				else{
					window.alert("x="+x);
				}
				
	});
}
}

function submitEvalAnswer(q_key){
k=a_key;
if(k.length==0 || k==0){ //one should actually validate using regexp TODO
	window.alert("Cannot submit such a null answer");
	return;
}else{
	$.ajax({
		type: "POST",
		url: document.location.pathname+"/"+q_key,
		data: {answer:k}
	}).done(function(x){
				if(x=="S"){
					document.location.reload()
				}
				else if(x=="R"){
					window.alert("You've already answered this once");
				}
				else if(x=="F"){
					window.alert("Failed.. for some reason.");
				}
				else{
					window.alert("x="+x);
				}
				
	});
}
}
