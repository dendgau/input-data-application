from django import template

register = template.Library()

@register.simple_tag
def upload_js():
	return """
<!-- The template to display files available for upload -->
<script id="template-upload" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
	<tr class="template-upload fade">
		<td>
			<p class="name">{%=file.name%}</p>
			{% if (file.error) { %}
				<div><span class="label label-important">{%=locale.fileupload.error%}</span><span class="red" style="margin-left: 5px">{%=file.error%}</span></div>
			{% } %}
		</td>
		<td></td>
		<td></td>
		<td style="text-align: center">
			<p class="size">{%=o.formatFileSize(file.size)%}</p>
			{% if (!o.files.error) { %}
				<div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="progress-bar progress-bar-success" style="width:0%;"></div></div>
			{% } %}
		</td>
		<td></td>
		<td>
			{% if (!o.files.error && !i && !o.options.autoUpload) { %}
				<button class="btn btn-primary start">
					<i class="glyphicon glyphicon-upload"></i>
					<span>{%=locale.fileupload.start%}</span>
				</button>
			{% } %}
			{% if (!i) { %}
				<button class="btn btn-warning cancel">
					<i class="glyphicon glyphicon-ban-circle"></i>
					<span>{%=locale.fileupload.cancel%}</span>
				</button>
			{% } %}
		</td>
	</tr>
{% } %}
</script>
<!-- The template to display files available for download -->
<script id="template-download" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
	<tr class="template-download fade">
		<td>
			<p>
				<a href="{%=file.editUrl%}" title="{%=file.name%}">{%=file.name%}</a>
			</p>
			{% if (file.error) { %}
				<div><span class="label label-important">{%=locale.fileupload.error%}</span> {%=file.error%}</div>
			{% } %}
		</td>
		<td style="width: 25%; text-align: justify">
			{%=file.note%}
		</td>
		<td style="text-align: center">
			{%=file.form%}
		</td>
		<td style="text-align: center">
			<span class="size">{%=o.formatFileSize(file.size)%}</span>
		</td>
		<td style="text-align: center">
			{%=file.uploadDate%}
		</td>
		<td>
			{% if (file.isProcess) { %}
				In Process
			{% }else{ %}
				<div class="visible-md visible-lg hidden-sm hidden-xs action-buttons">
					<a class="green" href="{%=file.editUrl%}">
						<i class="icon-pencil bigger-130"></i>
					</a>
					<a style="cursor:pointer" class="red delete" data-type="{%=file.deleteType%}" data-url="{%=file.deleteUrl%}"{% if (file.deleteWithCredentials) { %} data-xhr-fields='{"withCredentials":true}'{% } %}>
						<i class="icon-trash bigger-130"></i>
					</a>
				</div>
			{% } %}
		</td>
	</tr>
{% } %}
</script>
"""






