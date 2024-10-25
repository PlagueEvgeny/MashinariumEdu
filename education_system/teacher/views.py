from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from mainapp.models import Course, Review, FinalCourseSession
from mainapp.models import Module, FinalModuleSession, FinalSessionResponse, FinalSessionFile
from mainapp.models import FinalSessionFile
from mainapp.models import Session, Homework, HomeworkFile
from mainapp.models import Test, TestQuestion, TestResponse, TestAnswerChoice, UserAnswer
from django.contrib import messages
from teacher.forms import CourseForm, ModuleForm, SessionForm, FinalModuleSessionForm, FinalCourseSessionForm
from django.http import HttpResponse, HttpResponseRedirect
from chatapp.models import Room
from mainapp.utility.download_files import download_files
from django.forms import modelformset_factory
from teacher.forms import TestForm, QuestionFormSet, AnswerChoiceFormSet, TestFullForm


@login_required
def course_teacher(request):
    courses = Course.objects.filter(teacher=request.user, is_active=True)

    context = {
        "courses": courses,
        "title": "Преподаватель",
    }

    return render(request, "teacher/course_teacher.html", context)


@login_required
def course_detail(request, slug):
    # Получаем курс по slug
    course = get_object_or_404(Course, slug=slug, teacher=request.user)

    # Получаем модули, финальные занятия и тесты
    modules = course.module_course.all()  # Модули курса
    final_course_assignments = FinalCourseSession.objects.filter(course=course)  # Финальное занятие курса
    tests = Test.objects.filter(course=course)  # Тесты, связанные с курсом

    context = {
        'course': course,
        'modules': modules,
        'final_course_assignments': final_course_assignments,
        'tests': tests,
        "title": f"Курс: {course.name}"
    }

    return render(request, 'teacher/course_detail.html', context)

@login_required
def module_teacher(request, slug, pk):
    # Получаем курс по Slug
    course = get_object_or_404(Course, slug=slug)
    # Получаем модуль по ID
    module = get_object_or_404(Module, course=course, id=pk)


    # Получаем занятия, задания, финальные задания и тесты
    sessions = module.sessions.all()
    final_assignments = FinalModuleSession.objects.filter(module=module)
    tests = Test.objects.filter(module=module)

    context = {
        'module': module,
        'sessions': sessions,
        'final_assignments': final_assignments,
        'tests': tests,
        "title": f"Модуль: {module.name}"
    }
    return render(request, 'teacher/module_teacher.html', context)


def final_session_all(request, slug, pk, module_id=None):
    course = get_object_or_404(Course, slug=slug)
    module = get_object_or_404(Module, course__slug=slug, id=module_id) if module_id else None

    if module_id:
        final_session = FinalModuleSession.objects.filter(id=pk, module=module).first()
    else:
        final_session = FinalCourseSession.objects.filter(id=pk, course=course).first()

    if not final_session:
        messages.error(request, "Финальное занятие не найдено.")
        if module_id:
            return redirect('teacher:final_module_session_teacher', kwargs={"slug": course.slug, "module_id": module.id, 'pk': final_session.id})
        else:
            return redirect('teacher:final_course_session_teacher', kwargs={"slug": course.slug, 'pk': final_session.id})

    if module_id:
        final_response = FinalSessionResponse.objects.filter(final_module_session=final_session)
    else:
        final_response = FinalSessionResponse.objects.filter(final_course_session=final_session)

    download_response_id = request.GET.get('download_response_id')
    if download_response_id:
        response = get_object_or_404(FinalSessionResponse, id=download_response_id)

        # Проверка наличия загруженных файлов
        if response.files.exists():  # Проверяем, есть ли связанные файлы
            return download_files(response)
        else:
            messages.error(request, "Файлы не найдены для скачивания.")
            if module_id:
                return HttpResponseRedirect(
                    reverse('teacher:final_module_session_teacher', kwargs={"slug": course.slug, "module_id": module.id, 'pk': final_session.id}))
            else:
                return HttpResponseRedirect(reverse('teacher:final_course_session_teacher', kwargs={"slug": course.slug, 'pk': final_session.id}))

    context = {
        "course": course,
        "module": module,
        "final_session": final_session,
        "final_response": final_response,
        "title": f"Контрольное занятие: {final_session.title}",
    }

    return render(request, "teacher/final_session.html", context)


def session(request, slug, pk, module_id=None):
    module = get_object_or_404(Module, course__slug=slug, id=module_id)
    session = get_object_or_404(Session, module=module, id=pk)

    # Проверяем, есть ли у пользователя доступ к модулю
    if request.user not in module.completed_by.all():
        messages.error(request, "У вас нет доступа к этому модулю.")
        return redirect('main:courses')  # Перенаправляем на страницу курсов, если нет доступа

    # Получаем все домашние задания для текущего занятия
    home_work = Homework.objects.filter(session=session)

    download_response_id = request.GET.get('download_response_id')
    if download_response_id:
        home_work = get_object_or_404(Homework, id=download_response_id)

        # Проверка наличия загруженных файлов
        if home_work.files.exists():  # Проверяем, есть ли связанные файлы
            return download_files(home_work)
        else:
            messages.error(request, "Файлы не найдены для скачивания.")


    context = {
        "module": module,
        "session": session,
        "home_work": home_work,
        "title": f"Занятие: {session.title}",
    }

    return render(request, "teacher/lesson_teacher.html", context)


def test(request, slug, pk, module_id=None):
    course = get_object_or_404(Course, slug=slug)
    module = get_object_or_404(Module, course__slug=slug, id=module_id) if module_id else None

    if module_id:
        testing = Test.objects.filter(id=pk, module=module).first()
    else:
        testing = Test.objects.filter(id=pk, course=course).first()

    questions = testing.questions.all()
    questions_count = questions.count()

    response = TestResponse.objects.filter(test=testing)

    if not testing:
        messages.error(request, "Тестирование не найдено.")
        if module_id:
            return redirect('teacher:testing_module_teacher', kwargs={"slug": course.slug, "module_id": module.id, 'pk': testing.id})
        else:
            return redirect('teacher:testing_course_teacher', kwargs={"slug": course.slug, 'pk': testing.id})


    context = {
        "course": course,
        "module": module,
        "testing": testing,
        "response": response,
        "questions_count": questions_count,
        "title": f"Тестирование: {testing.title}",
    }

    return render(request, "teacher/testing_teacher.html", context)


@login_required
def course_student_teacher(request, slug):
    course = Course.objects.get(teacher=request.user, is_active=True, slug=slug)

    context = {
        'course': course,
        "title": f"Участиники курса {course.name}"
    }

    return render(request, "teacher/course_student_teacher.html", context)


# Создать
@login_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.teacher = request.user
            form.save()
            messages.success(request, f'Курс {form.name} успешно создан')
            Room.objects.get_or_create(course=form, name=form.name, slug=form.slug)
            room = Room.objects.get(slug=form.slug)
            room.user.add(request.user)
            return HttpResponseRedirect(reverse
                                        ('teacher:course_teacher'))
        messages.error(request, 'Курс не создан')
    form = CourseForm()

    context = {
        'form': form,
        "title": f"Создать курс",
    }

    return render(request, "teacher/crud/create/course_create_teacher.html", context)


# Изменить
@login_required
def course_change(request, slug):
    courses = Course.objects.get(teacher=request.user, is_active=True, slug=slug)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=courses)
        if form.is_valid():
            form = form.save(commit=False)
            form.teacher = request.user
            form.save()
            messages.success(request, 'Изменения встпили в силу')
            return HttpResponseRedirect(reverse
                                        ('teacher:course_change', kwargs={'slug': courses.slug}))
        messages.error(request, 'Изменения не вступили в силу')
    form = CourseForm()

    context = {
        "courses": courses,
        'form': form,
        "title": f"Изменить курс: {courses.name}",
    }

    return render(request, "teacher/crud/change/course_change_teacher.html", context)


@login_required
def module_change(request, slug, pk):
    course = Course.objects.get(teacher=request.user, is_active=True, slug=slug)
    module = Module.objects.get(course=course, id=pk)
    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES, instance=module)
        if form.is_valid():
            form = form.save(commit=False)
            form.course = course
            form.save()
            messages.success(request, 'Изменения вступили в силу')
            return HttpResponseRedirect(reverse
                                        ('teacher:module_change', kwargs={'slug': course.slug, 'pk': module.id}))
        messages.error(request, 'Изменения не вступили в силу')
    form = ModuleForm()

    context = {
        "course": course,
        "module": module,
        'form': form,
        "title": f"Изменить модуль: {module.name}",
    }

    return render(request, "teacher/crud/change/module_change_teacher.html", context)


@login_required
def session_change(request, slug, module_id, pk):
    module = Module.objects.get(course__slug=slug, id=module_id)
    session = Session.objects.get(module=module_id, id=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, request.FILES, instance=session)
        if form.is_valid():
            form = form.save(commit=False)
            form.module = module
            form.save()
            messages.success(request, 'Изменения встпили в силу')
            return HttpResponseRedirect(reverse
                                        ('teacher:session_change',
                                         kwargs={'slug': module.course.slug, 'module_id': module.id, 'pk': session.id}))
        messages.error(request, 'Изменения не вступили в силу')
    form = SessionForm()

    context = {
        "module": module,
        "session": session,
        'form': form,
        "title": f"Изменить занятие: {session.title}",
    }

    return render(request, "teacher/crud/change/lesson_change_teacher.html", context)


@login_required
def final_session_change(request, slug, pk, module_id=None):
    course = Course.objects.get(teacher=request.user, is_active=True, slug=slug)
    final_session = None
    module = None
    if not module_id:
        final_session = FinalCourseSession.objects.get(course=course, id=pk)
    if module_id:
        module = Module.objects.get(course=course, id=module_id)
        final_session = FinalModuleSession.objects.get(module=module, id=pk)

    if request.method == "POST":
        if module_id:
            form = FinalModuleSessionForm(request.POST, request.FILES, instance=final_session)
        else:
            form = FinalCourseSessionForm(request.POST, request.FILES, instance=final_session)

        if form.is_valid():
            form = form.save(commit=False)
            if module_id:
                form.module = module
            else:
                form.course = course
            form.save()
            messages.success(request, 'Изменения встпили в силу')
            if not module_id:
                return HttpResponseRedirect(reverse
                                            ('teacher:final_session_course_change',
                                             kwargs={'slug': course.slug, 'pk': final_session.id}))
            return HttpResponseRedirect(reverse
                                        ('teacher:final_session_module_change',
                                         kwargs={'slug': course.slug, 'module_id': module.id, 'pk': final_session.id}))
        messages.error(request, 'Изменения не вступили в силу')
    if module_id:
        form = FinalModuleSessionForm()
    else:
        form = FinalCourseSessionForm()

    context = {
        "final_session": final_session,
        'form': form,
        "title": f"Изменить занятие: {final_session.title}",
    }

    return render(request, "teacher/crud/change/final_event_change_teacher.html", context)
#
#
@login_required
def edit_test(request, slug, pk, module_id=None):
    course = get_object_or_404(Course, teacher=request.user, is_active=True, slug=slug)
    module = None
    test = None

    if module_id:
        module = get_object_or_404(Module, course=course, id=module_id)
        test = get_object_or_404(Test, module=module, id=pk)
    else:
        test = get_object_or_404(Test, course=course, id=pk)

    # Получаем связанные вопросы и варианты ответов
    questions = TestQuestion.objects.filter(test=test).prefetch_related('choices')

    if request.method == 'POST':
        print("Полученные данные формы:", request.POST)  # Отладка
        form = TestForm(request.POST, instance=test)
        question_formset = QuestionFormSet(request.POST, instance=test, prefix='questions')

        # Удаляем пустые формы вопросов
        for question_form in question_formset:
            if not question_form.cleaned_data.get('question_text') and not question_form.cleaned_data.get('id'):
                question_formset.forms.remove(question_form)

        # Проверьте валидность формы
        if form.is_valid() and question_formset.is_valid():
            saved_test = form.save()

            for question_form in question_formset:
                if question_form.cleaned_data.get('DELETE'):
                    try:
                        question_form.instance.delete()
                    except ValueError as e:
                        messages.error(request, f"Ошибка при удалении вопроса: {str(e)}")
                        return HttpResponseRedirect(
                            reverse('teacher:edit_test',
                                    kwargs={'slug': course.slug, 'module_id': module_id, 'pk': test.id}))
                else:
                    # Проверяем, чтобы текст вопроса был не пустым
                    if question_form.cleaned_data.get('question_text'):
                        question_instance = question_form.save(commit=False)
                        question_instance.test = saved_test
                        question_instance.save()

                        answer_formset = AnswerChoiceFormSet(
                            request.POST, instance=question_instance, prefix=f'answers-{question_instance.id}'
                        )
                        answer_formset.full_clean()
                        print("Ошибки answer_formset после full_clean:", answer_formset.errors)

                        if answer_formset.is_valid():
                            for answer_form in answer_formset:
                                if not answer_form.is_valid():
                                    print(
                                        f"Ошибки для ответа с текстом '{answer_form.cleaned_data.get('choice_text', 'не указан')}'",
                                        answer_form.errors)
                                # Проверяем, чтобы текст ответа был не пустым
                                print(answer_form)
                                if answer_form.cleaned_data.get('choice_text'):
                                    answer_form.save()
                                else:
                                    print(f"Пустой ответ для вопроса {question_instance}")
                                    print(f"Пустой ответ для вопроса {answer_form.errors}")
                        else:
                            print(f"Ошибки формы ответов для вопроса {question_instance.id}:", answer_formset.errors)
                            for error in answer_formset.errors:
                                messages.error(request, f"Ошибка в ответах: {error}")
                    else:
                        print("Пустой вопрос найден")

            messages.success(request, "Тест успешно обновлён.")
            return HttpResponseRedirect(
                reverse('teacher:edit_test', kwargs={'slug': course.slug, 'module_id': module_id, 'pk': test.id}))
        else:
            messages.error(request, "Исправьте ошибки в форме.")
            print("Ошибки формы теста:", form.errors)
            print("Ошибки формы вопросов:", question_formset.errors)

    else:
        form = TestForm(instance=test)
        question_formset = QuestionFormSet(instance=test, prefix='questions')

    # Создаём список, где каждый элемент — это пара (форма вопроса, formset для ответов)
    question_answer_pairs = []
    for question_form in question_formset:
        question = question_form.instance
        answer_formset = AnswerChoiceFormSet(instance=question, prefix=f'answers-{question.id}')
        question_answer_pairs.append((question_form, answer_formset))

    print(form)
    print(question_answer_pairs)

    context = {
        'form': form,
        'question_answer_pairs': question_answer_pairs,
        'title': f"Изменить тестирование: {test.title}",
    }
    return render(request, 'teacher/crud/change/testing_change_teacher.html', context)















