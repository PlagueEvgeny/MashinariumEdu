from django import forms
from .models import Homework, FinalSessionResponse, TestQuestion


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['answer']  # Без файла здесь

    def __init__(self, *args, **kwargs):
        super(HomeworkForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = "Ответ"


class FinalSessionResponseForm(forms.ModelForm):
    class Meta:
        model = FinalSessionResponse
        fields = ['comment']  # Без файла здесь

    def __init__(self, *args, **kwargs):
        super(FinalSessionResponseForm, self).__init__(*args, **kwargs)
        self.fields['comment'].label = "Ответ"


class TestResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test')
        super().__init__(*args, **kwargs)

        for question in test.questions.all():
            if question.question_type == TestQuestion.SINGLE_CHOICE:
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.question_text,
                    choices=[(choice.id, choice.choice_text) for choice in question.choices.all()],
                    widget=forms.RadioSelect
                )
            elif question.question_type == TestQuestion.MULTIPLE_CHOICE:
                self.fields[f'question_{question.id}'] = forms.MultipleChoiceField(
                    label=question.question_text,
                    choices=[(choice.id, choice.choice_text) for choice in question.choices.all()],
                    widget=forms.CheckboxSelectMultiple
                )
            elif question.question_type == TestQuestion.TEXT_ANSWER:
                # Поле для текстового ответа
                self.fields[f'question_{question.id}'] = forms.CharField(
                    label=question.question_text,
                    widget=forms.Textarea(attrs={'rows': 3}),  # Добавление атрибута для текстовой области
                    required=False  # Текстовый ответ может быть необязательным
                )

    def add_widget_classes(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control textarea-custom'})
            else:
                field.widget.attrs.update({'class': 'form-control'})