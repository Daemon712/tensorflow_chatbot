var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function () {
    $messages.mCustomScrollbar();
    loadMessages();
});

function loadMessages() {
    $.get(window.location.pathname + '/message'
    ).done(function (messages) {
        for (let message of messages) {
            if (message['author'] === -1) {
                insertBotMessage(message.text)
            } else {
                insertUserMessage(message.text)
            }
        }

        updateScrollbar();

    }).fail(function () {
        alert('Ошибка :(');
    });
}

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function setDate() {
    d = new Date();
    if (m !== d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
}

function insertMessage() {
    let messageInput = $('.message-input');
    let text = messageInput.val();
    if ($.trim(text) === '') {
        return false;
    }
    insertUserMessage(text).addClass('new');
    // setDate();
    messageInput.val(null);
    updateScrollbar();
    interact(text);
}

$('.message-submit').click(function () {
    insertMessage();
});

$(window).on('keydown', function (e) {
    if (e.which === 13) {
        insertMessage();
        return false;
    }
});


function interact(message) {
    $('<div class="message loading new"><figure class="avatar"><img src="/static/res/bot_pic.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    $.post(window.location.pathname + '/message', {
        msg: message,
    }).done(function (reply) {
        $('.message.loading').remove();
        insertBotMessage(reply['text']).addClass('new');
        // setDate();
        updateScrollbar();

    }).fail(function () {
        alert('Ошибка :(');
    });
}

function insertUserMessage(text) {
    return $('<div class="message message-personal">' + text + '</div>').appendTo($('.mCSB_container'))
}

function insertBotMessage(text) {
    return $('<div class="message new"><figure class="avatar"><img src="/static/res/bot_pic.png" /></figure>' + text + '</div>').appendTo($('.mCSB_container'));
}