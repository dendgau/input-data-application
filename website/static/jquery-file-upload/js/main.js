/*
 * jQuery File Upload Plugin JS Example 8.8.2
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, regexp: true */
/*global $, window, blueimp */
var groupForm = []

$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        // Uncomment the following to send cross-domain cookies:
        //xhrFields: {withCredentials: true},
        //url: 'server/php/'
        maxFileSize: 8000000,
        acceptFileTypes: /(\.|\/)(pdf)$/i,
        //maxNumberOfFiles: 3,
    });

    var is_alert = false
    $('#fileupload').bind('fileuploadadded', function (e, data) {
        if ($("select[name='group_form']").val() < 0){
            alert("ERROR: You can't choose file if you don't select form. Please try again");
            $("#cancel_all").click();
            return false;
        }else{
            if($("#fileupload .table-upload-today .start").length > 0){
                $("#start_all").show();
                $("#cancel_all").show();
            }
        }
    }).bind('fileuploadfailed', function (e, data) {
        if($("#fileupload .table-upload-today .start").length <= 0){
            $("#start_all").hide();
            $("#cancel_all").hide();
        }else{
            $("#start_all").show();
            $("#cancel_all").show();
        }
    }).bind('fileuploadstarted', function (e, data) {
        if($("#fileupload .table-upload-today .start").length - 1 <= 0){
            $("#start_all").hide();
            $("#cancel_all").hide();
        }else{
            $("#start_all").show();
            $("#cancel_all").show();
        }
    })

    // Enable iframe cross-domain access via redirect option:
    $('#fileupload').fileupload(
        'option',
        'redirect',
        window.location.href.replace(
            /\/[^\/]*$/,
            '/cors/result.html?%s'
        )
    );

    if (window.location.hostname === 'blueimp.github.io') {
        // Demo settings:
        $('#fileupload').fileupload('option', {
            url: '//jquery-file-upload.appspot.com/',
            // Enable image resizing, except for Android and Opera,
            // which actually support image resizing, but fail to
            // send Blob objects via XHR requests:
            disableImageResize: /Android(?!.*Chrome)|Opera/
                .test(window.navigator.userAgent),
            maxFileSize: 5000000,
            acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i
        });
        // Upload server status check for browsers with CORS support:
        if ($.support.cors) {
            $.ajax({
                url: '//jquery-file-upload.appspot.com/',
                type: 'HEAD'
            }).fail(function () {
                $('<div class="alert alert-danger"/>')
                    .text('Upload server currently unavailable - ' +
                            new Date())
                    .appendTo('#fileupload');
            });
        }
    } else {
        // Load existing files:
        $('#fileupload').addClass('fileupload-processing');
        $.ajax({
            // Uncomment the following to send cross-domain cookies:
            //xhrFields: {withCredentials: true},
            //url: $('#fileupload').fileupload('option', 'url'),
            url: '/upload/view/',
            dataType: 'json',
            context: $('#fileupload')[0]
        }).always(function () {
            $(this).removeClass('fileupload-processing');
        }).done(function (result) {
            groupForm = result.group_forms;
            $(this).fileupload('option', 'done')
                .call(this, null, {result: result.files});

            var html_group_form = "";
            var html_form = "";
            if (groupForm.length > 0) {
                html_group_form += "<option value='-1'>" + "-----------------" + "</option>";
                for (var i = 0; i < groupForm.length; i++) {
                    html_group_form += "<option value='" + i + "'>" + groupForm[i]["name"] + "</option>";
                    html_form += "<option value=''>-----------------</option>";
                }
                $(".tool-upload").show();
                $(".information-upload").show();
                $(".alert-permission-upload").remove();
                $(".fileupload-buttonbar").show();
            }else{
                $(".fileupload-buttonbar").remove();
                $(".information-upload").remove();
                $(".alert-permission-upload").html('<i class="icon-warning-sign orange"></i> '+result.error);
                $(".alert-permission-upload").show();
                $(".fileupload-progress").remove();
            }
            $("select[name='group_form']").html(html_group_form);
            $("select[name='form']").html(html_form);
        });
    }

});

$("body").on("change", "select[name='group_form']", function(){
    var index = $(this).val();
    if (index >= 0){
        var html_form = "";
        for (var j=0; j<groupForm[index]["forms"].length; j++){
            html_form += "<option value='"+groupForm[index]["forms"][j]["id"]+"'>"+groupForm[index]["forms"][j]["name"]+"</option>";
        }
        $("select[name='form']").html(html_form);
        $("#choose-file").removeAttr("disabled");
    }else{
        var html_form = "";
        html_form += "<option value=''>-----------------</option>";
        $("select[name='form']").html(html_form);
        $("#choose-file").attr("disabled", true);
    }
    return false;
})
