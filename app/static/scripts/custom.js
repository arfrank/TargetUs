$(document).ready(function() {
	$('#namespace_login').submit(function() {
		namespace = $('#namespace_login_value').val();
		if(namespace != ''){
			window.location.replace("http://"+$('#namespace_login_value').val()+'.target-us.appspot.com/auth/login');
		}else{
			alert('Please enter a namespace to login.');
		}
		return false;
	});
	$('#create_form').submit(function() {
		ret = true;
		$('.error').removeClass('error');
		for (var i=1; i < 5 ; i++) {
			if ($('#redirect'+i).val() != '') {
				if ($('#redirector'+i).val()=='') {
					$('#redirector'+i).addClass('error');
					ret = false;
				};
			};
			if ($('#redirector'+i).val() != '') {
				if ($('#redirect'+i).val()=='') {
					$('#redirect'+i).addClass('error');
					ret = false;
				};
			};
		};
		return ret;
	});

});

