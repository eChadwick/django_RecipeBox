function addTag() {
    var newDiv = document.createElement('p');
    const newFormNumber = document.getElementById('id_tag-create-form-TOTAL_FORMS').value;

    newDiv.innerHTML = `
            <label for=id_tag-create-form-${newFormNumber}-tag_name>Tag name:</label>
            <input type="text" name="tag-create-form-${newFormNumber}-tag_name" maxlength="250" id="id_tag-create-form-${newFormNumber}-tag_name">
            <input type="checkbox" onclick="hideParent(this)">
    `

    document.getElementsByClassName('tag-create-pane')[0].appendChild(newDiv);
    document.getElementById('id_tag-create-form-TOTAL_FORMS').value++;
}