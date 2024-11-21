  function createPaginationControls(results, currentPage, resultsPerPage) {
        const totalPages = Math.ceil(results.length / resultsPerPage);
        const paginationContainer = document.getElementById('paginationControls');
        paginationContainer.innerHTML = ''; // Clear current controls

        // Create "Previous" button
        const prevButton = document.createElement('button');
        prevButton.textContent = 'Previous';
        prevButton.disabled = currentPage === 1; // Disable if on the first page
        prevButton.onclick = () => renderResults(results, currentPage - 1, resultsPerPage);
        paginationContainer.appendChild(prevButton);

        // Create page number buttons
        for (let i = 1; i <= totalPages; i++) {
            const button = document.createElement('button');
            button.textContent = i;
            button.className = i === currentPage ? 'active' : '';
            button.onclick = () => renderResults(results, i, resultsPerPage);
            paginationContainer.appendChild(button);
        }

        // Create "Next" button
        const nextButton = document.createElement('button');
        nextButton.textContent = 'Next';
        nextButton.disabled = currentPage === totalPages; // Disable if on the last page
        nextButton.onclick = () => renderResults(results, currentPage + 1, resultsPerPage);
        paginationContainer.appendChild(nextButton);
    }

    // Render initial results
    renderResults(sampleResults);