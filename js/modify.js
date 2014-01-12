function changeTheta(u_id,increment){
if(u_id.length==0 || !u_id)
	return;
if(increment==true || increment==false){}else{return;}
$.ajax({
	type: "POST",
	url: "credentials/"+u_id,
	data:{i:increment}
}).done(function(x){

	if(x=="S"){
		window.alert("Done");
	}
	else if(x=="F"){
		window.alert("Not done");
	}
	else{
		window.alert(x);
	}
	});
}
