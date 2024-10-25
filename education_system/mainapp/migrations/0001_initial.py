# Generated by Django 5.1.2 on 2024-10-24 07:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalModuleSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('task_condition', models.TextField(blank=True, null=True, verbose_name='Условие задания')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активность')),
            ],
            options={
                'verbose_name': 'Финальное занятие модуля',
                'verbose_name_plural': 'Финальные занятия модулей',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Название')),
                ('slug', models.SlugField(max_length=128, unique=True, verbose_name='Название на английском')),
                ('desc', models.TextField(verbose_name='Описание')),
                ('complexity', models.IntegerField(choices=[(0, 'Easy'), (1, 'Medium'), (2, 'Difficult')], default=0, verbose_name='Уровень сложности')),
                ('images', models.ImageField(default='course/images/default.png', upload_to='course/images/', verbose_name='Изображение')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активность')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата начала')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания')),
                ('status', models.CharField(choices=[('PL', 'Запланирован'), ('AC', 'Активен'), ('CO', 'Завершен'), ('CA', 'Отменен')], default='AC', max_length=2)),
                ('students', models.ManyToManyField(blank=True, related_name='courses', related_query_name='course_students', to=settings.AUTH_USER_MODEL, verbose_name='Студенты')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses_teacher', to=settings.AUTH_USER_MODEL, verbose_name='Преподаватель')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FinalCourseSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('task_condition', models.TextField(blank=True, null=True, verbose_name='Условие задания')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активность')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='final_sessions', to='mainapp.course', verbose_name='Курс')),
            ],
            options={
                'verbose_name': 'Финальное занятие курса',
                'verbose_name_plural': 'Финальные занятия курсов',
            },
        ),
        migrations.CreateModel(
            name='FinalSessionResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий студента')),
                ('feedback', models.TextField(blank=True, null=True, verbose_name='Комментарии преподавателя')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')),
                ('final_course_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='mainapp.finalcoursesession', verbose_name='Финальное занятие курса')),
                ('final_module_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='mainapp.finalmodulesession', verbose_name='Финальное занятие модуля')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='final_responses', to=settings.AUTH_USER_MODEL, verbose_name='Студент')),
            ],
            options={
                'verbose_name': 'Ответ на финальное занятие',
                'verbose_name_plural': 'Ответы на финальные занятия',
            },
        ),
        migrations.CreateModel(
            name='FinalSessionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='final_session_submissions/', verbose_name='Файл с ответом')),
                ('final_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='mainapp.finalsessionresponse', verbose_name='финальное занятие')),
            ],
            options={
                'verbose_name': 'Файл домашнего задания',
                'verbose_name_plural': 'Файлы домашних заданий',
            },
        ),
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(blank=True, null=True, verbose_name='Ответ')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Задание выполнено')),
                ('feedback', models.TextField(blank=True, null=True, verbose_name='Обратная связь')),
                ('submitted_by', models.ManyToManyField(blank=True, related_name='submitted_homework', to=settings.AUTH_USER_MODEL, verbose_name='Пользователи, сдавшие задание')),
            ],
            options={
                'verbose_name': 'Домашнее задание',
                'verbose_name_plural': 'Домашние задания',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='HomeworkFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='homework_submissions/', verbose_name='Файл с ответом')),
                ('homework', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='mainapp.homework', verbose_name='Домашнее задание')),
            ],
            options={
                'verbose_name': 'Файл домашнего задания',
                'verbose_name_plural': 'Файлы домашних заданий',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Название модуля')),
                ('desc', models.TextField(blank=True, default='', null=True, verbose_name='Описание модуля')),
                ('open', models.BooleanField(db_index=True, default=True, verbose_name='Активность')),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='active', max_length=10, verbose_name='Статус')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='Позиция модуля')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата начала')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания')),
                ('completed_by', models.ManyToManyField(blank=True, related_name='completed_modules', to=settings.AUTH_USER_MODEL, verbose_name='Пользователи, прошедшие модуль')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_course', to='mainapp.course', verbose_name='Курс')),
            ],
            options={
                'verbose_name': 'Модуль',
                'verbose_name_plural': 'Модули',
                'ordering': ['position'],
            },
        ),
        migrations.AddField(
            model_name='finalmodulesession',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='final_sessions', to='mainapp.module', verbose_name='Модуль'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Рейтинг')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='mainapp.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название занятия')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание занятия')),
                ('homework_condition', models.TextField(blank=True, null=True, verbose_name='Условие домашнего задания')),
                ('webinar_link', models.URLField(blank=True, null=True, verbose_name='Ссылка на вебинар')),
                ('presentation', models.FileField(blank=True, null=True, upload_to='presentations/', verbose_name='Презентация')),
                ('annotation', models.FileField(blank=True, null=True, upload_to='annotations/', verbose_name='Аннотация')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активность')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='mainapp.module', verbose_name='Модуль')),
            ],
            options={
                'verbose_name': 'Занятие',
                'verbose_name_plural': 'Занятия',
                'ordering': ['module'],
            },
        ),
        migrations.AddField(
            model_name='homework',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homework_assignments', to='mainapp.session', verbose_name='Занятие'),
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название теста')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание теста')),
                ('duration', models.PositiveIntegerField(default=60, verbose_name='Длительность (минуты)')),
                ('passing_score', models.PositiveIntegerField(default=50, verbose_name='Проходной балл')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Активность')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_tests', to='mainapp.course', verbose_name='Курс')),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='module_tests', to='mainapp.module', verbose_name='Модуль')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
            },
        ),
        migrations.CreateModel(
            name='TestQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField(verbose_name='Текст вопроса')),
                ('question_type', models.CharField(choices=[('single', 'Один вариант ответа'), ('multiple', 'Несколько вариантов ответа'), ('text', 'Текстовый ответ')], default='single', max_length=10, verbose_name='Тип вопроса')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='mainapp.test', verbose_name='Тест')),
            ],
            options={
                'verbose_name': 'Вопрос теста',
                'verbose_name_plural': 'Вопросы теста',
            },
        ),
        migrations.CreateModel(
            name='TestAnswerChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200, verbose_name='Вариант ответа')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Правильный ответ')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='mainapp.testquestion', verbose_name='Вопрос')),
            ],
        ),
        migrations.CreateModel(
            name='TestResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(default=0, verbose_name='Баллы')),
                ('submitted_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_responses', to=settings.AUTH_USER_MODEL, verbose_name='Студент')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='mainapp.test', verbose_name='Тест')),
            ],
            options={
                'verbose_name': 'Ответ на тест',
                'verbose_name_plural': 'Ответы на тесты',
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_answer', models.TextField(blank=True, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.testquestion')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='mainapp.testresponse')),
                ('selected_choices', models.ManyToManyField(blank=True, to='mainapp.testanswerchoice')),
            ],
        ),
    ]