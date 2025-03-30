// 🔃 Modal "Bearbeiten" açma
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-schulung-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_mitarbeiter_id").value = this.dataset.mitarbeiterId;
            document.getElementById("edit_projekt_id").value = this.dataset.projektId || "";
            document.getElementById("edit_schulungstyp").value = this.dataset.schulungstyp;
            document.getElementById("edit_datum_start").value = this.dataset.datumStart;
            document.getElementById("edit_datum_ende").value = this.dataset.datumEnde;
            document.getElementById("edit_dauer").value = this.dataset.dauer;
            document.getElementById("edit_kosten").value = this.dataset.kosten;
            document.getElementById("edit_anbieter").value = this.dataset.anbieter;
            document.getElementById("edit_teilgenommen").value = this.dataset.teilgenommen;
            document.getElementById("edit_beschreibung").value = this.dataset.beschreibung;

            toggleModal("editSchulungModal");
        });
    });

    // 🔍 Arama
    const searchInput = document.getElementById("schulungSearch");
    const tableRows = document.querySelectorAll("#schulungTable tbody tr");

    searchInput.addEventListener("keyup", function () {
        const query = this.value.toLowerCase();
        tableRows.forEach(row => {
            const rowText = row.innerText.toLowerCase();
            row.style.display = rowText.includes(query) ? "" : "none";
        });
    });
});

// 📌 Modal aç/kapa
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = show ? "block" : "none";
    }
}

// ✖️ Modal dışında tıklanırsa kapat
window.onclick = function (event) {
    ["addSchulungModal", "editSchulungModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Tablo sıralama
function sortSchulungTable(columnIndex) {
    const table = document.querySelector("#schulungTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        if (columnIndex === 0) { // Datum (dd.mm.yyyy)
            aVal = new Date(aVal.split(".").reverse().join("-"));
            bVal = new Date(bVal.split(".").reverse().join("-"));
            return aVal - bVal;
        }

        if (columnIndex === 3 || columnIndex === 4) { // Dauer veya Kosten
            aVal = parseFloat(aVal.replace(",", ".")) || 0;
            bVal = parseFloat(bVal.replace(",", ".")) || 0;
            return aVal - bVal;
        }

        return aVal.localeCompare(bVal);
    });

    sortedRows.forEach(row => table.querySelector("tbody").appendChild(row));
}
