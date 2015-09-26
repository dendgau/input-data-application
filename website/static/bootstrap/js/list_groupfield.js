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
						html += "<tr>"+
							"<td style='padding-bottom: 17px'>"+items[i]["name"]+"</td>"+
							"<td>"+
								'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">'+
									'<a class="green" href="/transaction/edit_groupfield?action=edit&groupfield_id='+items[i]["id"]+'">'+
										'<i class="icon-pencil bigger-130"></i>'+
									'</a>'+
									'<a id="delete-field-'+items[i]["id"]+'" class="red delete-field" href="/transaction/delete_groupfield?action=delete&groupfield_id='+items[i]["id"]+'">'+
										'<i style="margin: 0 2px" class="icon-trash bigger-130"></i>'+
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
				}
			});
		}
	}
});

$("body").on("click", ".delete-field", function(){
	var groupfield_id = ($(this).attr("id")).split("-")[2];
	$(".action-buttons-" + groupfield_id).removeClass("visible-lg");
	$(".loading-span-" + groupfield_id).show();
	$(this).click();
	return false;
});

function getTemplate(items){
	var html = "";
	for(var i=0; i<items.length; i++){
		counter += 1;
		html += "<tr>"+
			"<td style='padding-bottom: 17px'>"+items[i]["name"]+"</td>"+
			"<td>"+
				'<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons action-buttons-'+items[i]["id"]+'">'+
					'<a class="green" href="/transaction/edit_groupfield?action=edit&groupfield_id='+items[i]["id"]+'">'+
						'<i class="icon-pencil bigger-130"></i>'+
					'</a>'+
					'<a id="delete-field-'+items[i]["id"]+'" class="red delete-field" href="/transaction/delete_groupfield?action=delete&groupfield_id='+items[i]["id"]+'">'+
						'<i style="margin: 0 2px" class="icon-trash bigger-130"></i>'+
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