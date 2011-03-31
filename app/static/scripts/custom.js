$(document).ready(function() {
	$('#namespace_login').submit(function() {
		namespace = $('#namespace_login_value').val();
		if(namespace != ''){
			window.location.replace("http://"+$('#namespace_login_value').val()+'.qrtar.com/auth/login');
		}else{
			alert('Please enter a namespace to login.');
		}
		return false;
	});


});

