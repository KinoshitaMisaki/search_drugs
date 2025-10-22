let currentPage = 1;

document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        currentPage = 1; // Reset to first page on new search
        performSearch();
    });
});

async function performSearch() {
    const formData = new FormData(document.getElementById('search-form'));
    const params = new URLSearchParams(formData);
    params.append('page', currentPage);

    const response = await fetch(`/search?${params.toString()}`);
    const data = await response.json();

    updateTable(data.results);
    updatePagination(data.total_pages, data.current_page);
    document.getElementById('search-count').textContent = `検索件数: ${data.total_items} 件`;
}

function updateTable(results) {
    const resultTableBody = document.querySelector('#result-table tbody');
    const noResultsMessage = document.getElementById('no-results-message');

    resultTableBody.innerHTML = '';

    if (results.length === 0) {
        noResultsMessage.style.display = 'block';
    } else {
        noResultsMessage.style.display = 'none';
        results.forEach((result, index) => {
            const row = document.createElement('tr');
            const itemNumber = ((currentPage - 1) * 50) + index + 1;
            row.innerHTML = `
                <td>${itemNumber}</td>
                <td>${result['薬品名(和名)'] || ''}</td>
                <td>${result['薬品名(英名)'] || ''}</td>
                <td>${result['型番'] || ''}</td>
                <td>${result['メーカー名'] || ''}</td>
            `;
            resultTableBody.appendChild(row);
        });
    }
}

function updatePagination(totalPages, currentPage) {
    const paginationUl = document.getElementById('pagination');
    paginationUl.innerHTML = '';

    const createPageLink = (page, text = page) => {
        const li = document.createElement('li');
        li.className = `page-item ${page === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" data-page="${page}">${text}</a>`;
        return li;
    };

    const createEllipsis = () => {
        const li = document.createElement('li');
        li.className = 'page-item disabled';
        li.innerHTML = `<span class="page-link">...</span>`;
        return li;
    };

    // Previous button
    if (currentPage > 1) {
        paginationUl.appendChild(createPageLink(currentPage - 1, '前へ'));
    }

    // Page numbers logic
    const pagesToShow = [];
    if (totalPages <= 7) {
        for (let i = 1; i <= totalPages; i++) {
            pagesToShow.push(i);
        }
    } else {
        pagesToShow.push(1);
        if (currentPage > 3) {
            pagesToShow.push('...');
        }
        if (currentPage > 2) {
            pagesToShow.push(currentPage - 1);
        }
        if (currentPage !== 1 && currentPage !== totalPages) {
            pagesToShow.push(currentPage);
        }
        if (currentPage < totalPages - 1) {
            pagesToShow.push(currentPage + 1);
        }
        if (currentPage < totalPages - 2) {
            pagesToShow.push('...');
        }
        pagesToShow.push(totalPages);
    }

    // Create unique page links
    const uniquePages = [...new Set(pagesToShow)];
    uniquePages.forEach(page => {
        if (page === '...') {
            paginationUl.appendChild(createEllipsis());
        } else {
            paginationUl.appendChild(createPageLink(page));
        }
    });


    // Next button
    if (currentPage < totalPages) {
        paginationUl.appendChild(createPageLink(currentPage + 1, '次へ'));
    }

    // Add event listeners to new links
    document.querySelectorAll('.page-link[data-page]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = parseInt(e.target.dataset.page);
            if (page !== currentPage) {
                currentPage = page;
                performSearch();
            }
        });
    });
}


const exportCsvButton = document.getElementById('export-csv');
exportCsvButton.addEventListener('click', () => {
    const formData = new FormData(document.getElementById('search-form'));
    const params = new URLSearchParams(formData);

    window.location.href = `/export_csv?${params.toString()}`;
});
