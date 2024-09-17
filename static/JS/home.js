let file1 = document.getElementById("id_Pan_Card")
let file2 = document.getElementById("id_Aadhar_Card")
let label1 = document.getElementById("label1")
let label2 = document.getElementById("label2")
let form = document.getElementById("Upolad_form")
file1.addEventListener('click', function (event) {
    popup(label1, "")
})
file2.addEventListener('click', function (event) {
    popup(label2, "")
})
document.getElementById("Upload_details").addEventListener("click", function (event) {
    if ((file1.files.length == 0 || file2.files.length == 0) || (file1.files[0].size > 500000 || file2.files[0].size > 500000)) {
        if (file1.files.length == 0) {
            popup(label1, "Please select a file");
        } else if (file1.files[0].size > 5000000) {
            popup(label1, "File must be less than 5MB");
        }

        if (file2.files.length == 0) {
            popup(label2, "Please select a file");
        } else if (file2.files[0].size > 5000000) {
            popup(label2, "File must be less than 5MB");
        }
    } else {
        form.submit()
    }
});

function popup(element, text) {
    element.innerHTML = text
}