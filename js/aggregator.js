function fetchParams(q_id){
if(q_id.length==0 || q_id==0){
	window.alert("Invalid question id");
	return;
}else{
	$.ajax({
		type: "GET",
		url: "../computation/getkhi/"+q_id
	}).done(function(x){
		//return won't function properly since this is an async call
		//so, update with this value when call finishes
		if(x=="F"){
			window.alert("Failed")
		}
		else{
		m=x.split(',');
		document.getElementById('result').innerHTML="<b>a</b>:"+m[0]+", <b>b</b>:"+m[1]+", <b>c</b>:"+m[2];
		}
	});
}
}

