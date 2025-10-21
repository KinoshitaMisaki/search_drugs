document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchCount = document.getElementById('search-count');
    const resultTableBody = document.querySelector('#result-table tbody');
    const noResultsMessage = document.getElementById('no-results-message');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        performSearch();
    });

    // Initial search to show all data
    performSearch();

    async function performSearch() {
        const formData = new FormData(searchForm);
        const params = new URLSearchParams(formData);

        const response = await fetch(`/search?${params.toString()}`);
        const results = await response.json();

        updateTable(results);
    }

    function updateTable(results) {
        // Clear existing table rows
        resultTableBody.innerHTML = '';

        // Update search count
        searchCount.textContent = `検索件数: ${results.length} 件`;

        if (results.length === 0) {
            noResultsMessage.style.display = 'block';
        } else {
            noResultsMessage.style.display = 'none';
            results.forEach((result, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${result['薬品名(和名)'] || ''}</td>
                    <td>${result['薬品名(英名)'] || ''}</td>
                    <td>${result['型番'] || ''}</td>
                    <td>${result['メーカー名'] || ''}</td>
                `;
                resultTableBody.appendChild(row);
            });
        }
    }

    const exportCsvButton = document.getElementById('export-csv');
    exportCsvButton.addEventListener('click', () => {
        const formData = new FormData(searchForm);
        const params = new URLSearchParams(formData);

        window.location.href = `/export_csv?${params.toString()}`;
    });
});
