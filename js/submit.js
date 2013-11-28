function submit(){
q=document.getElementById('q').value;
a1=document.getElementById('a1').value;
a2=document.getElementById('a2').value;
a3=document.getElementById('a3').value;
a4=document.getElementById('a4').value;
if(q.length==0 || a1.length==0 || a2.length==0 || a3.length==0 || a4.length==0){
	window.alert("Empty fields!");
	return;
}
$.ajax({
	type: "POST",
	url: "add",
	data:{q:q,a1:a1,a2:a2,a3:a3,a4:a4}
}).done(
	function(x){
		if(x=="S"){
			window.alert("Posted!");
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
