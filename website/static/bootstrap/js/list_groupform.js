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
						counter += 1;
						html += "<tr id='groupform-"+items[i]["id"]+"'>"+
							"<td>"+items[i]["name"]+"</td>"+
							"<td>"+items[i]["description"]+"</td>"+
							"<td>"+items[i]["html"]+"</td>"+
							"<td style='text-align: center'>";
								if (items[i]["icon"]){
									html+='<span class="profile-picture">'+
										'<img style="width: 80px" class="editable img-responsive editable-click editable-empty" alt="Icon" src="'+items[i]["icon"]+'">'+
									'</span>';
								}
							html+="</td>"+
							"<td>"+
								'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">'+
									'<a class="green" href="/transaction/group_form_edit/'+items[i]["id"]+'">'+
										'<i class="icon-pencil bigger-130"></i>'+
									'</a>'+
									'<a id="delete-groupform-'+items[i]["id"]+'" class="red delete-groupform" href="">'+
										'<i style="margin: 0 3px" class="icon-trash bigger-130"></i>'+
									'</a>'+
								'</div>'+
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

$("body").on("click", ".delete-groupform", function(){
	if (confirm("Do you want to delete this GroupForm?")) {
		var groupform_id = ($(this).attr("id")).split("-")[2];
		var me = $(this);
		$(".action-buttons-" + groupform_id).removeClass("visible-lg");
		$(".loading-span-" + groupform_id).show();
		$.ajax({
			url: "/transaction/group_form_delete/" + groupform_id,
			type: "DELETE",
			beforeSend: function (xhr, settings) {
				if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
					xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
				}
			},
			success: function (data) {
				$("#groupform-" + groupform_id).fadeOut(300, function () {
					$("#groupform-" + groupform_id).remove();
				});
				for (var i=0; i<items_search.length; i++){
					if (items_search[i]["id"] == groupform_id){
						items_search.splice(i, 1);
						break;
					}
				}
			},
			error: function (request, error) {
				alert("ERROR: You can not delete this GroupForm. Please try again");
				$(".loading-span-"+groupform_id).hide();
				$(".action-buttons-"+groupform_id).addClass("visible-lg");
			}
		});
	}
	return false;
});

function getTemplate(items){
	var html = "";
	for(var i=0; i<items.length; i++){
		counter += 1;
		html += "<tr id='groupform-"+items[i]["id"]+"'>"+
			"<td>"+items[i]["name"]+"</td>"+
			"<td>"+items[i]["description"]+"</td>"+
			"<td>"+items[i]["html"]+"</td>"+
			"<td style='text-align: center'>";
				if (items[i]["icon"]){
					html+='<span class="profile-picture">'+
						'<img style="width: 80px" class="editable img-responsive editable-click editable-empty" alt="Icon" src="'+items[i]["icon"]+'">'+
					'</span>';
				}
			html+="</td>"+
			"<td>"+
				'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">'+
					'<a class="green" href="/transaction/group_form_edit/'+items[i]["id"]+'">'+
						'<i class="icon-pencil bigger-130"></i>'+
					'</a>'+
					'<a id="delete-groupform-'+items[i]["id"]+'" class="red delete-groupform" href="">'+
						'<i style="margin: 0 3px" class="icon-trash bigger-130"></i>'+
					'</a>'+
				'</div>'+
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