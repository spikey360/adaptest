function fetchKhi(q_id,a,b){
if(q_id.length==0 || q_id==0){
	window.alert("Invalid question id");
	return;
}else{
	$.ajax({
		type: "GET",
		url: "../computation/getkhi/"+q_id,
		data:{a:a,b:b}
	}).done(function(x){
		window.alert(x);
		return x;
	});
}
}

var start_a=0.0;
var start_b=0.0;
var end_a=1.0;
var end_b=10.0;

function aggregateKhi(q_id,a_step,b_step){
z=""
if(q_id.length==0 || q_id==0){
	window.alert("Invalid question id");
	return;
}else{
	for(;start_a<=end_a;start_a+=a_step){
		for(;start_b<=end_b;start_b+=b_step){
			z+=fetchKhi(q_id,start_a,start_b)+" ";
		}
		z+="\n";
	}
	document.getElementById('x').value=z;
}
}

