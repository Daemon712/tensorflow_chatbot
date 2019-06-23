let rates = ['content', 'organization', 'vocabulary', 'grammar'];
var sum = 0;
let feedback = {};
feedback['messages'] = {};
feedback['total_rate'] = 3;

function initSlider(rate) {
    sum += 2;
    feedback[rate + '_rate'] = 3;
    $("#" + rate + "-slider").slider({
        range: "min",
        value: 2,
        max: 4,
        slide: function (event, ui) {
            $("#" + rate + "-label").text(1 + ui.value);
            feedback[rate + '_rate'] = 1 + ui.value;
            let old = $(this).slider("value");
            let summary = $("#summary");
            sum = sum - old + ui.value;
            let avg = sum / rates.length;
            summary.text(avg + 1);
            $("#progressbar").progressbar("option", {value: avg});
            feedback['total_rate'] = 1 + avg;
        }
    });
}

function sendFeedback() {
    feedback['comment'] = $("#comment-area").val();
    $.ajax(window.location.pathname, {
        data: JSON.stringify(feedback),
        contentType: 'application/json',
        type: 'POST',
    }).done(function () {
        alert('Спасибо за отзыв!');
        window.location = "/";
    }).fail(function () {
        alert('Ошибка :(');
    });
}

$(function () {
    $("#tabs").tabs();
    $("#progressbar").progressbar({value: 2, max: 4});
    for (let rate of rates) {
        initSlider(rate);
    }
    $('.id').each(function () {
        let id = $(this).val();
        feedback['messages'][id] = {'category': null, 'rate': 0};
    });
    $('.select-category').selectmenu({
        change: function (event, data) {
            let id = $(this).attr('id').split('-')[1];
            feedback['messages'][id]['category'] = data.item.value;
        }
    });
    $('.like').checkboxradio({
        icon: false
    }).change(function () {
        let id = $(this).attr('id').split('-')[1];
        feedback['messages'][id]['rate'] = this.value ? 1.0 : 0.0;
    });
});
