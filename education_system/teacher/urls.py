from django.urls import path
import teacher.views as teacher

app_name = 'teacher'

urlpatterns = [
    path('course/', teacher.course_teacher, name="course_teacher"),
    path('course/<slug:slug>', teacher.course_detail, name="course_detail"),
    path('course/<slug:slug>/m-<int:pk>', teacher.module_teacher, name="module_teacher"),
    path('course/<slug:slug>/students', teacher.course_student_teacher, name="course_student_teacher"),
    path('course/<slug:slug>/f-<int:pk>', teacher.final_session_all, name='final_course_session_teacher'), # Финальное занятие курсов
    path('course/<slug:slug>/m-<int:module_id>/f-<int:pk>', teacher.final_session_all, name='final_module_session_teacher'),  # Финальное занятие модуля
    path('course/<slug:slug>/t-<int:pk>', teacher.test, name='testing_course_teacher'), # Тестирование курсов
    path('course/<slug:slug>/m-<int:module_id>/t-<int:pk>', teacher.test, name='testing_module_teacher'),  # Тестирование модуля
    path('course/<slug:slug>/m-<int:module_id>/s-<int:pk>', teacher.session, name='session_teacher'), #
    #
    path('create/course/', teacher.course_create, name="course_create"),
    #
    path('change/<slug:slug>', teacher.course_change, name="course_change"),
    path('change/<slug:slug>/m-<int:pk>', teacher.module_change, name="module_change"),
    path('change/<slug:slug>/m-<int:module_id>/s-<int:pk>/', teacher.session_change, name="session_change"),
    path('change/<slug:slug>/f-<int:pk>/', teacher.final_session_change, name="final_session_course_change"),
    path('change/<slug:slug>/m-<int:module_id>/f-<int:pk>/', teacher.final_session_change, name="final_session_module_change"),
    path('change/<slug:slug>/m-<int:module_id>/t-<int:pk>/', teacher.edit_test, name="edit_test"),
]
