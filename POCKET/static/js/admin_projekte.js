// ✅ Modal aç/kapat
function toggleModal(modalId, show = true) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = show ? "block" : "none";
    }
}

// ✅ Dışarı tıklayınca modal kapansın
window.onclick = function (event) {
    ["addProjektModal", "editProjektModal", "projektDetailModal"].forEach(id => {
        const modal = document.getElementById(id);
        if (event.target === modal) {
            toggleModal(id, false);
        }
    });
};

// ✅ Tablo sıralama
function sortProjektTable(columnIndex) {
    const table = document.querySelector("#projektTable");
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].innerText.trim().toLowerCase();
        let bVal = b.cells[columnIndex].innerText.trim().toLowerCase();

        if (columnIndex === 2) {
            aVal = new Date(aVal.split(".").reverse().join("-"));
            bVal = new Date(bVal.split(".").reverse().join("-"));
            return aVal - bVal;
        }

        if ([4, 5, 6].includes(columnIndex)) {
            return parseFloat(aVal.replace(",", ".").replace("€", "")) - parseFloat(bVal.replace(",", ".").replace("€", ""));
        }

        return aVal.localeCompare(bVal);
    });

    sortedRows.forEach(row => table.querySelector("tbody").appendChild(row));
}

// ✅ Modal "Bearbeiten" açma ve Arama
document.addEventListener("DOMContentLoaded", function () {
    // ✏️ Bearbeiten Modal
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

    // 📄 Details Modal
    document.querySelectorAll(".projekt-detail-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            openProjektDetailModal(this);
        });
    });
});

// ✅ Grafik değişkenleri (global)
let finanzChart;
let kostenChart;

// ✅ Details Modal açma
function openProjektDetailModal(element) {
    // Genel Bilgiler
    document.getElementById("modalProjektTitle").textContent = element.dataset.projektname;
    document.getElementById("modalZeitraum").textContent = `${element.dataset.startdatum} – ${element.dataset.enddatum}`;
    document.getElementById("modalKunden").textContent = element.dataset.kunde_2
      ? `${element.dataset.kunde_1}, ${element.dataset.kunde_2}`
      : element.dataset.kunde_1;
    document.getElementById("modalTyp").textContent = element.dataset.projekttyp;
    document.getElementById("modalStatus").textContent = element.dataset.status;
    document.getElementById("modalBeschreibung").textContent = element.dataset.beschreibung;
  
    // Sayısal Değerler
    const budget = parseFloat(element.dataset.budget) || 0;
    const einnahmen = parseFloat(element.dataset.einnahmen) || 0;
    const ausgaben = parseFloat(element.dataset.ausgaben) || 0;
    const differenz = einnahmen - budget;
    const gewinn = einnahmen - ausgaben;
  
    // Sayısal değerleri yaz
    document.getElementById("modalBudget").textContent = budget.toFixed(2) + " €";
    document.getElementById("modalEinnahmen").textContent = einnahmen.toFixed(2) + " €";
    document.getElementById("modalAusgaben").textContent = ausgaben.toFixed(2) + " €";
    document.getElementById("modalDifferenz").textContent = differenz.toFixed(2) + " €";
    document.getElementById("modalGewinn").textContent = gewinn.toFixed(2) + " €";
  
    // Chart 1: Finanzübersicht
    const ctx1 = document.getElementById("finanzChart").getContext("2d");
    if (finanzChart) finanzChart.destroy();
    finanzChart = new Chart(ctx1, {
      type: "bar",
      data: {
        labels: ["Einnahmen", "Budget", "Ausgaben"],
        datasets: [{
          label: "Finanzen (€)",
          data: [einnahmen, budget, ausgaben],
          backgroundColor: ["#4CAF50", "#2196F3", "#F44336"]
        }]
      },
      options: {
        responsive: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: {
              maxRotation: 0,
              minRotation: 0
            }
          }
        }
      }
    });
  
    // Chart 2: Ausgabenverteilung (Donut)
    const abrechnung = parseFloat(element.dataset.abrechnung) || 0;
    const reisekosten = parseFloat(element.dataset.reisekosten) || 0;
    const schulungskosten = parseFloat(element.dataset.schulungskosten) || 0;
  
    const ctx2 = document.getElementById("kostenChart").getContext("2d");
    if (kostenChart) kostenChart.destroy();
    kostenChart = new Chart(ctx2, {
      type: "doughnut",
      data: {
        labels: ["Abrechnung", "Reisekosten", "Schulungskosten"],
        datasets: [{
          data: [abrechnung, reisekosten, schulungskosten],
          backgroundColor: ["#007bff", "#ffc107", "#28a745"]
        }]
      },
      options: {
        responsive: false,
        cutout: "50%",
        radius: "90%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 15,
              padding: 15
            }
          }
        }
      }
    });
  
    toggleModal("projektDetailModal", true);
  }