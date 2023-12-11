function hideParent(clickedElement) {
    var parentElement = clickedElement.parentElement;
    if (parentElement) {
        parentElement.style.display = 'none';
    }
}