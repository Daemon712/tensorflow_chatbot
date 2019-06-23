let charts = [];

function updateCharts() {
    for (key in charts) {
        charts[key].redraw();
    }
}

$(function () {
    $("#tabs").tabs({
        activate: updateCharts
    });
    $("#rates-accordion").accordion({
        heightStyle: "content",
        activate: updateCharts
    });
    $("#struct-tabs").tabs({
        activate: updateCharts
    });

    //////////////////////////////
    // Object.keys(charts).forEach(function (metric) {
    //     loadData(metric);
    // });
    initArea('chats_count', ['Диалоги', 'Отзывы']);
    initDonut('feedback_ratio');
    initArea('chat_lengths', ['Максимум', 'В среднем']);
    initDonut('chat_length_ratio');
    for (let rate of ['content', 'organization', 'vocabulary', 'grammar', 'total']) {
        initDonut('rate_ratio/' + rate);
        initArea('rate_trend/' + rate, ['Максимум', 'Средняя', 'Минимум']);
    }
    initDonut('msg_ratio');
    initDonut('msg_ratio/0');
    initDonut('msg_ratio/-1');
    for (let category of ['greeting', 'narrative', 'question', 'answer', 'request', 'abuse', 'goodbye']) {
        for (let donut of ['next_msg_ratio', 'prev_msg_ratio', 'msg_rate_ratio']) {
            initDonut(donut + '/' + category);
        }
        let chart = 'msg_position/' + category;
        $.get('/metrics/' + chart
        ).done(function (data) {
            charts[chart] = Morris.Bar({
                element: chart,
                data: data,
                xkey: 0,
                ykeys: [1],
                labels: ['Реплик']
            });
        }).fail(function () {
            console.error('ошибка загрузки метрики ' + chart)
        });
    }

    ////
    $("#vocabulary-table").DataTable({
            processing: true,
            serverSide: true,
            ajax: "/vocabulary_table",
            lengthChange: false,
            columns: [
                {data: 0},
                {data: 1},
                {data: 2},
                {data: 3},
                {data: 4},
                {data: 5},
            ],
            language: lang
        });
        $("#progressbar_1").progressbar({
            value: parseFloat($("#progressbar_1>.progress-label").text())
        });
        $("#progressbar_2").progressbar({
            value: parseFloat($("#progressbar_2>.progress-label").text())
        });
        $("#feedback-table").DataTable({
            processing: true,
            serverSide: true,
            ajax: "/feedback_table",
            lengthChange: false,
            columns: [
                {data: 0},
                {data: 1},
                {data: 2},
            ],
            language: lang
        });
});

function initDonut(chart) {
    // charts[chart] = Morris.Donut({element: chart, data: {'label': 'Загрузка', 'value': 100}});
    $.get('/metrics/' + chart
    ).done(function (data) {
        charts[chart] = Morris.Donut({element: chart, data: data});
    }).fail(function () {
        console.error('ошибка загрузки метрики ' + chart)
    });
}

function initArea(chart, labels) {
    let ykeys = [];
    for (let i = 0; i < labels.length; i++) {
        ykeys.push(i + 1)
    }
    $.get('/metrics/' + chart
    ).done(function (data) {
        charts[chart] = Morris.Area({
            element: chart,
            data: data,
            behaveLikeLine: true,
            xkey: 0,
            ykeys: ykeys,
            labels: labels
        });
    }).fail(function () {
        console.error('ошибка загрузки метрики ' + chart)
    });
}

let lang = {
    "info": "Показано с _START_ по _END_ из _TOTAL_ записей",
    "infoFiltered": "(всего _MAX_)",
    "search": "Поиск:",
    "paginate": {
        "first": "Начало",
        "last": "Конец",
        "next": ">",
        "previous": "<"
    },
}