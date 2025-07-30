document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll(".ingredient-input");

    inputs.forEach(function (input) {
        const awesomplete = new Awesomplete(input, {
            minChars: 1,
            autoFirst: true
        });

        input.addEventListener("input", function () {
            const query = input.value;
            if (query.length < 1) return;

            fetch("/ingredient-autocomplete?q=" + encodeURIComponent(query))
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    awesomplete.list = data;
                });
        });
    });
});