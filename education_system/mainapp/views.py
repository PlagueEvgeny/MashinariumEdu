from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from mainapp.models import Course, Review, FinalCourseSession
from mainapp.models import Module, FinalModuleSession, FinalSessionResponse, FinalSessionFile
from mainapp.models import FinalSessionFile
from mainapp.models import Session, Homework, HomeworkFile
from mainapp.models import Test, TestQuestion, TestResponse, TestAnswerChoice, UserAnswer
from django.contrib import messages
from mainapp.forms import HomeworkForm, FinalSessionResponseForm, TestResponseForm
from django.http import HttpResponse, HttpResponseRedirect
from mainapp.utility.download_files import download_files


@login_required
def course_list(request):
    # Получаем все курсы
    all_courses = Course.objects.all()

    # Получаем курсы, которые купил пользователь
    purchased_courses = request.user.courses.all()  # Assuming 'course_student_related' is the related name for many-to-many relation

    # Исключаем купленные курсы из общего списка
    available_courses = all_courses.exclude(id__in=purchased_courses.values_list('id', flat=True))

    context = {
        'purchased_courses': purchased_courses,
        'available_courses': available_courses,
        "title": f"Курсы"
    }
    return render(request, 'mainapp/courses/course_list.html', context)


@login_required
def course_detail(request, slug):
    """Отображает детали курса. Если курс уже приобретен, показываем модуль, иначе показываем детали."""
    course = get_object_or_404(Course, slug=slug)

    if request.user in course.students.all():
        # Пользователь уже приобрел курс, перенаправляем его к модулю
        return redirect('main:purchased_course_detail', course_id=course.id)

    # Отображение деталей курса
    context = {
        'course': course,
        'reviews': course.reviews.all(),
        "title": f"Курс: {course.name}"
    }
    return render(request, 'mainapp/courses/course_detail.html', context)


@login_required
def purchased_course_detail(request, slug):
    # Получаем курс по slug
    course = get_object_or_404(Course, slug=slug)

    # Проверяем, имеет ли пользователь доступ к этому курсу
    if request.user not in course.students.all():
        messages.error(request, "У вас нет доступа к этому курсу.")
        return redirect('main:courses')  # Перенаправляем на страницу курсов, если нет доступа

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

    return render(request, 'mainapp/courses/purchased_course_detail.html', context)


def module_detail(request, slug, pk):
    # Получаем курс по Slug
    course = get_object_or_404(Course, slug=slug)
    # Получаем модуль по ID
    module = get_object_or_404(Module, course=course, id=pk)

    # Проверяем, имеет ли пользователь доступ к этому модулю
    if request.user not in module.completed_by.all():
        messages.error(request, "У вас нет доступа к этому модулю.")
        return redirect('main:courses')  # Перенаправляем на страницу курсов, если нет доступа

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
    return render(request, 'mainapp/courses/module_detail.html', context)


@login_required
def session(request, slug, module_id, pk):
    # Получаем модуль и занятие
    module = get_object_or_404(Module, course__slug=slug, id=module_id)
    session = get_object_or_404(Session, module=module, id=pk)

    # Проверяем, есть ли у пользователя доступ к модулю
    if request.user not in module.completed_by.all():
        messages.error(request, "У вас нет доступа к этому модулю.")
        return redirect('main:courses')  # Перенаправляем на страницу курсов, если нет доступа

    # Получаем все домашние задания для текущего занятия
    home_work = Homework.objects.filter(session=session, submitted_by=request.user)

    # Обработка запроса на скачивание файлов
    if request.GET.get('download_homework_id'):
        homework_id = request.GET.get('download_homework_id')
        homework = get_object_or_404(Homework, id=homework_id)
        return download_files(homework)

    if request.method == "POST":
        form = HomeworkForm(request.POST)

        if form.is_valid():
            # Сохраняем домашнее задание без добавления пользователя
            homework = form.save(commit=False)
            homework.session = session  # Привязываем к занятию
            homework.save()  # Сохраняем объект

            # Теперь добавляем пользователя к полю ManyToManyField
            homework.submitted_by.add(request.user)  # Добавляем пользователя к списку сдавших задание

            # Обработка загрузки файлов
            files = request.FILES.getlist('files')  # Получаем список файлов
            for file in files:
                HomeworkFile.objects.create(homework=homework, file=file)

            messages.success(request, 'Домашнее задание отправлено')
            return HttpResponseRedirect(reverse('main:session',
                                                kwargs={"slug": module.course.slug, 'module_id': module.id,
                                                        'pk': session.id}))

        messages.error(request, 'Домашнее задание не отправлено')

    form = HomeworkForm()
    context = {
        "form": form,
        "module": module,
        "session": session,
        "home_work": home_work,
        "title": f"Занятие: {session.title}",
    }

    return render(request, "mainapp/courses/session.html", context)


@login_required
def final_session_all(request, slug, pk, module_id=None):
    # Получаем курс по slug
    course = get_object_or_404(Course, slug=slug)

    # Если указан module_id, получаем модуль
    module = get_object_or_404(Module, course__slug=slug, id=module_id) if module_id else None

    # Пытаемся найти финальное занятие модуля или курса
    if module_id:
        final_session = FinalModuleSession.objects.filter(id=pk, module=module).first()
    else:
        final_session = FinalCourseSession.objects.filter(id=pk, course=course).first()

    if not final_session:
        messages.error(request, "Финальное занятие не найдено.")
        if module_id:
            return redirect('main:final_module_session', kwargs={"slug": course.slug, "module_id": module_id, 'pk': pk})
        else:
            return redirect('main:final_course_session', kwargs={"slug": course.slug, 'pk': pk})

    # Проверка доступа к курсу
    if request.user not in course.students.all():
        messages.error(request, "У вас нет доступа к этому занятию.")
        if module_id:
            return redirect('main:final_module_session', kwargs={"slug": course.slug, "module_id": module_id, 'pk': pk})
        else:
            return redirect('main:final_course_session', kwargs={"slug": course.slug, 'pk': pk})

    # Получаем ответы студента на финальные занятия (если есть)
    if module_id:
        final_responses = FinalSessionResponse.objects.filter(
            student=request.user,
            final_module_session=final_session,
        )
    else:
        final_responses = FinalSessionResponse.objects.filter(
            student=request.user,
            final_course_session=final_session,
        )

    # Обработка запроса на скачивание файлов
    if request.GET.get('download_response_id'):
        response_id = request.GET.get('download_response_id')
        final_response = get_object_or_404(FinalSessionResponse, id=response_id)
        if final_response.submitted_files:
            return download_files(final_response)
        else:
            messages.error(request, "Файлы не найдены для скачивания.")
            if module_id:
                return redirect('main:final_module_session',
                                kwargs={"slug": course.slug, "module_id": module_id, 'pk': pk})
            else:
                return redirect('main:final_course_session', kwargs={"slug": course.slug, 'pk': pk})

    if request.method == "POST":
        form = FinalSessionResponseForm(request.POST, request.FILES)

        if form.is_valid():
            # Создаем ответ на финальное задание
            final_response = form.save(commit=False)
            final_response.student = request.user  # Привязываем студента

            # Привязываем финальное занятие (модуль или курс)
            if module_id:
                final_response.final_module_session = final_session
            else:
                final_response.final_course_session = final_session

            final_response.save()  # Сохраняем ответ

            # Добавляем загруженные файлы
            files = request.FILES.getlist('files')  # Получаем список файлов
            for file in files:
                FinalSessionFile.objects.create(final_session=final_response, file=file)

            messages.success(request, 'Ответ на финальное занятие отправлен')
            if module_id:
                return HttpResponseRedirect(reverse('main:final_module_session',
                                                    kwargs={"slug": course.slug, "module_id": module_id,
                                                            'pk': final_session.id}))
            else:
                return HttpResponseRedirect(
                    reverse('main:final_course_session', kwargs={"slug": course.slug, 'pk': final_session.id}))

        messages.error(request, 'Ответ на финальное занятие не отправлен')

    form = FinalSessionResponseForm()
    context = {
        "form": form,
        "course": course,
        "module": module,
        "final_session": final_session,
        "final_responses": final_responses,
        "title": f"Контрольное занятие: {final_session.title}",
    }

    return render(request, "mainapp/courses/final_session.html", context)


@login_required
def take_test(request, slug, test_id, module_id=None):
    course = get_object_or_404(Course, slug=slug)

    if module_id:
        module = get_object_or_404(Module, course=course, id=module_id)
        test = get_object_or_404(Test, module=module, id=test_id, is_active=True)
    else:
        test = get_object_or_404(Test, course=course, id=test_id, is_active=True)

    questions = test.questions.all()

    # Проверка на существование уже пройденного теста
    existing_response = TestResponse.objects.filter(test=test, student=request.user).first()
    if existing_response:
        messages.info(request, "Вы уже проходили этот тест.")
        return redirect('main:test_result', response_id=existing_response.id)

    if request.method == "POST":
        form = TestResponseForm(request.POST, test=test)

        if form.is_valid():
            score = 0
            response = TestResponse.objects.create(
                test=test,
                student=request.user,
                score=0
            )

            for question in questions:
                # Обработка вопроса с одним вариантом ответа
                if question.question_type == TestQuestion.SINGLE_CHOICE:
                    submitted_answer_id = form.cleaned_data.get(f'question_{question.id}')
                    if submitted_answer_id:
                        try:
                            submitted_answer = TestAnswerChoice.objects.get(id=submitted_answer_id)
                            # Создаем объект UserAnswer и сохраняем выбранный ответ
                            user_answer = UserAnswer.objects.create(
                                response=response,
                                question=question,
                                text_answer=None
                            )
                            user_answer.selected_choices.set([submitted_answer])  # Сохраняем выбранный вариант

                            # Проверка правильности ответа
                            if submitted_answer.is_correct:
                                score += 1
                        except TestAnswerChoice.DoesNotExist:
                            pass  # В случае отсутствия ответа, ничего не делаем

                # Обработка вопроса с несколькими вариантами ответа
                elif question.question_type == TestQuestion.MULTIPLE_CHOICE:
                    submitted_answer_ids = form.cleaned_data.get(f'question_{question.id}', [])
                    if submitted_answer_ids:
                        submitted_answers = TestAnswerChoice.objects.filter(id__in=submitted_answer_ids)

                        user_answer = UserAnswer.objects.create(
                            response=response,
                            question=question,
                            text_answer=None
                        )
                        user_answer.selected_choices.set(submitted_answers)

                        # Получаем правильные ответы
                        correct_answers = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
                        submitted_answers_ids = set(map(int, submitted_answer_ids))
                        # Сравниваем наборы правильных и отправленных ответов
                        if submitted_answers_ids == correct_answers:
                            score += 1

                # Обработка текстового вопроса
                elif question.question_type == TestQuestion.TEXT_ANSWER:
                    submitted_answer = form.cleaned_data.get(f'question_{question.id}', '')

                    # Проверяем, что ответ не пустой или None
                    if submitted_answer.strip():  # Проверяем, что ответ не пустой
                        UserAnswer.objects.create(
                            response=response,
                            question=question,
                            text_answer=submitted_answer
                        )

                        correct_answer = question.choices.filter(is_correct=True).first()
                        if correct_answer:
                            correct_answer_text = correct_answer.choice_text
                            # Проверяем правильность текстового ответа
                            if submitted_answer.strip().lower() == correct_answer_text.strip().lower():
                                score += 1

                    else:
                        # Если ответа нет, можно создать запись с пустым ответом
                        UserAnswer.objects.create(
                            response=response,
                            question=question,
                            text_answer=""
                        )

            # Сохранение результата
            response.score = score
            response.save()

            # Оповещение пользователя о результате теста
            if score >= test.passing_score:
                messages.success(request, f"Тест пройден! Ваш результат: {score}/{len(questions)}")
            else:
                messages.error(request, f"Тест не пройден. Ваш результат: {score}/{len(questions)}")

            return redirect('main:test_result', response_id=response.id)

    else:
        form = TestResponseForm(test=test)

    context = {
        'test': test,
        'questions': questions,
        'form': form,
        "title": f"Тестирование: {test.title}",
    }

    return render(request, 'mainapp/tests/take_test.html', context)


@login_required
def test_result(request, response_id):
    response = get_object_or_404(TestResponse, id=response_id, student=request.user)
    questions_with_answers = []

    for question in response.test.questions.all():
        correct_answers = []

        if question.question_type == TestQuestion.SINGLE_CHOICE or question.question_type == TestQuestion.MULTIPLE_CHOICE or question.question_type == TestQuestion.TEXT_ANSWER:
            correct_answers = list(question.choices.filter(is_correct=True).values_list('choice_text', flat=True))


        elif question.question_type == TestQuestion.TEXT_ANSWER:
            correct_answers = list(question.choices.filter(is_correct=True).values_list('choice_text', flat=True))

        user_answer = response.user_answers.filter(question=question).first()

        questions_with_answers.append({
            'question': question,
            'correct_answers': correct_answers,
            'user_answer': user_answer
        })

    context = {
        'response': response,
        'test': response.test,
        'questions_with_answers': questions_with_answers,
        "title": f"Результаты теста: {response.test.title}",
    }

    return render(request, 'mainapp/tests/test_result.html', context)




