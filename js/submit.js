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
