$(window).scroll(function() {
	if($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
		if (!is_loading && has_next){
			var action = location.href;
			action = action.split("?")[0];
			action += "?q="+encodeURIComponent(q)+"&page="+next_page;
			is_loading = true
			$(".loading-span").show();
			$.ajax({
				url: action,
				type: "GET",
				success: function (data) {
					var items = data.items;
					var html = "";
					for(var i=0; i<items.length; i++){
						html += "<tr id='field-"+items[i]["id"]+"'>"+
							"<td style='padding-bottom:15px'>"+items[i]["label"]+"</td>"+
							"<td>"+items[i]["fieldtype"]+"</td>"+
							"<td>"+items[i]["description"]+"</td>"+
							"<td>"+items[i]["html"]+"</td>"+
							"<td>"+
								'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">';
									html+='<a style="cursor: pointer" title="Edit" class="green" href="/transaction/field_edit/'+items[i]["id"]+'">'+
										'<i class="icon-pencil bigger-130"></i>'+
									'</a>';
									html+='<a style="cursor: pointer" title="Delete" id="delete-field-'+items[i]["id"]+'" class="red delete-field">'+
										'<i style="margin: 0 2px" class="icon-trash bigger-130"></i>'+
									'</a>';
							html+="</div>"+
								'<center style="margin-bottom: 10px">'+
									'<span class="loading-span-'+items[i]["id"]+'" style="font-size: 12px; display: none;">'+
										'<img width="20px" src="/site_media/static/bootstrap/images/loading.gif">'+
									'</span>'+
								'</center>'+
							"</td>"+
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
				},
				error: function (request, error) {
					alert("ERROR: Please check your Internet connection");
				},
			});
		}
	}
});

$("body").on("click", ".delete-field", function(){
	if (confirm("Do you want to delete this user?")) {
		var field_id = ($(this).attr("id")).split("-")[2];
		$(".action-buttons-" + field_id).removeClass("visible-lg");
		$(".loading-span-" + field_id).show();
		$.ajax({
			url: "/transaction/field_delete/" + field_id,
			type: "DELETE",
			beforeSend: function (xhr, settings) {
				if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
					xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
				}
			},
			success: function (data) {
				$("#field-" + field_id).fadeOut(300, function () {
					$("#field-" + field_id).remove();
				});
				for (var i=0; i<items_search.length; i++){
					if (items_search[i]["id"] == field_id){
						items_search.splice(i, 1);
						break;
					}
				}
			},
			error: function (request, error) {
				alert("ERROR: You can not delete this field. Please try again");
				$(".loading-span-"+field_id).hide();
				$(".action-buttons-"+field_id).addClass("visible-lg");
			},
		});
	}
	return false;
});

function getTemplate(items){
	var html = "";
	for(var i=0; i<items.length; i++){
		html += "<tr id='field-"+items[i]["id"]+"'>"+
			"<td style='padding-bottom:15px'>"+items[i]["label"]+"</td>"+
			"<td>"+items[i]["fieldtype"]+"</td>"+
			"<td>"+items[i]["description"]+"</td>"+
			"<td>"+items[i]["html"]+"</td>"+
			"<td>"+
				'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">';
					html+='<a style="cursor: pointer" title="Edit" class="green" href="/transaction/field_edit/'+items[i]["id"]+'">'+
						'<i class="icon-pencil bigger-130"></i>'+
					'</a>';
					html+='<a style="cursor: pointer" title="Delete" id="delete-field-'+items[i]["id"]+'" class="red delete-field">'+
						'<i style="margin: 0 2px" class="icon-trash bigger-130"></i>'+
					'</a>';
			html+="</div>"+
				'<center style="margin-bottom: 10px">'+
					'<span class="loading-span-'+items[i]["id"]+'" style="font-size: 12px; display: none;">'+
						'<img width="20px" src="/site_media/static/bootstrap/images/loading.gif">'+
					'</span>'+
				'</center>'+
			"</td>"+
		"</tr>";
	}
	return html;
}
