// 連続送信防止
$('.save').on('click', function(e){
	$('.save').addClass('disabled');
	$('#obj_form').submit();
})
$(function() {
	$(".log_cell").each(function() {
		if ($(this).text().trim() != "") {
			$(this).addClass("table-success");
		}
	});
});