function addIngredient() {
  var newDiv = document.createElement('p');
  const newFormNumber = document.getElementById('id_ingredient-form-TOTAL_FORMS').value;

  newDiv.innerHTML = `
    <input type="text" name="ingredient-form-${newFormNumber}-name" placeholder="Ingredient" maxlength="255" id="id_ingredient-form-${newFormNumber}-name">
    -
    <input type="text" name="ingredient-form-${newFormNumber}-measurement" placeholder="Amount" maxlength="255" id="id_ingredient-form-${newFormNumber}-measurement">
    <input type="checkbox" name="ingredient-form-${newFormNumber}-DELETE" onclick="hideParent(this)" id="id_ingredient-form-${newFormNumber}-DELETE">
  `;

  document.getElementsByClassName('ingredients-pane')[0].appendChild(newDiv);
  document.getElementById('id_ingredient-form-TOTAL_FORMS').value++
}