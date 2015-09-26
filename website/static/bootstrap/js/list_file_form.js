$(window).scroll(function() {
	if($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
		if (!is_loading && has_next){
			var action = location.href;
			action = action.split("?")[0];
			action += "?q="+encodeURIComponent(q)+"&page="+next_page;
			is_loading = true;
			$(".loading-span").show();
			$.ajax({
				url: action,
				type: "GET",
				success: function (data) {
					var items = data.items;
					var html = "";
					for(var i=0; i<items.length; i++){
						counter += 1;
						html += "<tr>"+
							"<td><a href='/processing/input_data?fileupload_id="+items[i]["id"]+"&form_id="+items[i]["form_id"]+"'>"+items[i]["name"]+"</td>"+
							"<td style='text-align: center'>";
							if (items[i]["is_exist_file_tiff"]) {
								if (items[i]["is_finish_process"]) {
									html += '<div class="progress" data-percent="' + items[i]["file_process"] + '">' +
										'<div class="progress-bar" style="width:' + items[i]["progress"] + '%; background-color: #337ab7"></div>' +
									'</div>';
								} else {
									html += '<div class="progress" data-percent="' + items[i]["file_process"] + '">' +
										'<div class="progress-bar" style="width:' + items[i]["progress"] + '%; background-color: #d9534f"></div>' +
									'</div>';
								}
							}else{
								html+="<span class='red'><i class='icon-warning-sign'></i> "+items[i]["file_process"]+"</span>";
							}
							html+="</td>"+
							"<td style='text-align: justify'>"+items[i]["note"]+"</td>"+
							"<td style='text-align: center'>"+items[i]["form"]+"</td>"+
							"<td style='text-align: center'>"+items[i]["size"]+"</td>"+
							"<td style='text-align: center'><span class='label'>"+items[i]["upload_date"]+"</span></td>"+
							"<td style='text-align: center'><span class='label'>"+items[i]["process_date"]+"</span></td>"+
						"</tr>";
						items_search.push(items[i]);
					}
					is_loading = false;
					has_next = data.has_next
					next_page = data.next_page
					setTimeout(function(){
						$(".tbody-origin").append(html);
						$(".loading-span").hide();
					}, 300);
				}
			});
		}
	}
});

function getTemplate(items){
	var html = "";
	for(var i=0; i<items.length; i++){
		counter += 1;
		html += "<tr>"+
			"<td><a href='/processing/input_data?fileupload_id="+items[i]["id"]+"&form_id="+items[i]["form_id"]+"'>"+items[i]["name"]+"</td>"+
			"<td style='text-align: center'>";
			if (items[i]["is_exist_file_tiff"]) {
				if (items[i]["is_finish_process"]) {
					html += '<div class="progress" data-percent="' + items[i]["file_process"] + '">' +
						'<div class="progress-bar" style="width:' + items[i]["progress"] + '%; background-color: #337ab7"></div>' +
					'</div>';
				} else {
					html += '<div class="progress" data-percent="' + items[i]["file_process"] + '">' +
						'<div class="progress-bar" style="width:' + items[i]["progress"] + '%; background-color: #d9534f"></div>' +
					'</div>';
				}
			}else{
				html+="<span class='red'><i class='icon-warning-sign'></i> "+items[i]["file_process"]+"</span>";
			}
			html+="</td>"+
			"<td style='text-align: justify'>"+items[i]["note"]+"</td>"+
			"<td style='text-align: center'>"+items[i]["form"]+"</td>"+
			"<td style='text-align: center'>"+items[i]["size"]+"</td>"+
			"<td style='text-align: center'><span class='label'>"+items[i]["upload_date"]+"</span></td>"+
			"<td style='text-align: center'><span class='label'>"+items[i]["process_date"]+"</span></td>"+
		"</tr>";
	}
	return html;
}

$("body").on("click", ".delete-file", function(){
	var file_id = ($(this).attr("id")).split("-")[2];
	$.ajax({
		url: "/upload/delete/"+file_id,
		type: "DELETE",
		beforeSend: function(xhr, settings){
			if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
				xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}
		},
		success: function (data) {
			alert("Deleted success!")
			location.reload()
		}
	});
	return false;
});