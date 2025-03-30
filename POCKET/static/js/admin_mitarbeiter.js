// 🔃 Bearbeiten modal'ını aç ve formu doldur
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-mitarbeiter-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_vorname").value = this.dataset.vorname;
            document.getElementById("edit_nachname").value = this.dataset.nachname;
            document.getElementById("edit_standort").value = this.dataset.standort;
            document.getElementById("edit_abteilung").value = this.dataset.abteilung;
            document.getElementById("edit_status").value = this.dataset.status;
            document.getElementById("edit_rolle").value = this.dataset.rolle;

            toggleModal("editMitarbeiterModal", true);
        });
    });

    // 🔍 Arama kutusu (live search)
    const searchInput = document.getElementById("mitarbeiterSearch");
    const tableRows = document.querySelectorAll("#mitarbeiterTable tbody tr");

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

// 📌 Modal aç/kapat fonksiyonu
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = show ? "block" : "none";
    }
}

// 🖱️ Modal dışına tıklayınca kapatma
window.onclick = function (event) {
    ["addMitarbeiterModal", "editMitarbeiterModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Tablo sıralama
function sortMitarbeiterTable(columnIndex) {
    const table = document.querySelector("#mitarbeiterTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        return aVal.localeCompare(bVal);
    });

    sortedRows.forEach(row => table.querySelector("tbody").appendChild(row));
}