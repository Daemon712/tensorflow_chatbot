let rates = ['content', 'organization', 'vocabulary', 'grammar'];
var sum = 0;

function initSlider(prefix) {
    sum += 2;
    $("#" + prefix + "-slider").slider({
        range: "min",
        value: 2,
        max: 4,
        slide: function (event, ui) {
            $("#" + prefix + "-label").text(1 + ui.value);
            let old = $(this).slider("value");
            let summary = $("#summary");
            sum = sum - old + ui.value;
            let avg = sum / rates.length;
            summary.text(avg + 1);
            $("#progressbar").progressbar("option", {value: avg});
        }
    });
}

function sendFeedback() {
    let data = {};
    for (let rate of rates) {
        data[rate + '_rate'] = $("#" + rate + "-slider").slider("value");
    }
    data['total_rate'] = sum / rates.length;
    data['comment'] = $("#comment-area").val();

    $.post(window.location.pathname, data
    ).done(function () {
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
});
