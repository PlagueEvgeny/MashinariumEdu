import nested_admin

from django.contrib import admin
from mainapp.models import Course, Review, FinalCourseSession
from mainapp.models import Module, FinalModuleSession, FinalSessionResponse, FinalSessionFile
from mainapp.models import FinalSessionFile
from mainapp.models import Session, Homework, HomeworkFile
from mainapp.models import Test, TestQuestion, TestResponse, TestAnswerChoice, UserAnswer
from mainapp.forms import HomeworkForm, FinalSessionResponseForm, TestResponseForm


admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Session)
admin.site.register(Homework)
admin.site.register(HomeworkFile)
admin.site.register(FinalModuleSession)
admin.site.register(FinalCourseSession)
admin.site.register(FinalSessionResponse)
admin.site.register(TestResponse)
admin.site.register(UserAnswer)

# Инлайн для вариантов ответов
class TestAnswerChoiceInline(nested_admin.NestedTabularInline):
    model = TestAnswerChoice
    extra = 2  # Количество пустых форм для добавления вариантов ответов
    fields = ['choice_text', 'is_correct']  # Добавляем поле для выбора правильного ответа
    min_num = 1  # Минимум 1 вариант
    max_num = 10  # Максимум 10 вариантов

# Инлайн для вопросов
class TestQuestionInline(nested_admin.NestedStackedInline):
    model = TestQuestion
    extra = 1  # Количество пустых форм для добавления вопросов
    inlines = [TestAnswerChoiceInline]  # Включаем inline для вариантов ответов

    def get_fields(self, request, obj=None):
        """Настраиваем отображение полей в зависимости от типа вопроса"""
        fields = ['question_text', 'question_type']
        return fields

    def get_inline_instances(self, request, obj=None):
        """Скрываем inline для вариантов ответов, если тип вопроса - текстовый"""
        if isinstance(obj, TestQuestion) and obj.question_type == TestQuestion.TEXT_ANSWER:
            return []  # Не отображаем варианты ответов для текстовых вопросов
        return super().get_inline_instances(request, obj)

# Админка для тестов
@admin.register(Test)
class TestAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'description', 'duration', 'passing_score', 'is_active')
    inlines = [TestQuestionInline]  # Включаем inline для вопросовлючаем inline для вопросов