function addIngredient() {
    var newDiv = document.createElement('div');

    newDiv.innerHTML = `
    <input type="text" name="form-${document.getElementById('id_form-TOTAL_FORMS').value}-name" placeholder="Ingredient" maxlength="255" id="id_form-${document.getElementById('id_form-TOTAL_FORMS').value}-name">
    <input type="text" name="form-${document.getElementById('id_form-TOTAL_FORMS').value}-measurement" placeholder="Amount" maxlength="255" id="id_form-${document.getElementById('id_form-TOTAL_FORMS').value}-measurement">
    <input type="checkbox" name="form-${document.getElementById('id_form-TOTAL_FORMS').value}-DELETE" onclick="hideParent(this)" id="id_form-${document.getElementById('id_form-TOTAL_FORMS').value}-DELETE">
  `;

    document.getElementsByClassName('ingredients-pane')[0].appendChild(newDiv);
    document.getElementById('id_form-TOTAL_FORMS').value++
}