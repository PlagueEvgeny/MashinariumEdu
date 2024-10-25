from django.db import models
from django.utils.translation import gettext_lazy as _
from authapp.models import UserProfile
from django.db.models import Avg
from django.utils import timezone


class BaseFinalSession(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Название"))
    task_condition = models.TextField(verbose_name=_("Условие задания"), blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Активность"))

    class Meta:
        abstract = True  # Делает класс абстрактным


class Course(models.Model):
    class Complexity(models.IntegerChoices):
        EASY = 0, _('Easy')
        MEDIUM = 1, _('Medium')
        DIFFICULT = 2, _('Difficult')

    class CourseStatus(models.TextChoices):
        PLANNED = 'PL', _('Запланирован')
        ACTIVE = 'AC', _('Активен')
        COMPLETED = 'CO', _('Завершен')
        CANCELLED = 'CA', _('Отменен')

    name = models.CharField(max_length=128, verbose_name=_("Название"))
    slug = models.SlugField(max_length=128, verbose_name=_("Название на английском"), unique=True)
    desc = models.TextField(verbose_name=_("Описание"))
    complexity = models.IntegerField(verbose_name=_("Уровень сложности"),
                                     choices=Complexity.choices, default=Complexity.EASY)
    images = models.ImageField(verbose_name=_("Изображение"), upload_to='course/images/',
                               default='course/images/default.png')
    teacher = models.ForeignKey(UserProfile, verbose_name=_("Преподаватель"),
                                on_delete=models.CASCADE, related_name='courses_teacher')
    students = models.ManyToManyField(UserProfile, verbose_name=_("Студенты"),
                                      related_name='courses', related_query_name="course_students", blank=True)
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Активность"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    start_date = models.DateTimeField(verbose_name=_("Дата начала"), null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=_("Дата окончания"), null=True, blank=True)
    status = models.CharField(max_length=2, choices=CourseStatus.choices, default=CourseStatus.ACTIVE)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")

    def __str__(self):
        return self.name

    def get_student_count(self):
        return self.students.count()

    def average_rating(self):
        if self.reviews.count() == 0:
            return None
        return self.reviews.aggregate(Avg('rating'))['rating__avg']


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(verbose_name=_("Рейтинг"), choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(verbose_name=_("Комментарий"), blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")

    def __str__(self):
        return f'Отзыв для {self.course.name} от {self.student.email}'


class Module(models.Model):
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('canceled', _('Canceled')),
    )

    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        on_delete=models.CASCADE,
        related_name='module_course'
    )
    name = models.CharField(max_length=128, verbose_name="Название модуля")
    desc = models.TextField(verbose_name="Описание модуля", default='', blank=True, null=True)
    open = models.BooleanField(default=True, db_index=True, verbose_name=_("Активность"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    position = models.PositiveIntegerField(verbose_name="Позиция модуля", default=0)
    completed_by = models.ManyToManyField(
        UserProfile,
        verbose_name="Пользователи, прошедшие модуль",
        related_name='completed_modules',
        blank=True
    )
    start_date = models.DateTimeField(verbose_name="Дата начала", null=True, blank=True)
    end_date = models.DateTimeField(verbose_name="Дата окончания", null=True, blank=True)

    class Meta:
        ordering = ["position"]
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"

    def __str__(self):
        return self.name

    def is_active(self):
        """Проверяет, открыт ли модуль на текущий момент."""
        now = timezone.now()
        return self.open and (self.start_date is None or self.start_date <= now) and (
                self.end_date is None or self.end_date >= now)


class Session(models.Model):
    module = models.ForeignKey(
        Module,
        verbose_name=_("Модуль"),
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    title = models.CharField(verbose_name=_("Название занятия"), max_length=200)  # Новое поле для названия занятия
    description = models.TextField(verbose_name=_("Описание занятия"), blank=True, null=True)  # Новое поле для описания
    homework_condition = models.TextField(verbose_name=_("Условие домашнего задания"), blank=True,
                                          null=True)  # Условие домашнего задания
    webinar_link = models.URLField(verbose_name=_("Ссылка на вебинар"), max_length=200, blank=True, null=True)
    presentation = models.FileField(verbose_name=_("Презентация"), upload_to='presentations/', blank=True, null=True)
    annotation = models.FileField(verbose_name=_("Аннотация"), upload_to='annotations/', blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Активность"))

    class Meta:
        verbose_name = _("Занятие")
        verbose_name_plural = _("Занятия")
        ordering = ["module"]

    def __str__(self):
        return f"{self.title} для модуля: {self.module.name}"


class Homework(models.Model):
    session = models.ForeignKey(
        Session,
        verbose_name=_("Занятие"),
        on_delete=models.CASCADE,
        related_name='homework_assignments'
    )
    answer = models.TextField(verbose_name=_("Ответ"), blank=True, null=True)
    submitted_by = models.ManyToManyField(
        UserProfile,
        verbose_name=_("Пользователи, сдавшие задание"),
        related_name='submitted_homework',
        blank=True
    )
    is_completed = models.BooleanField(default=False, verbose_name=_("Задание выполнено"))
    feedback = models.TextField(verbose_name=_("Обратная связь"), blank=True, null=True)

    class Meta:
        verbose_name = _("Домашнее задание")
        verbose_name_plural = _("Домашние задания")
        ordering = ["id"]

    def __str__(self):
        return f"для занятия: {self.session.module.name}"


class HomeworkFile(models.Model):
    homework = models.ForeignKey(
        Homework,
        verbose_name=_("Домашнее задание"),
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(verbose_name=_("Файл с ответом"), upload_to='homework_submissions/')

    class Meta:
        verbose_name = _("Файл домашнего задания")
        verbose_name_plural = _("Файлы домашних заданий")

    def __str__(self):
        return f"Файл для задания: {self.homework.session.title}"


class FinalModuleSession(BaseFinalSession):
    module = models.ForeignKey(
        Module,
        verbose_name=_("Модуль"),
        on_delete=models.CASCADE,
        related_name='final_sessions'
    )

    class Meta:
        verbose_name = _("Финальное занятие модуля")
        verbose_name_plural = _("Финальные занятия модулей")

    def __str__(self):
        return self.title


class FinalCourseSession(BaseFinalSession):
    course = models.ForeignKey(
        Course,
        verbose_name=_("Курс"),
        on_delete=models.CASCADE,
        related_name='final_sessions'
    )

    class Meta:
        verbose_name = _("Финальное занятие курса")
        verbose_name_plural = _("Финальные занятия курсов")

    def __str__(self):
        return self.title


class FinalSessionResponse(models.Model):
    final_module_session = models.ForeignKey(
        FinalModuleSession,
        verbose_name=_("Финальное занятие модуля"),
        on_delete=models.CASCADE,
        related_name='responses',
        null=True,
        blank=True  # Позволяет пустое значение, если это задание курса
    )
    final_course_session = models.ForeignKey(
        FinalCourseSession,
        verbose_name=_("Финальное занятие курса"),
        on_delete=models.CASCADE,
        related_name='responses',
        null=True,
        blank=True  # Позволяет пустое значение, если это задание модуля
    )
    student = models.ForeignKey(
        UserProfile,
        verbose_name=_("Студент"),
        on_delete=models.CASCADE,
        related_name='final_responses'
    )
    comment = models.TextField(verbose_name=_("Комментарий студента"), blank=True, null=True)
    feedback = models.TextField(verbose_name=_("Комментарии преподавателя"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата отправки"))

    class Meta:
        verbose_name = _("Ответ на финальное занятие")
        verbose_name_plural = _("Ответы на финальные занятия")

    def __str__(self):
        if self.final_module_session:
            return f"Ответ студента {self.student} на занятие {self.final_module_session.title}"
        if self.final_course_session:
            return f"Ответ студента {self.student} на занятие {self.final_course_session.title}"
        return "Ответ студента без привязки к занятию"


class FinalSessionFile(models.Model):
    final_session = models.ForeignKey(
        FinalSessionResponse,
        verbose_name=_("финальное занятие"),
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(verbose_name=_("Файл с ответом"), upload_to='final_session_submissions/')

    class Meta:
        verbose_name = _("Файл домашнего задания")
        verbose_name_plural = _("Файлы домашних заданий")

    def __str__(self):
        if final_module_session.final_module_session:
            return f"Файл для задания: {self.final_session.final_module_session.title}"
        else:
            return f"Файл для задания: {self.final_session.final_course_session.title}"


class Test(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Название теста"))
    description = models.TextField(verbose_name=_("Описание теста"), blank=True, null=True)
    duration = models.PositiveIntegerField(verbose_name=_("Длительность (минуты)"), default=60)
    passing_score = models.PositiveIntegerField(verbose_name=_("Проходной балл"), default=50)
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Активность"))
    module = models.ForeignKey(
        Module,
        verbose_name=_("Модуль"),
        on_delete=models.CASCADE,
        related_name='module_tests',
        blank=True,
        null=True
    )
    course = models.ForeignKey(
        Course,
        verbose_name=_("Курс"),
        on_delete=models.CASCADE,
        related_name='course_tests',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Тест")
        verbose_name_plural = _("Тесты")

    def __str__(self):
        return self.title

    def clean(self):
        if not self.module and not self.course:
            raise ValidationError(_("Тест должен быть привязан либо к модулю, либо к курсу."))


class TestQuestion(models.Model):
    SINGLE_CHOICE = 'single'
    MULTIPLE_CHOICE = 'multiple'
    TEXT_ANSWER = 'text'

    QUESTION_TYPE_CHOICES = [
        (SINGLE_CHOICE, _("Один вариант ответа")),
        (MULTIPLE_CHOICE, _("Несколько вариантов ответа")),
        (TEXT_ANSWER, _("Текстовый ответ")),
    ]

    test = models.ForeignKey(
        Test,
        verbose_name=_("Тест"),
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField(verbose_name=_("Текст вопроса"))
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default=SINGLE_CHOICE,
        verbose_name=_("Тип вопроса")
    )

    class Meta:
        verbose_name = _("Вопрос теста")
        verbose_name_plural = _("Вопросы теста")

    def __str__(self):
        return f"Вопрос: {self.question_text}"

class TestAnswerChoice(models.Model):
    question = models.ForeignKey(
        TestQuestion,
        verbose_name=_("Вопрос"),
        on_delete=models.CASCADE,
        related_name='choices'
    )
    choice_text = models.CharField(max_length=200, verbose_name=_("Вариант ответа"))
    is_correct = models.BooleanField(default=False, verbose_name=_("Правильный ответ"))

    def __str__(self):
        return f"Вариант ответа: {self.choice_text}"

    def clean(self):
        if self.question.question_type == TestQuestion.SINGLE_CHOICE and self.is_correct:
            if self.question.choices.filter(is_correct=True).exists():
                raise ValidationError(
                    _("Для вопросов с одним вариантом ответа может быть только один правильный ответ."))


class TestResponse(models.Model):
    test = models.ForeignKey(
        Test,
        verbose_name=_("Тест"),
        on_delete=models.CASCADE,
        related_name='responses'
    )
    student = models.ForeignKey(
        UserProfile,
        verbose_name=_("Студент"),
        on_delete=models.CASCADE,
        related_name='test_responses'
    )
    score = models.PositiveIntegerField(verbose_name=_("Баллы"), default=0)
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата отправки"))

    class Meta:
        verbose_name = _("Ответ на тест")
        verbose_name_plural = _("Ответы на тесты")

    def __str__(self):
        return f"Ответ студента {self.student} на тест {self.test.title}"


class UserAnswer(models.Model):
    response = models.ForeignKey(TestResponse, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(TestAnswerChoice, blank=True)  # Для многовариантных вопросов
    text_answer = models.TextField(null=True, blank=True)  # Для текстовых вопросов

    def __str__(self):
        return f"Ответ на вопрос: {self.question.question_text}"
