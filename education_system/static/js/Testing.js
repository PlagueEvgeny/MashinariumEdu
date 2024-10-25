document.addEventListener('DOMContentLoaded', function () {
    let questionIndex = parseInt(document.querySelectorAll('.question-form').length);
    let answerIndex = [];

    // Инициализация answerIndex для существующих вопросов
    document.querySelectorAll('.question-form').forEach((question, idx) => {
        answerIndex[idx] = document.querySelectorAll(`[data-question-id="${idx}"] .answer-form`).length;

        // Скрываем чекбоксы удаления для вопросов
        const deleteCheckbox = document.querySelector(`input[name="questions-${idx}-DELETE"]`);
        if (deleteCheckbox) {
            deleteCheckbox.closest('p').style.display = 'none';  // Скрываем родительский элемент с чекбоксом
        }
    });

    // Добавление нового вопроса
    document.getElementById('add-question').addEventListener('click', function () {
        const questionTemplate = document.getElementById('question-template').innerHTML.replace(/__prefix__/g, questionIndex);
        document.getElementById('questions-container').insertAdjacentHTML('beforeend', questionTemplate);

        // Увеличиваем значение TOTAL_FORMS для вопросов
        const totalForms = document.querySelector('#id_questions-TOTAL_FORMS');
        totalForms.value = parseInt(totalForms.value) + 1;

        // Инициализируем индекс для ответов для нового вопроса
        answerIndex[questionIndex] = 0;
        questionIndex++;
    });

    // Удаление вопроса
    document.getElementById('questions-container').addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-question')) {
            const questionForm = event.target.closest('.question-form');
            const questionId = questionForm.dataset.questionId;

            // Проверяем, существует ли поле с вопросом
            const deleteInput = document.createElement('input');
            deleteInput.type = 'hidden';
            deleteInput.name = `questions-${questionId}-DELETE`; // Создаем скрытое поле для удаления
            deleteInput.value = 'on'; // Указываем, что нужно удалить

            questionForm.appendChild(deleteInput); // Добавляем это скрытое поле в форму

            // Удаляем форму вопроса из DOM
            questionForm.style.display = 'none'; // Вместо удаления из DOM, просто скрываем элемент
        }
    });


    // Добавление ответа к конкретному вопросу
    document.getElementById('questions-container').addEventListener('click', function (event) {
        if (event.target.classList.contains('add-answer')) {
            const questionElement = event.target.closest('.question-form');
            const questionId = questionElement.getAttribute('data-question-id');

            // Проверяем, есть ли правильный questionId
            console.log("Добавление ответа к вопросу с ID:", questionId);  // Отладка
            console.log("Текущий индекс ответа для этого вопроса:", answerIndex[questionId]);  // Отладка

            if (!answerIndex[questionId]) {
                answerIndex[questionId] = 0;  // Если индекс не установлен, инициализируем его
                console.log("Инициализация answerIndex для questionId:", questionId);  // Отладка
            }

            const answerContainer = questionElement.querySelector('.answer-container');

            const answerTemplate = document.getElementById('answer-template').innerHTML.replace(/__prefix__/g, `${questionId}-${answerIndex[questionId]}`);
            answerContainer.insertAdjacentHTML('beforeend', answerTemplate);

            // Увеличиваем индекс ответов для конкретного вопроса
            answerIndex[questionId]++;
        }
    });

    // Удаление ответа
    document.getElementById('questions-container').addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-answer')) {
            const answerForm = event.target.closest('.answer-form');

            // Удаляем форму ответа из DOM
            answerForm.remove();
        }
    });
    document.getElementById('test-form').addEventListener('submit', function (event) {
        // Удаляем пустые ответы
        document.querySelectorAll('.answer-form input[type="text"]').forEach(function (input) {
            if (!input.value.trim()) {
                input.closest('.answer-form').remove();
            }
        });

        // Удаляем пустые вопросы
        document.querySelectorAll('.question-form textarea').forEach(function (textarea) {
            if (!textarea.value.trim()) {
                textarea.closest('.question-form').remove();
            }
        });
    });
});
