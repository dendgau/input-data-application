function getCookie(name){
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
var currentURL = ""
$.ajax({
	url: "/user/get_menu_header",
	type: "POST",
	data: {
		"action": "ajax_post",
		"current_path": window.location.pathname
	},
	success: function (data) {
		var html = '';
		currentURL = data.current_url_name
		if (data.type == "admin"){
			html +=
			"<li class='parent-li'>"+
				"<a href='' class='dropdown-toggle'>" +
					"<i class='glyphicon glyphicon-user'></i> "+
					"<span class='menu-text'>Manage users</span>"+
					"<b class='arrow icon-angle-down'></b>"+
				"</a>"+
				"<ul class='submenu'>"+
					"<li>"+
						"<a class='child-menu' url='list_user' href='/user/list_all_user'>"+
							"<i class='icon-double-angle-right'></i> List all users"+
						"</a>"+
					"</li>"+
					"<li>"+
						"<a class='child-menu' url='add_customer_admin' href='/user/customer_admin_add'>"+
							"<i class='icon-double-angle-right'></i> Create new customer"+
						"</a>"+
					"</li>"+
					"<li>"+
						"<a class='child-menu' url='add_staff' href='/user/staff_add'>"+
							"<i class='icon-double-angle-right'></i> Create new staff"+
						"</a>"+
					"</li>"+
				"</ul>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a href='' class='dropdown-toggle'>" +
					"<i class='icon-desktop'></i> "+
					"<span class='menu-text'>Fields</span>"+
					"<b class='arrow icon-angle-down'></b>"+
				"</a>"+
				"<ul class='submenu'>"+
					"<li>"+
						"<a class='child-menu' url='list-field' href='/transaction/list_field'>"+
							"<i class='icon-double-angle-right'></i> List all fields"+
						"</a>"+
					"</li>"+
					"<li>"+
						"<a class='child-menu' url='field-add' href='/transaction/field_add'>"+
							"<i class='icon-double-angle-right'></i> Create Field"+
						"</a>"+
					"</li>"+
				"</ul>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a href='' class='dropdown-toggle'>" +
					"<i class='icon-list'></i> "+
					"<span class='menu-text'>GroupField</span>"+
					"<b class='arrow icon-angle-down'></b>"+
				"</a>"+
				"<ul class='submenu'>"+
					"<li>"+
						"<a class='child-menu' url='groupfield_list' href='/transaction/groupfield_list'>"+
							"<i class='icon-double-angle-right'></i> List GroupField"+
						"</a>"+
					"</li>"+
					"<li>"+
						"<a class='child-menu' url='create_groupfield' href='/transaction/create_groupfield'>"+
							"<i class='icon-double-angle-right'></i> Create GroupField"+
						"</a>"+
					"</li>"+
				"</ul>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a href='' class='dropdown-toggle'>" +
					"<i class='icon-edit'></i> "+
					"<span class='menu-text'>Form</span>"+
					"<b class='arrow icon-angle-down'></b>"+
				"</a>"+
				"<ul class='submenu'>"+
					"<li>"+
						"<a class='child-menu' url='form_list' href='/transaction/form_list'>"+
							"<i class='icon-double-angle-right'></i> List Form"+
						"</a>"+
					"</li>"+
					"<li>"+
						"<a class='child-menu' url='create_form' href='/transaction/create_form'>"+
							"<i class='icon-double-angle-right'></i> Create Form"+
						"</a>"+
					"</li>"+
				"</ul>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a href='' class='dropdown-toggle'>" +
					"<i class='icon-list-alt'></i> "+
					"<span class='menu-text'>GroupForm</span>"+
					"<b class='arrow icon-angle-down'></b>"+
				"</a>"+
				"<ul class='submenu'>"+
					"<li>"+
						"<a class='child-menu' url='list-group-form' href='/transaction/list_group_form'>"+
							"<i class='icon-double-angle-right'></i> List GroupForm"+
						"</a>"+
					"</li>"+
					"<li>"+
						"<a class='child-menu' url='group-form-add' href='/transaction/group_form_add'>"+
							"<i class='icon-double-angle-right'></i> Create GroupForm"+
						"</a>"+
					"</li>"+
				"</ul>"+
			"</li>";
		}else if (data.type == "customer_admin"){
			html +=
			"<li class='parent-li'>"+
				"<a href='/dashboard' url='dashboard' class='dropdown-toggle'>"+
					"<i class='icon-dashboard'></i> "+
					"<span class='menu-text'>Dashboard</span>"+
				"</a>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a href='' class='dropdown-toggle'>"+
					"<i class='glyphicon glyphicon-user'></i> "+
					"<span class='menu-text'>Manage staff</span>"+
					"<b class='arrow icon-angle-down'></b>"+
				"</a>"+
				"<ul class='submenu'>"+
					"<li>"+
						"<a class='child-menu' url='list_user' href='/user/list_all_user'>"+
							"<i class='icon-double-angle-right'></i> List all staff"+
						"</a>"+
					"</li>"+
					"<li>"+
						"<a class='child-menu' url='add_customer_staff' href='/user/customer_staff_add'>"+
							"<i class='icon-double-angle-right'></i> Create new staff"+
						"</a>"+
					"</li>"+
				"</ul>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a url='upload-history' href='/upload/history' class='dropdown-toggle'>"+
					"<i class='glyphicon glyphicon-calendar'></i> "+
					"<span class='menu-text'>History</span>"+
				"</a>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a url='upload-new' href='/upload/new' class='dropdown-toggle'>"+
					"<i class='glyphicon glyphicon-upload'></i> "+
					"<span class='menu-text'>Upload new file</span>"+
				"</a>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a href='' url='group-form-add' class='dropdown-toggle'>"+
					"<i class='glyphicon glyphicon-print'></i> "+
					"<span class='menu-text'>Export report</span>"+
				"</a>"+
			"</li>";
		}else if (data.type == "customer_staff"){
			html +=
			"<li class='parent-li'>"+
				"<a href='/dashboard' url='dashboard' class='dropdown-toggle'>"+
					"<i class='icon-dashboard'></i> "+
					"<span class='menu-text'>Dashboard</span>"+
				"</a>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a url='upload-history' href='/upload/history' class='dropdown-toggle'>"+
					"<i class='glyphicon glyphicon-calendar'></i> "+
					"<span class='menu-text'>History</span>"+
				"</a>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a url='upload-new' href='/upload/new' class='dropdown-toggle'>"+
					"<i class='glyphicon glyphicon-upload'></i> "+
					"<span class='menu-text'>Upload new file</span>"+
				"</a>"+
			"</li>"+
			"<li class='parent-li'>"+
				"<a href='' class='child-menu' url='group-form-add' class='dropdown-toggle'>"+
					"<i class='glyphicon glyphicon-print'></i> "+
					"<span class='menu-text'>Export report</span>"+
				"</a>"+
			"</li>";
		}else if (data.type == "staff"){
			$(".loading-span-notify").show();
			$(".bell_notify").hide();
			$.ajax({
				url: "/user/get_notify_staff",
				type: "POST",
				data: {
				},
				success: function (data) {
					var items = data.items
					if (items.length > 0){
						$(".there-are").show();
						$(".there-are-not").hide();
						$(".number-notify").html(items.length)

						var html_notify = ""
						for (var i=0; i<items.length; i++){
							html_notify+="<li>"+
								'<a class="link_notify" href="'+items[i]["link"]+'">'+
									'<div class="clearfix">'+
										'<span class="pull-left">'+items[i]["name"]+'</span>'+
										'<span class="pull-right">'+items[i]["file_process"]+'</span>'+
									'</div>'+
									'<div class="progress progress-mini ">'+
										'<div style="width:'+items[i]["progress"]+'%" class="progress-bar "></div>'+
									'</div>'+
								'</a>'+
							'</li>';
						}
						setTimeout(function(){
							$(".notification-content").html(html_notify);
							$(".loading-span-notify").hide();
							$(".bell_notify").show();
						}, 300);
					}else{
						$(".there-are").hide();
						$(".there-are-not").show();
						setTimeout(function(){
							$(".notification-content").html("");
							$(".loading-span-notify").hide();
							$(".bell_notify").show();
						}, 300);
					}
				}
			})
			//$("body").on("click", ".open-notify", function(){
			//	var openNotify = $(this);
			//	if (openNotify.hasClass("open")){
			//		openNotify.removeClass("open");
			//		$(".notification-content").html("");
			//	}else{
			//		openNotify.addClass("open");
			//		$.ajax({
			//			url: "/user/get_notify_staff",
			//			type: "POST",
			//			data: {
			//			},
			//			success: function (data) {
			//				var items = data.items
			//				if (items.length > 0){
			//					$(".there-are").show();
			//					$(".there-are-not").hide();
			//					$(".number-notify").html(items.length)
			//
			//					var html_notify = ""
			//					for (var i=0; i<items.length; i++){
			//						html_notify+="<li>"+
			//							'<a class="link_notify" href="'+items[i]["link"]+'">'+
			//								'<div class="clearfix">'+
			//									'<span class="pull-left">'+items[i]["name"]+'</span>'+
			//									'<span class="pull-right">'+items[i]["file_process"]+'</span>'+
			//								'</div>'+
			//								'<div class="progress progress-mini ">'+
			//									'<div style="width:'+items[i]["progress"]+'%" class="progress-bar "></div>'+
			//								'</div>'+
			//							'</a>'+
			//						'</li>';
			//					}
			//					$(".notification-content").html(html_notify);
			//				}else{
			//					$(".there-are").hide();
			//					$(".there-are-not").show();
			//					$(".notification-content").html("");
			//				}
			//			}
			//		})
			//	}
			//	return false;
			//});

			$("body").on("click", ".link_notify", function(){
				location.href=$(this).attr("href");
				return false;
			})

			for (var i=0; i<data.data.length; i++){
				html +=
				"<li class='parent-li'>"+
					"<a href='' class='dropdown-toggle'>" +
						"<span class='menu-text'>"+data.data[i]["name"]+"</span>"+
						"<b class='arrow icon-angle-down'></b>"+
					"</a>";
					var forms = data.data[i]["forms"];
					var html_sub = "<ul class='submenu'>";
					for (var j=0; j<forms.length; j++){
						html_sub += "<li>"+
							"<a href='/transaction/files/"+forms[j]["id"]+"'>"+
								"<i class='icon-double-angle-right'></i> "+forms[j]["name"]+
							"</a>"+
						"</li>";
					}
					html_sub+="</ul>";
				html += html_sub;
				html+="</li>";
			}
		}

		$(".dynamic-menu").html(html);
		var elementUrl = $("a[url='"+currentURL+"']"),
			elementHref = $("a[href='"+location.pathname+"']");

		if (elementUrl.length){
			if (elementUrl.hasClass("child-menu")){
				var subMenu = elementUrl.parents("ul.submenu");
				var parentLi = elementUrl.parents("li.parent-li");
				var currentIcon = elementUrl.children("i")
				subMenu.show();
				parentLi.addClass("open");
				currentIcon.show();
			}else{
				var parentLi = elementUrl.parent("li.parent-li");
				parentLi.addClass("open");
			}
		}

		if (elementHref.length){
			var subMenu = elementHref.parents("ul.submenu");
			var parentLi = elementHref.parents("li.parent-li");
			var currentIcon = elementHref.children("i")
			subMenu.show();
			parentLi.addClass("open");
			currentIcon.show();
		}
	}
});