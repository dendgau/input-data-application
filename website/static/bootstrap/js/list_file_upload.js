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
						html += "<tr id='file_"+items[i]["id"]+"'>"+
							"<td>"+items[i]["name"]+"</td>"+
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
							'<td style="text-align: left">';
								if (!items[i]["is_start_process"]){
									html+='<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">'+
										'<a class="green" href="/upload/edit/'+items[i]["id"]+'">'+
											'<i class="icon-pencil bigger-130"></i>'+
										'</a>'+
										'<a id="delete-file-'+items[i]["id"]+'" class="red delete-file" href="">'+
											'<i style="margin: 0 3px"  class="icon-trash bigger-130"></i>'+
										'</a>'+
									'</div>'+
									'<center style="margin-bottom: 10px">'+
										'<span class="loading-span-'+items[i]["id"]+'" style="font-size: 12px; display: none;">'+
											'<img width="20px" src="/site_media/static/bootstrap/images/loading.gif">'+
										'</span>'+
									'</center>';
								}else{
									html+="In Process"
								}
							html+="</td>"+
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

$("body").on("click", ".delete-file", function(){
	if (confirm("Do you want to delete this file?")){
		var file_id = ($(this).attr("id")).split("-")[2];
		$(".action-buttons-"+file_id).removeClass("visible-lg");
		$(".loading-span-"+file_id).show();
		$.ajax({
			url: "/upload/delete/"+file_id,
			type: "DELETE",
			beforeSend: function(xhr, settings){
				if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
					xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
				}
			},
			success: function (data) {
				$("#file_"+file_id).fadeOut(300, function() {
					$("#file_"+file_id).remove();
				});
				for (var i=0; i<items_search.length; i++){
					if (items_search[i]["id"] == file_id){
						items_search.splice(i, 1);
						break;
					}
				}
			},
			error: function (request, error) {
				alert("ERROR: You can not delete this user. Please try again");
				$(".loading-span-"+file_id).hide();
				$(".action-buttons-"+file_id).addClass("visible-lg");
			},
		});
	}
	return false;
});

function getTemplate(items){
	var html = "";
	for(var i=0; i<items.length; i++){
		counter += 1;
		html += "<tr id='file_"+items[i]["id"]+"'>"+
			"<td>"+items[i]["name"]+"</td>"+
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
			'<td style="text-align: left">';
				if (!items[i]["is_start_process"]){
					html+='<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">'+
						'<a class="green" href="/upload/edit/'+items[i]["id"]+'">'+
							'<i class="icon-pencil bigger-130"></i>'+
						'</a>'+
						'<a  id="delete-file-'+items[i]["id"]+'" class="red delete-file" href="">'+
							'<i style="margin: 0 3px"  class="icon-trash bigger-130"></i>'+
						'</a>'+
					'</div>'+
					'<center style="margin-bottom: 10px">'+
						'<span class="loading-span-'+items[i]["id"]+'" style="font-size: 12px; display: none;">'+
							'<img width="20px" src="/site_media/static/bootstrap/images/loading.gif">'+
						'</span>'+
					'</center>';
				}else{
					html+="In Process"
				}
			html+="</td>"+
		"</tr>";
	}
	return html;
}