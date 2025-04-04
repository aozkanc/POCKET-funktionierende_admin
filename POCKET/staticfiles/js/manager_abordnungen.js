// 🔃 Modal "Bearbeiten" açma
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-abordnung-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            // Verileri modal inputlarına atıyoruz
            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_projekt").value = this.dataset.projekt_id;
            document.getElementById("edit_mitarbeiter").value = this.dataset.mitarbeiter_id;
            document.getElementById("edit_zeitraum_start").value = this.dataset.zeitraum_start;
            document.getElementById("edit_zeitraum_ende").value = this.dataset.zeitraum_ende;

            toggleModal("editAbordnungModal", true);
        });
    });

    // 🔍 Arama
    const searchInput = document.getElementById("abordnungSearch");
    const tableRows = document.querySelectorAll("#abordnungTable tbody tr");
    if (searchInput) {
        searchInput.addEventListener("keyup", function () {
            const query = this.value.toLowerCase();
            tableRows.forEach(row => {
                const rowText = row.innerText.toLowerCase();
                row.style.display = rowText.includes(query) ? "" : "none";
            });
        });
    }
});

// 📌 Modal aç/kapat
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = show ? "block" : "none";
    }
}

// Modal dışına tıklanınca kapanma
window.onclick = function (event) {
    ["addAbordnungModal", "editAbordnungModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Tablo sıralama
function sortAbordnungTable(columnIndex) {
    const table = document.querySelector("#abordnungTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        if (columnIndex === 2 || columnIndex === 3) { // Tarihler
            aVal = new Date(aVal.split(".").reverse().join("-"));
            bVal = new Date(bVal.split(".").reverse().join("-"));
            return aVal - bVal;
        }

        return aVal.localeCompare(bVal);
    });

    sortedRows.forEach(row => table.querySelector("tbody").appendChild(row));
}
