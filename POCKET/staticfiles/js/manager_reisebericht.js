document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-reisebericht-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            document.getElementById("edit_id").value = this.dataset.id;
            document.getElementById("edit_mitarbeiter").value = this.dataset.mitarbeiterId;
            document.getElementById("edit_projekt").value = this.dataset.projektId;
            document.getElementById("edit_datum").value = this.dataset.datum;
            document.getElementById("edit_zielort").value = this.dataset.zielort;
            document.getElementById("edit_verkehrsmittel").value = this.dataset.verkehrsmittel;
            document.getElementById("edit_distanz_km").value = this.dataset.distanz;
            document.getElementById("edit_kosten_fahrt").value = this.dataset.kostenFahrt;
            document.getElementById("edit_hotel_name").value = this.dataset.hotelName;
            document.getElementById("edit_kosten_übernachtung").value = this.dataset.kostenÜbernachtung;
            document.getElementById("edit_gesamtkosten").value = this.dataset.gesamtkosten;
            document.getElementById("edit_rechnung_vorhanden").value = this.dataset.rechnungVorhanden;

            toggleModal("editReiseberichtModal", true);
        });
    });

    // 🔍 Arama
    const searchInput = document.getElementById("reiseberichtSearch");
    const tableRows = document.querySelectorAll("#reiseberichtTable tbody tr");

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

// ⛔ Modal dışına tıklanınca kapansın
window.onclick = function (event) {
    ["addReiseberichtModal", "editReiseberichtModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// 🔽 Tablo sıralama
function sortReiseberichtTable(columnIndex) {
    const table = document.querySelector("#reiseberichtTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.toLowerCase();
        let bVal = b.cells[columnIndex].innerText.toLowerCase();

        if (columnIndex === 2) { // Datum
            aVal = new Date(aVal.split(".").reverse().join("-"));
            bVal = new Date(bVal.split(".").reverse().join("-"));
            return aVal - bVal;
        }

        if ([4, 5].includes(columnIndex)) { // Kosten
            aVal = parseFloat(aVal.replace(",", ".").replace(/[^\d.-]/g, "")) || 0;
            bVal = parseFloat(bVal.replace(",", ".").replace(/[^\d.-]/g, "")) || 0;
            return aVal - bVal;
        }

        return aVal.localeCompare(bVal);
    });

    sortedRows.forEach(row => table.querySelector("tbody").appendChild(row));
}
