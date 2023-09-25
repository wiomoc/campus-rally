function scoreChange(id, value) {
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch("", {
        method: "POST",
        body: `_selected_action=${id}&action=set_score&value=${value}&csrfmiddlewaretoken=${csrfToken}`,
        headers: {"Content-Type": "application/x-www-form-urlencoded"}
    }).catch(e => alert("Could not update score. Please reload page."))

}