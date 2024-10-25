document.addEventListener("DOMContentLoaded", function () {
    // Найти кнопку добавления вопросов
    var addQuestionButton = document.getElementById("add-question");

    if (addQuestionButton) {
        addQuestionButton.addEventListener("click", function () {
            // Клонировать шаблон вопроса
            var questionTemplate = document.getElementById("question-template");
            var newQuestion = questionTemplate.cloneNode(true);
            newQuestion.style.display = "block";

            // Добавить в основной формсет
            var questionsContainer = document.getElementById("questions-container");
            questionsContainer.appendChild(newQuestion);

            // Обновить индекс управления для формы
            var totalForms = document.getElementById("id_form-TOTAL_FORMS");
            totalForms.value = parseInt(totalForms.value) + 1;

            // Добавить обработчик для удаления вопроса
            var removeQuestionButton = newQuestion.querySelector(".remove-question");
            removeQuestionButton.addEventListener("click", function () {
                questionsContainer.removeChild(newQuestion);
                totalForms.value = parseInt(totalForms.value) - 1;
            });
        });
    }
});