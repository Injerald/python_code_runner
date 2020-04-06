let alertElement = _.template('<div class="alert alert-<%= type %> alert-dismissable"><button type="button" class="close" ' +
    'data-dismiss="alert" aria-hidden="true">&times;</button><%= message %></div>');

function receive_code_result(task_id) {
    let code_result_socket = new WebSocket('ws://127.0.0.1:8765/');
    code_result_socket.onopen = function (event) {
        code_result_socket.send(task_id);
    };
    code_result_socket.onmessage = function (event) {
        $('#code-result textarea').text(event.data)
    }
}

$(function () {
    $('form').on("submit", function (e) {
        e.preventDefault();
        let python_code = $("#pythonTextarea");
        let alertContainer = $('#alert-container');

        $.ajax({
            type: 'POST',
            data: {'python_code': python_code.val()},
            url: window.location.href + 'python-handler',
            success: function (data) {
                alertContainer.empty().append(alertElement({
                    'type': 'success',
                    'message': 'Waiting for code result'
                }));
                $('#code-result textarea').text('Loading results...');
                let data_json = JSON.parse(data);
                receive_code_result(data_json['task_id']);
            },
            error: function () {
                alertContainer.empty().append(alertElement({
                    'type': 'danger',
                    'message': 'An error occurred'
                }));
            },
            complete: function () {
                alertContainer.show().fadeOut(3000);
            }
        });
    })
});