$('#select-to').change(function(){
	unselectItemArraySelect();
	$('#select-to option:selected').each( function() {
		var currentIndex = $(this)[0].index;
		arrSelected[currentIndex]['selected'] = true;
	});
});
$('#btn-add').click(function(){
	unselectItemArraySelect();
	$('#select-to option:selected').each( function() {
		$(this)[0].selected = false
	});

	$('#select-from option:selected').each( function() {
		arrSelected.push({
			'name': $(this).text(),
			'value': $(this).val(),
			'selected': true
		});
		$('#select-to').append("<option selected value='"+$(this).val()+"' name='" + $(this).val()+"'>"+$(this).text()+"</option>");
		$(this).remove();
	});
});
$('#btn-remove').click(function(){
	$('#select-to option:selected').each( function() {
		$('#select-from').append("<option value='"+$(this).val()+"' name='" + $(this).val()+"'>"+$(this).text()+"</option>");
		var currentIndex = $(this)[0].index;
		arrSelected.splice(currentIndex, 1);
		$(this).remove();
	});
});
$('#btn-up').click(function(){
	$('#select-to option:selected').each( function() {
		var currentIndex = $(this)[0].index,
			minIndex = 0;

		if (currentIndex > minIndex && !checkNearByExceptionUp(currentIndex)){
			var temp = arrSelected[currentIndex - 1];
			arrSelected[currentIndex - 1] = arrSelected[currentIndex];
			arrSelected[currentIndex] = temp;
		}
	});

	removeItemSelectToHTML();
	renderItemArraySelect();

	return false;
});

$('#btn-down').click(function(){
	$($('#select-to option:selected').get().reverse()).each( function() {
		var currentIndex = $(this)[0].index,
			maxIndex = $('#select-to option').length;

		if (currentIndex < maxIndex && !checkNearByExceptionDown(currentIndex, maxIndex)){
			var temp = arrSelected[currentIndex + 1];
			arrSelected[currentIndex + 1] = arrSelected[currentIndex];
			arrSelected[currentIndex] = temp;
		}
	});

	removeItemSelectToHTML();
	renderItemArraySelect();

	return false;
});

function checkNearByExceptionUp(currentIndex){
	for (var n = (currentIndex - 1); n >= 0; n--){
		if (!arrSelected[n]["selected"]) {
			return false;
		}
	}
	return true;
}

function checkNearByExceptionDown(currentIndex, maxIndex){
	for (var n = (currentIndex + 1); n < maxIndex; n++){
		if (!arrSelected[n]["selected"]) {
			return false;
		}
	}
	return true;
}

function renderItemArraySelect(){
	for (var n = 0; n < arrSelected.length; n++){
		if (arrSelected[n]["selected"]) {
			$('#select-to').append("<option selected value='"+arrSelected[n]["value"]+"' name='"+arrSelected[n]["value"]+"'>"+arrSelected[n]["name"]+"</option>");
		} else {
			$('#select-to').append("<option value='"+arrSelected[n]["value"]+"' name='"+arrSelected[n]["value"]+"'>"+arrSelected[n]["name"]+"</option>");
		}
	}
}

function unselectItemArraySelect(){
	for (var n = 0; n < arrSelected.length; n++){
		arrSelected[n]["selected"] = false;
	}
}

function removeItemSelectToHTML(){
	$('#select-to option').each( function() {
		$(this).remove();
	});
}

function selectAll() {
	var formSubmit = $(".button-submit").parents("form");
	$(".button-submit").attr("disabled", true);
	$(".loading-span").show();


	selectBox = document.getElementById("select-to");
	for(var i = 0; i < selectBox.options.length; i++)
	{
		 selectBox.options[i].selected = true;
	}
	notselectBox = document.getElementById("select-from");
	for(var i = 0; i < notselectBox.options.length; i++)
	{
		notselectBox.options[i].selected = false;
	}

	formSubmit.submit();
}

$(".btn-delete").click(function(){
	var rediredt_url = $(this).attr("href");
	$(this).attr("disabled", true);
	$(".loading-span").show();
	window.location.href = rediredt_url;
	return false;
});