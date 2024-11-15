function addTag() {
    var newDiv = document.createElement('p');
    const newFormNumber = document.getElementById('id_tag-create-form-TOTAL_FORMS').value;

    newDiv.innerHTML = `
            <input type="text" name="tag-create-form-${newFormNumber}-tag_name" maxlength="250" id="id_tag-create-form-${newFormNumber}-tag_name" placeholder="Create Tag">
            <input type="checkbox" onclick="hideParent(this)">
    `

    document.getElementsByClassName('tag-create-pane')[0].appendChild(newDiv);
    document.getElementById('id_tag-create-form-TOTAL_FORMS').value++;
}