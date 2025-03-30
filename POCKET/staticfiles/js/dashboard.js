document.addEventListener("DOMContentLoaded", function () {
    // Grafik 1: Kategori Bazlı
    const ctx1 = document.getElementById('kostenKategorieChart');
    if (ctx1) {
        const a = parseFloat(ctx1.dataset.abrechnung) || 0;
        const r = parseFloat(ctx1.dataset.reise) || 0;
        const s = parseFloat(ctx1.dataset.schulung) || 0;

        new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['Abrechnung', 'Reise', 'Schulung'],
                datasets: [{
                    data: [a, r, s],
                    backgroundColor: ['#3f63b1', '#5acbe4', '#ffc107'],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#333' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.label}: ${context.raw.toFixed(2)} €`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Grafik 2: Projekt vs Allgemein
    const ctx2 = document.getElementById('kostenProjektAllgemeinChart');
    if (ctx2) {
        const p = parseFloat(ctx2.dataset.projekt) || 0;
        const g = parseFloat(ctx2.dataset.allgemein) || 0;

        new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Projektgebunden', 'Allgemein'],
                datasets: [{
                    data: [p, g],
                    backgroundColor: ['#3f63b1', '#ffc107'],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#333' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.label}: ${context.raw.toFixed(2)} €`;
                            }
                        }
                    }
                }
            }
        });
    }
});
