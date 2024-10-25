from django import forms
from django.forms import inlineformset_factory

from mainapp.models import Course, Review, FinalCourseSession
from mainapp.models import Module, FinalModuleSession, FinalSessionResponse, FinalSessionFile
from mainapp.models import FinalSessionFile
from mainapp.models import Session, Homework, HomeworkFile
from mainapp.models import Test, TestQuestion, TestResponse, TestAnswerChoice, UserAnswer


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'name',
            'slug',
            'desc',
            'complexity',
            'images',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'course_form'


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = (
            'name',
            'desc',
            'open',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'module_form'


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = (
            'title',
            'description',
            'homework_condition',
            'webinar_link',
            'presentation',
            'annotation',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'lesson_form'


class FinalModuleSessionForm(forms.ModelForm):
    class Meta:
        model = FinalModuleSession
        fields = (
            'title',
            'task_condition',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'final_session_form'


class FinalCourseSessionForm(forms.ModelForm):
    class Meta:
        model = FinalCourseSession
        fields = (
            'title',
            'task_condition',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'final_session_form'

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'duration', 'passing_score', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название теста'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание теста'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Продолжительность', 'min': 1}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Проходной балл', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TestQuestionForm(forms.ModelForm):
    class Meta:
        model = TestQuestion
        fields = ['question_text', 'question_type']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Текст вопроса'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
        }

class TestAnswerChoiceForm(forms.ModelForm):
    class Meta:
        model = TestAnswerChoice
        fields = ['choice_text', 'is_correct']
        widgets = {
            'choice_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Вариант ответа'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        super().clean()
        is_correct = self.cleaned_data.get('is_correct')
        question = self.instance.question

        if question.question_type == TestQuestion.SINGLE_CHOICE and is_correct:
            if question.choices.filter(is_correct=True).exclude(id=self.instance.id).exists():
                raise forms.ValidationError(_("Для вопросов с одним вариантом ответа может быть только один правильный ответ."))


QuestionFormSet = inlineformset_factory(Test, TestQuestion, form=TestQuestionForm, extra=0, can_delete=True)
AnswerChoiceFormSet = inlineformset_factory(TestQuestion, TestAnswerChoice, form=TestAnswerChoiceForm, extra=0, can_delete=True)


class TestFullForm(forms.Form):
    test_form = TestForm(prefix='test')
    question_formset = QuestionFormSet(prefix='questions')
    answer_choice_formset = AnswerChoiceFormSet(prefix='answers')

