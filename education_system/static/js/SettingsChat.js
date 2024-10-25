// Убедитесь, что ваши переменные объявлены только один раз
const roomName = JSON.parse(document.getElementById('room_name').textContent);
const userEmail = JSON.parse(document.getElementById('email').textContent);
const userAvatar = JSON.parse(document.getElementById('avatar_url').textContent);
const userRole = JSON.parse(document.getElementById('role').textContent);

let chatSocket; // Объявляем переменную здесь
let reconnectAttempts = 0;
const maxReconnectAttempts = 10;

createChatSocket(); // Инициализация WebSocket

function createChatSocket() {
    if (chatSocket && chatSocket.readyState !== WebSocket.CLOSED) {
        chatSocket.close();
    }

    // Используйте localhost, если это локальная разработка
    chatSocket = new WebSocket('ws://' + window.location.host + '/ws/rooms/' + roomName + '/');

    chatSocket.onmessage = handleMessage;
    chatSocket.onclose = handleClose;
    chatSocket.onerror = handleError;
    chatSocket.onopen = () => {
        reconnectAttempts = 0; // Сбросить счетчик на успешном подключении
        console.log('WebSocket connection established');
    };
}

function handleMessage(e) {
    const data = JSON.parse(e.data);
    if (data.message) {
        const html = `
            <div class="message__user">
                <img src="${data.avatar}" class="message__image__user">
                <div>
                    <p class="message__userEmail">${data.email} (${userRole})</p>
                    <p class="message__content">${data.message}</p>
                    <data class="message__data__right">${data.date_added}</data>
                </div>
            </div>
        `;
        document.querySelector('#chat__message').innerHTML += html;
        scrollToBottom();
    }
}

function handleClose() {
    console.log('Chat socket closed. Attempting to reconnect...');
    if (reconnectAttempts < maxReconnectAttempts) {
        setTimeout(() => {
            reconnectAttempts++;
            console.log(`Reconnect attempt #${reconnectAttempts}`);
            createChatSocket();
        }, 1000 * reconnectAttempts); // Экспоненциальная задержка
    } else {
        console.error('Max reconnect attempts reached.');
    }
}

function handleError(error) {
    console.error('WebSocket error:', error);
}

document.querySelector('#chat__message__input__submit').onclick = function (e) {
    e.preventDefault();

    const messageInputDom = document.querySelector('#chat__message__input__text');
    const message = messageInputDom.value.trim();

    if (message.length > 0 && chatSocket.readyState === WebSocket.OPEN) {
        const dateAdded = new Date().toLocaleString('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: 'numeric',
            minute: 'numeric'
        });
        chatSocket.send(JSON.stringify({
            'message': message,
            'date_added': dateAdded,
            'email': userEmail,
            'avatar': userAvatar,
            'room': roomName
        }));
        messageInputDom.value = '';
    } else if (chatSocket.readyState !== WebSocket.OPEN) {
        alert('Соединение с сервером отсутствует. Попробуйте позже.');
    } else {
        alert('Введите сообщение!');
    }
}

function scrollToBottom() {
    const chatMessageDiv = document.querySelector('#chat__message');
    chatMessageDiv.scrollTop = chatMessageDiv.scrollHeight;
}

scrollToBottom();
