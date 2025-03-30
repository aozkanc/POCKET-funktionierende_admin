// 🔃 Modal "Bearbeiten" açma
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-projekt-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_projektname").value = this.dataset.projektname;
            document.getElementById("edit_startdatum").value = this.dataset.startdatum;
            document.getElementById("edit_enddatum").value = this.dataset.enddatum;
            document.getElementById("edit_budget").value = this.dataset.budget;
            document.getElementById("edit_kunde_1").value = this.dataset.kunde_1;
            document.getElementById("edit_kunde_2").value = this.dataset.kunde_2;
            document.getElementById("edit_projekttyp").value = this.dataset.projekttyp;
            document.getElementById("edit_status").value = this.dataset.status;
            document.getElementById("edit_beschreibung").value = this.dataset.beschreibung;

            toggleModal("editProjektModal", true);
        });
    });

    // 🔍 Arama
    const searchInput = document.getElementById("projektSearch");
    const tableRows = document.querySelectorAll("#projektTable tbody tr");

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

// 🖱️ Dışarı tıklayınca kapat
window.onclick = function (event) {
    ["addProjektModal", "editProjektModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Tablo sıralama
function sortProjektTable(columnIndex) {
    const table = document.querySelector("#projektTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        if (columnIndex === 2) { // Startdatum
            aVal = new Date(aVal.split(".").reverse().join("-"));
            bVal = new Date(bVal.split(".").reverse().join("-"));
            return aVal - bVal;
        }

        return aVal.localeCompare(bVal);
    });

    sortedRows.forEach(row => table.querySelector("tbody").appendChild(row));
}
