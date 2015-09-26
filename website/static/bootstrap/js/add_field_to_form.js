$('#select-to').change(function(){
	unselectItemArraySelect();
	$('#select-to option:selected').each( function() {
		var currentIndex = $(this)[0].index;
		arrSelected[currentIndex]['selected'] = true;
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