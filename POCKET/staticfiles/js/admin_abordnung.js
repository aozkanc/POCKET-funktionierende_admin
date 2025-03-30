// 🔃 Modal "Bearbeiten" açma
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-abordnung-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_projekt_id").value = this.dataset.projektId;
            document.getElementById("edit_mitarbeiter_id").value = this.dataset.mitarbeiterId;
            document.getElementById("edit_zeitraum_start").value = this.dataset.startdatum;
            document.getElementById("edit_zeitraum_ende").value = this.dataset.enddatum;

            document.getElementById("editAbordnungModal").style.display = "block";
        });
    });

    // 🔍 Arama
    const searchInput = document.getElementById("abordnungSearch");
    const tableRows = document.querySelectorAll("#abordnungTable tbody tr");
    searchInput.addEventListener("keyup", function () {
        const query = this.value.toLowerCase();
        tableRows.forEach(row => {
            const rowText = row.innerText.toLowerCase();
            row.style.display = rowText.includes(query) ? "" : "none";
        });
    });
});


// 📌 Modal işlemleri
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = show ? "block" : "none";
    }
}

window.onclick = function (event) {
    ["abordnungModal", "editAbordnungModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Sıralama
function sortAbordnungTable(columnIndex) {
    const table = document.querySelector("#abordnungTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        if (columnIndex === 2 || columnIndex === 3) {
            aVal = new Date(aVal.split(".").reverse().join("-"));
            bVal = new Date(bVal.split(".").reverse().join("-"));
            return aVal - bVal;
        }

        return aVal.localeCompare(bVal);
    });

    sortedRows.forEach(row => table.querySelector("tbody").appendChild(row));
}
