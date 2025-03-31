document.addEventListener("DOMContentLoaded", function () {
    // 🔍 Arama
    const searchInput = document.getElementById("einnahmeSearch");
    const table = document.getElementById("einnahmeTable");
    const rows = table.getElementsByTagName("tr");

    searchInput.addEventListener("keyup", function () {
        const filter = this.value.toLowerCase();

        for (let i = 1; i < rows.length; i++) {
            const rowText = rows[i].innerText.toLowerCase();
            rows[i].style.display = rowText.includes(filter) ? "" : "none";
        }
    });

    // ✏️ Bearbeiten modal'ı doldur
    const editButtons = document.querySelectorAll(".edit-einnahme-btn");
    editButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const id = btn.dataset.id;
            document.getElementById("edit_id").value = id;

            document.getElementById("edit_projekt_id").value = btn.dataset.projektId;
            document.getElementById("edit_betrag").value = btn.dataset.betrag;
            document.getElementById("edit_zahlungseingang").value = btn.dataset.zahlungseingang;
            document.getElementById("edit_zahlungsart").value = btn.dataset.zahlungsart;
            document.getElementById("edit_rechnungsnummer").value = btn.dataset.rechnungsnummer;
            document.getElementById("edit_status").value = btn.dataset.status;

            toggleModal("editEinnahmeModal", true);
        });
    });
});

// 🔁 Modal Açma/Kapama Fonksiyonu
function toggleModal(id, show = true) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = show ? "block" : "none";
    }
}

// Modal dışında tıklayınca kapatma
window.addEventListener('click', function(event) {
    const modal = document.getElementById('addEinnahmeModal'); // senin modal ID'in neyse
    if (event.target === modal) {
        toggleModal('addEinnahmeModal', false);
    }
});
