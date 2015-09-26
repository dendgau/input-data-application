$(".open-search-column").click(function(){
	var parent = $(this).parent(".parent-search-column");
	if (parent.hasClass("open1")){
		parent.removeClass("open1");
		parent.find(".search-column").hide();
		$(this).removeClass("blue");
	}else{
		$(".search-column").hide();
		$(".parent-search-column").removeClass("open1");
		$(".open-search-column").removeClass("blue");
		parent.addClass("open1");
		parent.find(".search-column").show();
		$(this).addClass("blue");
	}
	return false;
});

$(document).on( "click", function( event ) {
	if ($(".datepicker").find("[class='"+$(event.target).attr("class")+"']").length <= 0 &&
			$(".search-column").find("[class='"+$(event.target).attr("class")+"']").length <= 0) {
		$(".search-column").hide();
		$(".parent-search-column").removeClass("open1");
		$(".open-search-column").removeClass("blue");
	}else{
		return false;
	}
});

$(".th-search-column").click(function(){
	var openSearchColumn = $(this).find(".open-search-column");
	openSearchColumn.click();
	return false;
})

var isSortAsc = false,
	isSortDesc = false,
	isSearching = false,
	keyword = "",
	columnName = "";

$(".input-keyword-column").blur(function(){
	if (columnName == $(this).attr("columnname")) {
		if (keyword == $(this).val()) {
			return false;
		}else {
			if (!isSearching && $(this).val() == ""){
				return false;
			}
			$(this).val(keyword);
		}
	}else{
		if ($(this).val() == ""){
			return false;
		}
		$(this).val("");
	}
	alert("WARNING: Please press enter to search keyword in this column");
	return false;
});

$(".form-keyword-column").submit(function(){
	var input = $(this).find(".input-keyword-column"),
		_keyword = input.val(),
		lastResult = [];

	$("input.date-picker").val("");
	$(".type-title-date").removeClass("blue");
	$(".icon-select-date").hide();

	is_loading = true;
	if (columnName == $(this).attr("columnname")){
		if (keyword != ""){
			if (_keyword != ""){
				if (_keyword != keyword){
					if (isSortAsc){
						var arrAdvanceSearch = sortTextASC(items_search);
						lastResult = executeSearchColumn(arrAdvanceSearch, _keyword);
					}else if (isSortDesc){
						var arrAdvanceSearch = sortTextDESC(items_search);
						lastResult = executeSearchColumn(arrAdvanceSearch, _keyword);
					}else if (!isSortAsc && !isSortDesc){
						lastResult = executeSearchColumn(items_search, _keyword);
					}
					keyword = _keyword
				}else{
					return false;
				}
			}else{
				isSearching = false;
				keyword = "";
				if (isSortAsc) {
					lastResult = sortTextASC(items_search);
				}else if (isSortDesc){
					lastResult = sortTextDESC(items_search);
				}else if (!isSortAsc && !isSortDesc){
					is_loading = false;
					columnName = "";
					$(".tbody-origin").html(getTemplate(items_search));
					return false
				}
			}
		}else{
			if (_keyword != ""){
				if (isSortAsc) {
					var arrAdvanceSearch = sortTextASC(items_search);
					lastResult = executeSearchColumn(arrAdvanceSearch, _keyword);
				}else if (isSortDesc){
					var arrAdvanceSearch = sortTextDESC(items_search);
					lastResult = executeSearchColumn(arrAdvanceSearch, _keyword);
				}else if (!isSortAsc && !isSortDesc){
					lastResult = executeSearchColumn(items_search, _keyword);
				}
				keyword = _keyword
				isSearching = true;
			}else{
				return false;
			}
		}
	}else{
		if (_keyword != ""){
			isSortAsc = false;
			isSortDesc = false;

			isSearching = true;
			columnName = $(this).attr("columnname");
			keyword = _keyword;
			lastResult = executeSearchColumn(items_search, _keyword);

			$(".input-keyword-column").val("");
			$(this).find(".input-keyword-column").val(_keyword);
			disableAllSortCSS();
		}else{
			return false;
		}
	}
	$(".tbody-origin").html(getTemplate(lastResult));
	return false;
});

$(".a-sort-keyword").click(function(){
	var isSelected = $(this).hasClass("blue");
	$("input.date-picker").val("");
	$(".type-title-date").removeClass("blue");
	$(".icon-select-date").hide();
	disableAllSortCSS();
	if (!isSelected){
		activeSortCSS($(this));
	}
	executeSortColumn($(this), isSelected);
	return false;
});

function activeSortCSS(aCurrent){
	var iChild = aCurrent.children(".i-sort-keyword");
	aCurrent.addClass("blue");
	iChild.removeClass("invisible");
}

function disableAllSortCSS(){
	$(".a-sort-keyword").removeClass("blue");
	$(".i-sort-keyword").addClass("invisible");
}

function executeSortColumn(aCurrent, isSelected){
	if (columnName == aCurrent.attr("columnname")){
		var lastResult = [];
		var action = aCurrent.attr("action");
		is_loading = true;

		if (!isSelected) {
			var arrAdvanceSearch = items_search;
			if (isSearching) {
				arrAdvanceSearch = executeSearchColumn(items_search, keyword);
			}

			if (action == "sort-asc"){
				lastResult = sortTextASC(arrAdvanceSearch);
				isSortAsc = true;
				isSortDesc = false;
			}else if (action == "sort-desc"){
				lastResult = sortTextDESC(arrAdvanceSearch);
				isSortAsc = false;
				isSortDesc = true;
			}

			$(".tbody-origin").html(getTemplate(lastResult));
		}else{
			if (isSearching){
				lastResult  = executeSearchColumn(items_search, keyword);
				isSortAsc = false;
				isSortDesc = false;

				$(".tbody-origin").html(getTemplate(lastResult));
			}else{
				isSortAsc = false;
				isSortDesc = false;
				columnName = "";
				is_loading = false;

				$(".tbody-origin").html(getTemplate(items_search));
			}
		}
	}else{
		var action = aCurrent.attr("action");
		columnName = aCurrent.attr("columnname");

		$(".input-keyword-column").val("");
		isSearching = false;
		keyword = "";
		isSortAsc = false,
		isSortDesc = false,
		is_loading = true;

		if (action == "sort-asc"){
			lastResult = sortTextASC(items_search);
			isSortAsc = true;
			isSortDesc = false;
		}else if (action == "sort-desc"){
			lastResult = sortTextDESC(items_search);
			isSortAsc = false;
			isSortDesc = true;
		}
		$(".tbody-origin").html(getTemplate(lastResult));
	}
}

function sortTextASC(originArr){
	var arr = JSON.parse( JSON.stringify( originArr ) );
	if (columnName == "progress" || columnName == "real_size"){
		for (var i = 0; i < arr.length - 1; i++) {
			for (var j = i + 1; j < arr.length; j++) {
				var iInt = (arr[i][columnName]);
				var jInt = (arr[j][columnName]);
				if (iInt > jInt) {
					var temp = arr[i];
					arr[i] = arr[j];
					arr[j] = temp;
				}
			}
		}
	}else {
		for (var i = 0; i < arr.length - 1; i++) {
			for (var j = i + 1; j < arr.length; j++) {
				var indexStart = 0,
					indexEnd = ((arr[i][columnName]).length >= (arr[j][columnName]).length ? (arr[j][columnName]).length - 1 : (arr[i][columnName]).length - 1);

				do {
					var iString = (arr[i][columnName]).charAt(indexStart);
					var jString = (arr[j][columnName]).charAt(indexStart);
					if (iString > jString) {
						var temp = arr[i];
						arr[i] = arr[j];
						arr[j] = temp;
						break;
					} else if (iString < jString) break;
					indexStart += 1;
				} while (indexEnd >= indexStart);
			}
		}
	}
	return arr;
}

function sortTextDESC(originArr){
	var arr = JSON.parse( JSON.stringify( originArr ) );
	if (columnName == "progress" || columnName == "real_size"){
		for (var i = 0; i < arr.length - 1; i++) {
			for (var j = i + 1; j < arr.length; j++) {
				var iInt = (arr[i][columnName]);
				var jInt = (arr[j][columnName]);
				if (iInt < jInt) {
					var temp = arr[i];
					arr[i] = arr[j];
					arr[j] = temp;
				}
			}
		}
	}else {
		for (var i = 0; i < arr.length - 1; i++) {
			for (var j = i + 1; j < arr.length; j++) {
				var indexStart = 0,
					indexEnd = ((arr[i][columnName]).length >= (arr[j][columnName]).length ? (arr[j][columnName]).length - 1 : (arr[i][columnName]).length - 1);
				do {
					var iString = (arr[i][columnName]).charAt(indexStart);
					var jString = (arr[j][columnName]).charAt(indexStart);
					if (iString < jString) {
						var temp = arr[i];
						arr[i] = arr[j];
						arr[j] = temp;
						indexStart = indexEnd;
						break;
					} else if (iString > jString) break;
					indexStart += 1;
				} while (indexEnd >= indexStart);
			}
		}
	}
	return arr;
}

function executeSearchColumn(arr1, _keyword){
	var resultArr = [];
	var arr = JSON.parse( JSON.stringify( arr1 ) );
	for (var i=0; i<arr.length; i++){
		var strOrigin = (arr[i][columnName]).toLowerCase(),
			newKeyword = _keyword.toLowerCase(),
			indexStartSplit = strOrigin.indexOf(newKeyword);
		if (indexStartSplit > -1){
			var hightLightString = arr[i][columnName],
				hightLightString1 = [];
			hightLightString = hightLightString.split(_keyword);
			hightLightString1 =
			hightLightString = hightLightString.join("<strong style='background-color: yellow'>"+_keyword+"</strong>");
			arr[i][columnName] = hightLightString;
			resultArr.push(arr[i]);
		}
	}
	return resultArr;
}

$(".find_date_before").click(function(){
	is_loading = true;
	var ulParent = $(this).parents(".search-column");
	var liParent = $(this).parent(".li-datepicker");
	var inputPickDate = liParent.find(".date-picker");
	var dateSearch = new Date(inputPickDate.val());

	if (dateSearch != "Invalid Date"){
		disableAllSortCSS();
		isSortAsc = false;
		isSortDesc = false;
		isSearching = false;
		keyword = "";
		$(".input-keyword-column").val("");

		if (columnName != inputPickDate.attr("columnname")){
			$("input.date-picker").not(inputPickDate).val("");
			$(".type-title-date").removeClass("blue");
			$(".icon-select-date").hide();
		}

		ulParent.find("input.date-picker").not(inputPickDate).val("");
		ulParent.find(".type-title-date").removeClass("blue");
		ulParent.find(".icon-select-date").hide();
		liParent.find(".type-title-date").addClass("blue");
		liParent.find(".icon-select-date").show();
		columnName = inputPickDate.attr("columnname");
		var resultArr = [];
		var arr = JSON.parse( JSON.stringify( items_search ) );
		for (var i=0; i<arr.length; i++){
			var keywordDate = new Date(arr[i][columnName]);
			if (keywordDate < dateSearch){
				resultArr.push(arr[i]);
			}
		}
		$(".tbody-origin").html(getTemplate(resultArr));
	}else{
		$(".reset-date-time").click();
		inputPickDate.focus();
	}
	return false;
});

$(".find_on_date").click(function(){
	is_loading = true;
	var ulParent = $(this).parents(".search-column");
	var liParent = $(this).parent(".li-datepicker");
	var inputPickDate = liParent.find(".date-picker");
	var dateSearch = new Date(inputPickDate.val());

	if (dateSearch != "Invalid Date"){
		disableAllSortCSS();
		isSortAsc = false;
		isSortDesc = false;
		isSearching = false;
		keyword = "";
		$(".input-keyword-column").val("");

		if (columnName != inputPickDate.attr("columnname")){
			$("input.date-picker").not(inputPickDate).val("");
			$(".type-title-date").removeClass("blue");
			$(".icon-select-date").hide();
		}

		ulParent.find("input.date-picker").not(inputPickDate).val("");
		ulParent.find(".type-title-date").removeClass("blue");
		ulParent.find(".icon-select-date").hide();
		liParent.find(".type-title-date").addClass("blue");
		liParent.find(".icon-select-date").show();
		columnName = inputPickDate.attr("columnname");
		var resultArr = [];
			var arr = JSON.parse( JSON.stringify( items_search ) );
		for (var i=0; i<arr.length; i++){
			var keywordDate = new Date(arr[i][columnName]);
			if (keywordDate.getDate() == dateSearch.getDate() &&
			keywordDate.getMonth() == dateSearch.getMonth() &&
			keywordDate.getFullYear() == dateSearch.getFullYear()){
				resultArr.push(arr[i]);
			}
		}
		$(".tbody-origin").html(getTemplate(resultArr));
	}else{
		$(".reset-date-time").click();
		inputPickDate.focus();
	}
	return false;
});

$(".find_date_after").click(function(){
	is_loading = true;
	var ulParent = $(this).parents(".search-column");
	var liParent = $(this).parent(".li-datepicker");
	var inputPickDate = liParent.find(".date-picker");
	var dateSearch = new Date(inputPickDate.val());

	if (dateSearch != "Invalid Date"){
		disableAllSortCSS();
		isSortAsc = false;
		isSortDesc = false;
		isSearching = false;
		keyword = "";
		$(".input-keyword-column").val("");

		if (columnName != inputPickDate.attr("columnname")){
			$("input.date-picker").not(inputPickDate).val("");
			$(".type-title-date").removeClass("blue");
			$(".icon-select-date").hide();
		}

		ulParent.find("input.date-picker").not(inputPickDate).val("");
		ulParent.find(".type-title-date").removeClass("blue");
		ulParent.find(".icon-select-date").hide();
		liParent.find(".type-title-date").addClass("blue");
		liParent.find(".icon-select-date").show();
		columnName = inputPickDate.attr("columnname");
		var resultArr = [];
		var arr = JSON.parse( JSON.stringify( items_search ) );
		for (var i=0; i<arr.length; i++){
			var keywordDate = new Date(arr[i][columnName]);
			if (keywordDate > dateSearch){
				resultArr.push(arr[i]);
			}
		}
		$(".tbody-origin").html(getTemplate(resultArr));
	}else{
		$(".reset-date-time").click();
		inputPickDate.focus();
	}
	return false;
});

$(".reset-date-time").click(function(){
	if (columnName == $(this).attr("columnname")){
		var ulParent = $(this).parents(".search-column");
		is_loading = false;
		columnName = "";
		ulParent.find(".date-picker").val("");
		ulParent.find(".type-title-date").removeClass("blue");
		ulParent.find(".icon-select-date").hide();

		$(".tbody-origin").html(getTemplate(items_search));
		return false;
	}else{
		var ulParent = $(this).parents(".search-column");
		ulParent.find(".date-picker").val("");
	}
});