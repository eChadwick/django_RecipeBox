function initializeAutocomplete(input) {
    const awesomplete = new Awesomplete(input, {
        minChars: 1,
        autoFirst: true
    });

    input.addEventListener("input", function () {
        const query = input.value;
        if (query.length < 1) return;

        fetch("/ingredient-autocomplete?query=" + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                awesomplete.list = data;
            });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll(".ingredient-input");
    inputs.forEach(input => initializeAutocomplete(input));
});