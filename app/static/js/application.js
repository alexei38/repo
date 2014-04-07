$(document).ready(function() {
	$('#form_submit').live('click', function(){
		$(this).parent().parent().parent().parent().modal('hide');
        $('#pleaseWaitDialog').modal('show');
	});
});