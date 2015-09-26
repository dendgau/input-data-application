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
						html += "<tr id='user_"+items[i]["id"]+"'>"+
							"<td>"+items[i]["username"]+"</td>"+
							"<td>"+items[i]["email"]+"</td>"+
							"<td>"+items[i]["first_name"]+"</td>"+
							"<td>"+items[i]["last_name"]+"</td>"+
							"<td>";
								if (items[i]["is_staff"]){
									html+='<span style="padding-top: 4px" class="label label-danger arrowed arrowed-in-right">System staff</span>';
								}else{
									if (items[i]["is_customer_superadmin"]){
										html+='<span style="padding-top: 4px" class="label label-warning arrowed-right arrowed-in">Customer admin</span>';
									}else{
										html+='<span style="padding-top: 4px" class="label arrowed-right arrowed-in">Customer staff</span>';
									}
								}
							html+="</td>"+
							"<td>"+
								'<span style="padding-top: 4px" class="label label-inverse arrowed">'+items[i]["company"]+'</span>'+
							"</td>"+
							"<td>"+items[i]["date_joined"]+"</td>"+
							"<td>"+
								'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">';
									if (items[i]["is_staff"]){
										items[i]["position"] = "Staff";
										html+='<a style="cursor: pointer" title="Edit" class="green" href="/user/staff_edit/'+items[i]["id"]+'">'+
											'<i class="icon-pencil bigger-130"></i>'+
										'</a>';
									}else if (items[i]["is_customer_superadmin"]){
										items[i]["position"] = "Customer admin";
										html+='<a style="cursor: pointer" title="Edit" class="green" href="/user/customer_admin_edit/'+items[i]["id"]+'">'+
											'<i class="icon-pencil bigger-130"></i>'+
										'</a>';
									}else{
										items[i]["position"] = "Customer staff";
										html+='<a style="cursor: pointer" title="Edit" class="green" href="/user/customer_staff_edit/'+items[i]["id"]+'">'+
											'<i class="icon-pencil bigger-130"></i>'+
										'</a>';
									}
									html+='<a style="cursor: pointer" title="Delete" id="delete-user-'+items[i]["id"]+'" class="red delete-user">'+
										'<i style="margin: 0 2px" class="icon-trash bigger-130"></i>'+
									'</a>';
									if (items[i]["is_staff"] && !items[i]["is_superuser"]){
										html+='<a style="cursor: pointer" title="Set permission" href="/user/permission?user='+items[i]["id"]+'">'+
											'<i style="margin: 0 2px" class="icon-user bigger-130"></i>'+
										'</a>';
									}
							html+="</div>"+
								'<center style="margin-bottom: 10px">'+
									'<span class="loading-span-'+items[i]["id"]+'" style="font-size: 12px; display: none;">'+
										'<img width="20px" src="/site_media/static/bootstrap/images/loading.gif">'+
									'</span>'+
								'</center>'+
							"</td>"+
						"</tr>";
						items[i]["index_array"] = items_search.length - 1;
						items_search.push(items[i]);
					}
					is_loading = false;
					has_next = data.has_next;
					next_page = data.next_page;
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

$("body").on("click", ".delete-user", function(){
	if (confirm("Do you want to delete this user?")){
		var user_id = ($(this).attr("id")).split("-")[2];
		$(".action-buttons-"+user_id).removeClass("visible-lg");
		$(".loading-span-"+user_id).show();
		$.ajax({
			url: "/user/list_all_user",
			type: "POST",
			data: {"user_id": user_id, "action": "ajax_post"},
			beforeSend: function(xhr, settings){
				if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
					xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
				}
			},
			success: function (data) {
				$("#user_"+user_id).fadeOut(300, function() {
					$("#user_"+user_id).remove();
				});
				for (var i=0; i<items_search.length; i++){
					if (items_search[i]["id"] == user_id){
						items_search.splice(i, 1);
						break;
					}
				}
			},
			error: function (request, error) {
				alert("ERROR: You can not delete this user. Please try again");
				$(".loading-span-"+user_id).hide();
				$(".action-buttons-"+user_id).addClass("visible-lg");
			},
		});
	}
	return false;
});

function getTemplate(items){
	var html = "";
	for(var i=0; i<items.length; i++){
		html += "<tr id='user_"+items[i]["id"]+"'>"+
			"<td>"+items[i]["username"]+"</td>"+
			"<td>"+items[i]["email"]+"</td>"+
			"<td>"+items[i]["first_name"]+"</td>"+
			"<td>"+items[i]["last_name"]+"</td>"+
			"<td>";
				if (items[i]["is_staff"]){
					html+='<span style="padding-top: 4px" class="label label-danger arrowed arrowed-in-right">System staff</span>';
				}else{
					if (items[i]["is_customer_superadmin"]){
						html+='<span style="padding-top: 4px" class="label label-warning arrowed-right arrowed-in">Customer admin</span>';
					}else{
						html+='<span style="padding-top: 4px" class="label arrowed-right arrowed-in">Customer staff</span>';
					}
				}
			html+="</td>"+
			"<td>"+
				'<span style="padding-top: 4px" class="label label-inverse arrowed">'+items[i]["company"]+'</span>'+
			"</td>"+
			"<td>"+items[i]["date_joined"]+"</td>"+
			"<td>"+
				'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">';
					if (items[i]["is_staff"]){
						items[i]["position"] = "Staff";
						html+='<a style="cursor: pointer" title="Edit" class="green" href="/user/staff_edit/'+items[i]["id"]+'">'+
							'<i class="icon-pencil bigger-130"></i>'+
						'</a>';
					}else if (items[i]["is_customer_superadmin"]){
						items[i]["position"] = "Customer admin";
						html+='<a style="cursor: pointer" title="Edit" class="green" href="/user/customer_admin_edit/'+items[i]["id"]+'">'+
							'<i class="icon-pencil bigger-130"></i>'+
						'</a>';
					}else{
						items[i]["position"] = "Customer staff";
						html+='<a style="cursor: pointer" title="Edit" class="green" href="/user/customer_staff_edit/'+items[i]["id"]+'">'+
							'<i class="icon-pencil bigger-130"></i>'+
						'</a>';
					}
					html+='<a style="cursor: pointer" title="Delete" id="delete-user-'+items[i]["id"]+'" class="red delete-user">'+
						'<i style="margin: 0 2px" class="icon-trash bigger-130"></i>'+
					'</a>';
					if (items[i]["is_staff"] && !items[i]["is_superuser"]){
						html+='<a style="cursor: pointer" title="Set permission" href="/user/permission?user='+items[i]["id"]+'">'+
							'<i style="margin: 0 2px" class="icon-user bigger-130"></i>'+
						'</a>';
					}
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
