$(document).ready(function(){
	$('.profile__toggle__email').click(function(){
		$('.profile__toggle__input__email').slideToggle(300, function(){
			if ($(this).is(':hidden')) {
				$('.profile__toggle__email').html('Изменить');
			} else {
				$('.profile__toggle__email').html('Отменить изменения');
			}
		});
		return false;
	});
	$('.profile__toggle__telegram').click(function(){
		$('.profile__toggle__input__telegram').slideToggle(300, function(){
			if ($(this).is(':hidden')) {
				$('.profile__toggle__telegram').html('Изменить');
			} else {
				$('.profile__toggle__telegram').html('Отменить изменения');
			}
		});
		return false;
	});
});