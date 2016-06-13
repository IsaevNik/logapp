function main() {
	// Submit counter data to '/datareceiver' url and load response
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
	// Reset controle form of error log.
	function resetErrorControle(controlElement){
		$(controlElement).find('input:checkbox').each(function(){
			$(this).prop("checked", true);
		});
		$(controlElement).find('input.form-control').each(function(){
			$(this).val("");
			$(this).attr('disabled', 'disabled');
		});
	}
	// Reset controle form of request log.
	function resetRequestControle(controlElement){
		$(controlElement).find('.ch:checkbox').each(function(){
			$(this).prop("checked", true);
		});
		$(controlElement).find('.unch:checkbox').each(function(){
			$(this).prop("checked", false);
		});
		$(controlElement).find('input.form-control').each(function(){
			$(this).val("");
			$(this).attr('disabled', 'disabled');
		});
	}

	/* Send ajax request to server with information about what kind of 
	log user want to open if user click a button when log is open - close
	log, and reset controle panel*/
	$(".show-log-btn").on("click", function(){
		var filename = $(this).attr("data-target");
		var thisLogArea = $(this).siblings(".log-container").children(".log-area");
		var thisControlArea = $(this).siblings(".log-container").find(".control")
		if($(this).siblings(".log-container").css("display") == "none"){
			$.ajax({
	 			url: '/getlog',
	 			type: 'POST',
	 			contentType: "application/json; charset=utf-8",			
	 			data: JSON.stringify(filename),
 			
	 			success: function(response) {
	 				$(thisControlArea).html(response['control'])
	 				$(thisLogArea).html(response['log']);
	 			},
 			});	
		} else {
			var controlElement = $(this).siblings(".log-container").first();
			if (filename == "errors")
				resetErrorControle(controlElement);
			else
				resetRequestControle(controlElement);
		}
		$(this).siblings(".show-log-text").toggle();
		$(this).siblings(".hide-log-text").toggle();
		$(this).siblings(".log-container").slideToggle();
		
 	});
	// Make able or desable input fild depending on the apropriate checkbox
	$("input:checkbox").on('change', function() {
 		var thisInput = $(this).parents(".checkbox").next().next();
		if ($(thisInput).attr('disabled')) {
        	$(thisInput).removeAttr('disabled');
    	} else {
        	$(thisInput).attr('disabled', 'disabled');
    	}
	});
	/* Send to server ajax request with information about user choice 
	and display filtered error log*/
 	$("#refresh-error").on("click", function() {
 		var user_request = {}
 		if ($("#is-today").prop("checked")) {
 			var now = new Date();
 			var dt = [now.getFullYear(), now.getMonth() + 1, now.getDate()].join("-");
 		} else {
 			dt = String($("#user-date").val());
 		}
 		if (!dt) 
 			return false;
 		user_request["date"] = dt;

 		if ($('#is-all-errors').prop("checked")) {
 			user_request["errors"] = "";
 		} else {
 			user_request["errors"] = $("#user-choise-error").val();
 			if (!user_request["errors"])
 				return false;
 		}
 		
 		$.ajax({
	 			url: '/errorlogfilter',
	 			type: 'POST',
	 			contentType: "application/json; charset=utf-8",			
	 			data: JSON.stringify(user_request),
 			
	 			success: function(response) {
	 				$("#error-log-container .log-area").html(response['log']);
	 				$("#error-log-container .control").html(response['control'])
	 			},
 			});

 	});
 	/* Send to server ajax request with information about user choice 
	and display filtered request log*/
 	$("#refresh-request").on("click", function() {
		var user_request = {};
		if ($("#is-all-ip").prop("checked")) {
			user_request['ip'] = ""
		} else {
			user_request['ip'] = $("#user-choise-ip").val()
			if (!user_request["ip"])
 				return false;
		}
		if ($("#is-day-request").prop("checked")) {
			user_request['request_date'] = $("#user-date-request").val()
			if (!user_request["request_date"])
 				return false;
		} else {
			user_request['request_date'] = ""
			
		}
		if ($("#is-all-sn").prop("checked")) {
			user_request['sn'] = ""
		} else {
			user_request['sn'] = $("#user-choise-sn").val()
			if (!user_request["sn"])
 				return false;
		}
		if ($("#is-someday").prop("checked")) {
			user_request['start_date'] = $("#from-start-date").val()
			if (!user_request["start_date"])
 				return false;
		} else {
			user_request['start_date'] = ""
			
		}
		$.ajax({
	 			url: '/requestlogfilter',
	 			type: 'POST',
	 			contentType: "application/json; charset=utf-8",			
	 			data: JSON.stringify(user_request),
 			
	 			success: function(response) {
	 				$("#request-log-container .log-area").html(response['log']);
	 			},
 			});
 	});
}

$(document).ready(main)