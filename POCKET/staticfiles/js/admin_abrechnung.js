// 🔃 Bearbeiten modalını aç
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-abrechnung-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_monat").value = this.dataset.monat;
            document.getElementById("edit_mitarbeiter_id").value = this.dataset.mitarbeiterId;
            document.getElementById("edit_projekt_id").value = this.dataset.projektId || "";
            document.getElementById("edit_stunden").value = this.dataset.stunden;
            document.getElementById("edit_stundensatz").value = this.dataset.stundensatz;
            document.getElementById("edit_netto_summe").value = this.dataset.netto;
            document.getElementById("edit_brutto_summe").value = this.dataset.brutto;
            document.getElementById("edit_rechnung_status").value = this.dataset.status;
            document.getElementById("edit_zahlung").value = this.dataset.zahlung;
            document.getElementById("edit_leistungsnachweis").value = this.dataset.leistungsnachweis;
            document.getElementById("edit_bemerkung").value = this.dataset.bemerkung;

            toggleModal("editAbrechnungModal", true);
        });
    });

    // 🔍 Arama
    const searchInput = document.getElementById("abrechnungSearch");
    const tableRows = document.querySelectorAll("#abrechnungTable tbody tr");

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

// ⛔ Modal dışına tıklayınca kapanması
window.onclick = function (event) {
    ["addAbrechnungModal", "editAbrechnungModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Tablo sıralama
function sortAbrechnungTable(columnIndex) {
    const table = document.querySelector("#abrechnungTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sorted = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        if (columnIndex === 0) {  // Monat (örneğin: 03.2025)
            aVal = aVal.split(".").reverse().join("-");
            bVal = bVal.split(".").reverse().join("-");
            return new Date(aVal) - new Date(bVal);
        }

        if (columnIndex === 4) { // Netto
            return parseFloat(aVal) - parseFloat(bVal);
        }

        return aVal.localeCompare(bVal);
    });

    sorted.forEach(row => table.querySelector("tbody").appendChild(row));
}
