// ✏️ Modal "Bearbeiten" açma
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-schulungskosten-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_mitarbeiter").value = this.dataset.mitarbeiter;
            document.getElementById("edit_projekt").value = this.dataset.projekt;
            document.getElementById("edit_schulungstyp").value = this.dataset.schulungstyp;
            document.getElementById("edit_startdatum").value = this.dataset.startdatum;
            document.getElementById("edit_enddatum").value = this.dataset.enddatum;
            document.getElementById("edit_dauer").value = this.dataset.dauer;
            document.getElementById("edit_kosten").value = this.dataset.kosten;
            document.getElementById("edit_anbieter").value = this.dataset.anbieter;
            document.getElementById("edit_teilgenommen").value = this.dataset.teilgenommen;
            document.getElementById("edit_beschreibung").value = this.dataset.beschreibung;

            toggleModal("editSchulungskostenModal", true);
        });
    });

    // 🔍 Arama
    const searchInput = document.getElementById("schulungskostenSearch");
    const tableRows = document.querySelectorAll("#schulungskostenTable tbody tr");

    searchInput.addEventListener("keyup", function () {
        const query = this.value.toLowerCase();
        tableRows.forEach(row => {
            const rowText = row.innerText.toLowerCase();
            row.style.display = rowText.includes(query) ? "" : "none";
        });
    });
});

// 📌 Modal aç/kapat fonksiyonu
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = show ? "block" : "none";
    }
}

// ✖️ Modal dışına tıklanınca kapat
window.onclick = function (event) {
    ["addSchulungskostenModal", "editSchulungskostenModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Tablo sıralama fonksiyonu
function sortSchulungskostenTable(columnIndex) {
    const table = document.querySelector("#schulungskostenTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sorted = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        // Tarih karşılaştırması için dönüşüm
        if (columnIndex === 3) {
            aVal = new Date(aVal.split('.').reverse().join('-'));
            bVal = new Date(bVal.split('.').reverse().join('-'));
            return aVal - bVal;
        }

        // Sayısal karşılaştırma
        if (columnIndex === 4) {
            return parseFloat(aVal.replace(",", ".")) - parseFloat(bVal.replace(",", "."));
        }

        return aVal.localeCompare(bVal);
    });

    sorted.forEach(row => table.querySelector("tbody").appendChild(row));
}
