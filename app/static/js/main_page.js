function main() {



	$(".submit-button").on("click", function(){
		var counterData = {
							"sn": "13817406", 
							"data": [
								{
									"readout_dt": "1465193586", 
									"id": "881", 
									"counters": [
										{
											"val": "2877", 
											"n": "1"
										}, {
											"val": "2237", 
											"n": "2"
										}
									]
								}, {
									"readout_dt": "1465197765", 
									"id": "882", 
									"counters": [
										{
											"state": "0", 
											"val": "2878", 
											"n": "1"
										}, {
											"state": "1", 
											"val": "2238", 
											"n": "2"
										}
									]
								}
							]
						}
		$.ajax({
 			url: '/datareceiver',
 			type: 'POST',
 			contentType: "application/json; charset=ascii",			
 			data: JSON.stringify(counterData),
 			
 			success: function(response) {
 			},
 			error: function(error) {
 			}
 		});
	});
}

$(document).ready(main)