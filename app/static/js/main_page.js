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
 			contentType: "application/json; charset=utf-8",			
 			data: JSON.stringify(counterData),
 			
 			success: function(response) {
 				console.log(response);
 			},
 		});	
	});

	$(".show-log-btn").on("click", function(){
		var filename = $(this).attr("data-target") + ".log"
		var thisLogArea = $(this).siblings(".log-container").children(".log-area");
		if($(this).siblings(".log-container").css("display") == "none"){
			$.ajax({
	 			url: '/getlog',
	 			type: 'POST',
	 			contentType: "application/json; charset=utf-8",			
	 			data: JSON.stringify(filename),
 			
	 			success: function(response) {
	 				//console.log(response);
	 				$(".control").html(response['control'])
	 				$(thisLogArea).html(response['log']);
	 			},
 			});	
		}
		
		$(this).siblings(".show-log-text").toggle();
		$(this).siblings(".hide-log-text").toggle();
		$(this).siblings(".log-container").slideToggle();
 	});

 	$("#refresh-error").on("click", function() {
 		user_request = {}
 		if ($("#is-today").prop("checked")) {
 			var now = new Date();
 			var dt = [now.getFullYear(), now.getMonth() + 1, now.getDate()].join("-");
 		} else {
 			dt = String($("#user-date").val());
 		}
 		if (!dt) 
 			return false;
 		user_request["date"] = dt;

 		var errors = new Array();
 		var num_of_types = 0;
 		$(".type-of-error").each(function(){
 			num_of_types ++;
 			if ($(this).prop("checked")) {
 				errors.push($(this).parent().text().trim());
 			}
 		});
 		num_of_types /= 2;
 		var l = errors.length - num_of_types;
 		errors = errors.slice(0, l);

 		user_request["errors"] = errors;

 		$.ajax({
	 			url: '/errorlogfilter',
	 			type: 'POST',
	 			contentType: "application/json; charset=utf-8",			
	 			data: JSON.stringify(user_request),
 			
	 			success: function(response) {
	 				$("#error-log-container .log-area").html(response['log']);
	 			},
 			});

 	});
 	$("#is-today:checkbox").on('change', function() {
		if ($('#user-date').attr('disabled')) {
        	$('#user-date').removeAttr('disabled');
    	} else {
        	$('#user-date').attr('disabled', 'disabled');
    	}
	});
}

$(document).ready(main)