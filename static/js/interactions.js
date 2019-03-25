var textContainer, textareaSize, input;
var autoSize = function () {
    // also can use textContent or innerText
    textareaSize.innerHTML = input.value + '\n';
};

document.addEventListener('DOMContentLoaded', function() {
    textContainer = document.querySelector('.textarea-container');
    textareaSize = textContainer.querySelector('.textarea-size');
    input = textContainer.querySelector('textarea');

    autoSize();
    input.addEventListener('input', autoSize);
});

document.addEventListener('DOMContentLoaded', function() {
    $("#positive-feedback").bind('click', function() {
        $.getJSON($SCRIPT_ROOT + '/_prediction_feedback', {
            sample_id: $('input[name="sample_id"]').val(),
            correct: true
        }, function(data) {
            console.log(data)
        });
        return false;
    });
});

document.addEventListener('DOMContentLoaded', function() {
    $("#negative-feedback").bind('click', function() {
        $.getJSON($SCRIPT_ROOT + '/_prediction_feedback', {
            sample_id: $('input[name="sample_id"]').val(),
            correct: false
        }, function(data) {
            console.log(data)
        });
        return false;
    });
});

document.addEventListener('DOMContentLoaded', function() {
    $('#main-text-input').keydown(function(event) {
        if (event.which == 13) {
            this.form.submit();
            event.preventDefault();
         }
    });
});
