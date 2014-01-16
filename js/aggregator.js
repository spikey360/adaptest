function fetchKhi(q_id,a,b,khi_x,khi_y){
if(q_id.length==0 || q_id==0){
	window.alert("Invalid question id");
	return;
}else{
	$.ajax({
		type: "GET",
		url: "../computation/getkhi/"+q_id,
		data:{a:a,b:b}
	}).done(function(x){
		//return won't function properly since this is an async call
		//so, update with this value when call finishes
		khis[khi_x][khi_y]=parseFloat(x);
		done++;
	});
}
}
var mp_a=0.0;
var mp_b=0.0; //most probable, calculated after getting minimum χ
var start_a=0.0;
var start_b=0.0;
var end_a=1.0;
var end_b=10.0;
var aq=0.0, bq=0.0; //quanta
var khis=null;
var c=0; var d=0; //array index counters
var done=0; var total=0;
function aggregateKhi(q_id,a_step,b_step){
khis=new Array(); aq=a_step; bq=b_step;
total=((end_a-start_a)/a_step+1)*((end_b-start_b)/b_step+1); //+1 cause <= is given
if(q_id.length==0 || q_id==0){
	window.alert("Invalid question id");
	return;
}else{
	for(i=start_b;i<=end_b;i+=b_step){
		khis[c]=new Array()
		for(j=start_b;j<=end_a;j+=a_step){
			fetchKhi(q_id,j,i,c,d++);
		}
		d=0;c++;
	}

}
}

function getMinimumKhi(){
min_yet=khis[0][0];
for(i=0;i<khis.length;i++){
	for(j=0;j<khis[i].length;j++){
		if(khis[i][j]<min_yet){
			min_yet=khis[i][j];
			mp_a=j*aq; mp_b=i*bq;
		}
	}
}
return min_yet;
}

function tryEstimating(){
if(done!=total){
	document.getElementById('result').innerHTML="Working... "+done+"/"+total;
	window.setTimeout('tryEstimating()',100);
	return;
	}
	else{
		mk=getMinimumKhi();
		document.getElementById('result').innerHTML="<b>a</b>:"+mp_a+", <b>b</b>:"+mp_b+", c:0.25";
	}

}

function estimateParams(q_id,quant_a,quant_b){
quant_a=parseFloat(document.getElementById('quanta_a').value);
quant_b=parseFloat(document.getElementById('quanta_b').value);
aggregateKhi(q_id,quant_a,quant_b);
document.getElementById('result').innerHTML="Working...";
tryEstimating();
}
