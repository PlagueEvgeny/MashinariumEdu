from django.urls import path
import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('', mainapp.course_list, name='course_list'), # Список курсов
    path('<slug:slug>/', mainapp.course_detail, name='course_detail'), # Детали курсов (не куплены)
    path('user/course/<slug:slug>/', mainapp.purchased_course_detail, name='purchased_course_detail'), # Детали курсов (куплены)
    path('user/course/<slug:slug>/m-<int:pk>/', mainapp.module_detail, name='module_detail'), # Модули
    path('user/course/<slug:slug>/m-<int:module_id>/l-<int:pk>', mainapp.session, name='session'), # Занятие
    path('user/course/<slug:slug>/f-<int:pk>', mainapp.final_session_all, name='final_course_session'), # Финальное занятие курсов
    path('user/course/<slug:slug>/m-<int:module_id>/f-<int:pk>', mainapp.final_session_all, name='final_module_session'), # Финальное занятие модуля
    path('user/course/<slug:slug>/t-<int:test_id>', mainapp.take_test, name='take_test_course'), # Тестирование курсов
    path('user/course/<slug:slug>/m-<int:module_id>/t-<int:test_id>', mainapp.take_test, name='take_test_module'), # Тестирование модуля
    path('user/course/result/test-<int:response_id>', mainapp.test_result, name='test_result'), # Тестирование результаты
]