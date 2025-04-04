// 🔃 Bearbeiten modalını aç
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-abrechnung-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_mitarbeiter").value = this.dataset.mitarbeiterId;
            document.getElementById("edit_projekt").value = this.dataset.projektId;
            document.getElementById("edit_monat").value = this.dataset.monat;
            document.getElementById("edit_netto_summe").value = this.dataset.nettoSumme;
            document.getElementById("edit_brutto_summe").value = this.dataset.bruttoSumme;
            document.getElementById("edit_rechnung_status").value = this.dataset.rechnungStatus;
            document.getElementById("edit_zahlungseingang").value = this.dataset.zahlungseingang;
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

        // Tarih varsa
        if (columnIndex === 2) {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
            return aVal - bVal;
        }

        // Sayısal ise
        if (columnIndex === 3 || columnIndex === 4) {
            return parseFloat(aVal) - parseFloat(bVal);
        }

        return aVal.localeCompare(bVal);
    });

    sorted.forEach(row => table.querySelector("tbody").appendChild(row));
}
