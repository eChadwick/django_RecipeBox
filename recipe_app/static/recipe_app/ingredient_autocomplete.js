// Define the logic once
function initializeAutocomplete(input) {
    const awesomplete = new Awesomplete(input, {
        minChars: 1,
        autoFirst: true
    });

    input.addEventListener("input", function () {
        const query = input.value;
        if (query.length < 1) return;

        fetch("/ingredient-autocomplete?q=" + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                awesomplete.list = data;
            });
    });
}

// Apply to existing inputs on page load
document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll(".ingredient-input");
    inputs.forEach(input => initializeAutocomplete(input));
});