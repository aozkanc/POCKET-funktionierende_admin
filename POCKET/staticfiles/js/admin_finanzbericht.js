document.addEventListener("DOMContentLoaded", function() {
    // 🔍 Arama Özelliği
    document.getElementById("finanzSearch").addEventListener("keyup", function() {
        let searchValue = this.value.toLowerCase();
        let table = document.getElementById("finanzTable");
        let rows = table.getElementsByTagName("tr");

        for (let i = 1; i < rows.length; i++) {
            let rowText = rows[i].innerText.toLowerCase();
            rows[i].style.display = rowText.includes(searchValue) ? "" : "none";
        }
    });

    // 📊 Chart.js ile Dinamik Grafik
    let labels = [];
    let data = [];

    document.querySelectorAll("#finanzTable tbody tr").forEach(row => {
        let projektName = row.cells[0].innerText;
        let kosten = parseFloat(row.cells[2].innerText.replace("€", "").trim());

        let index = labels.indexOf(projektName);
        if (index === -1) {
            labels.push(projektName);
            data.push(kosten);
        } else {
            data[index] += kosten; // Aynı proje için maliyetleri topla
        }
    });

    var ctx = document.getElementById("finanzChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Gesamtkosten (€)",
                data: data,
                backgroundColor: ["red", "blue", "green", "orange", "purple", "gray"]
            }]
        }
    });
});

// 📌 Tablo Sıralama Fonksiyonu
function sortTable(columnIndex) {
    let table = document.getElementById("finanzTable");
    let rows = Array.from(table.getElementsByTagName("tr")).slice(1);

    let sortedRows = rows.sort((a, b) => {
        let aValue = a.cells[columnIndex].innerText.toLowerCase();
        let bValue = b.cells[columnIndex].innerText.toLowerCase();

        // 📅 Eğer tarih sütunu (Datum) sıralanıyorsa özel işlem yap
        if (columnIndex === 3) {
            aValue = parseInt(a.cells[columnIndex].getAttribute("data-timestamp"));
            bValue = parseInt(b.cells[columnIndex].getAttribute("data-timestamp"));
            return aValue - bValue; // Tarih sıralaması küçükten büyüğe
        }

        return aValue.localeCompare(bValue);
    });

    sortedRows.forEach(row => table.appendChild(row));
}
