function showSection(sectionId) {
    document.querySelectorAll('.tabContent').forEach(section => section.style.display = 'none');
    const target = document.getElementById(sectionId);
    if (target) target.style.display = 'block';
    if (sectionId === "topReviews") loadMovies('top_movies');
    else if (sectionId === "worstReviews") loadMovies('worst_movies');
}

async function loadMovies(movieType) {
    try {
        const response = await fetch('/static/top_worst_movies.json');
        const data = await response.json();
        const topMoviesList = document.getElementById('topMoviesList');
        const worstMoviesList = document.getElementById('worstMoviesList');
        topMoviesList.innerHTML = '';
        worstMoviesList.innerHTML = '';
        if (movieType === 'top_movies')
            (data.top_movies || []).forEach(movie => {
                const li = document.createElement('li');
                li.textContent = movie;
                topMoviesList.appendChild(li);
            });
        else if (movieType === 'worst_movies')
            (data.worst_movies || []).forEach(movie => {
                const li = document.createElement('li');
                li.textContent = movie;
                worstMoviesList.appendChild(li);
            });
    } catch (error) {
        console.error("Failed to load movie data:", error);
    }
}

console.log("script.js loaded");

async function searchMovie() {
    const input = document.getElementById('searchInput');
    const query = (input?.value || "").trim();

    let resultsDiv = document.getElementById('searchResults');
    if (!resultsDiv) {
        // Create results container if not present
        resultsDiv = document.createElement('div');
        resultsDiv.id = 'searchResults';
        resultsDiv.style.marginTop = '1rem';
        resultsDiv.style.padding = '0.75rem';
        resultsDiv.style.border = '1px solid #ddd';
        resultsDiv.style.borderRadius = '8px';
        input?.parentElement?.appendChild(resultsDiv);
    }
    resultsDiv.textContent = 'Searching…';

    if (!query) {
        resultsDiv.textContent = 'Please enter a keyword.';
        return;
    }

    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
            resultsDiv.textContent = 'No results found.';
            return;
        }

        // Grouped rendering: show movie title once, then all reviews as a list
        resultsDiv.innerHTML = '';

        // You may have multiple movies in future, so group reviews by title
        const grouped = {};

        data.forEach(item => {
            const title = item.movie_title || "Unknown Title";
            if (!grouped[title]) grouped[title] = [];
            grouped[title].push(item.review_content || "");
        });

        Object.keys(grouped).forEach(title => {
            // Title at top
            const titleElem = document.createElement('h2');
            titleElem.textContent = title;
            resultsDiv.appendChild(titleElem);

            // Reviews in a list
            const ul = document.createElement('ul');
            grouped[title].forEach(review => {
                const li = document.createElement('li');
                li.textContent = review;
                ul.appendChild(li);
            });
            resultsDiv.appendChild(ul);
        });
    } catch (err) {
        resultsDiv.textContent = 'Error: ' + err.message;
    }
}



let pendingReview = null;

async function addReview(confirm = null) {
    const movieNameInput = document.getElementById('movieNameInput');
    const reviewTextInput = document.getElementById('reviewTextInput');
    const reviewInputContainer = document.getElementById('reviewInputContainer');
    const reviewConfirmContainer = document.getElementById('reviewConfirmContainer');
    const suggestionText = document.getElementById('suggestionText');

    if (confirm !== null && pendingReview !== null) {
        if (confirm) {
            pendingReview.confirm = 'yes';
            await sendReview(pendingReview);
        } else {
            pendingReview = null;
            reviewConfirmContainer.style.display = 'none';
            reviewInputContainer.style.display = 'block';
            movieNameInput.value = '';
            reviewTextInput.value = '';
        }
        return;
    }

    const movieName = movieNameInput.value.trim();
    const reviewText = reviewTextInput.value.trim();

    if (!movieName || !reviewText) {
        alert('Please enter both movie name and review.');
        return;
    }

    const reviewData = { movie_name: movieName, review: reviewText };

    try {
        const response = await fetch('/add_review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reviewData)
        });
        const result = await response.json();

        if (response.status === 206 && result.suggestion) {
            // Show suggestion
            pendingReview = reviewData;
            suggestionText.textContent = `Did you mean "${result.suggestion}"?`;
            movieNameInput.value = result.suggestion; // Fill in the suggestion

            reviewInputContainer.style.display = 'none';
            reviewConfirmContainer.style.display = 'block';
        } else if (response.ok) {
            alert(result.message || 'Your review has been recorded.');
            movieNameInput.value = '';
            reviewTextInput.value = '';
            pendingReview = null;
            reviewConfirmContainer.style.display = 'none';
            reviewInputContainer.style.display = 'block';
        } else {
            alert(result.error || result.message || 'Failed to add review.');
        }
    } catch (error) {
        alert('Error submitting review. Please try again later.');
        console.error('Add review error:', error);
    }
}


async function sendReview(reviewData) {
    try {
        const response = await fetch('/add_review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reviewData)
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message || 'Your review has been recorded.');
            document.getElementById('movieNameInput').value = '';
            document.getElementById('reviewTextInput').value = '';
            document.getElementById('reviewConfirmContainer').style.display = 'none';
            document.getElementById('reviewInputContainer').style.display = 'block';
            pendingReview = null;
        } else {
            alert(result.error || result.message || 'Failed to add review.');
        }
    } catch (error) {
        alert('Error submitting confirmed review. Please try again later.');
        console.error('Send confirmed review error:', error);
    }
}

function confirmSuggestion(isConfirmed) { addReview(isConfirmed); }

async function loadSentimentAnalysis() {
    try {
        const response = await fetch('/sentiment_analysis');
        const data = await response.json();

        // Top sentiment formatting
        const topSection = document.getElementById('topSentiment');
        topSection.innerHTML = `
            <h3 style="margin-bottom: 8px;">Top Sentiment Score: ${data.top_sentiment.average_score.toFixed(2)}</h3>
            <ul style="padding-left: 0; list-style: none;">
            ${data.top_sentiment.reviews.map(r => `
                <li style="margin-bottom:16px;">
                    <span style="font-weight:bold;">${r.title}</span><br>
                    <span style="display:inline-block;margin-left:10px;">${r.review}</span>
                    <div style="font-size:13px;margin:2px 0 0 10px;color:#555;">
                        Sentiment: <span style="font-weight:bold;">${Number(r.score).toFixed(2)}</span>
                    </div>
                </li>
            `).join('')}
            </ul>
        `;

        // Worst sentiment formatting
        const worstSection = document.getElementById('worstSentiment');
        worstSection.innerHTML = `
            <h3 style="margin-top:32px;margin-bottom: 8px;">Worst Sentiment Score: ${data.worst_sentiment.average_score.toFixed(2)}</h3>
            <ul style="padding-left: 0; list-style: none;">
            ${data.worst_sentiment.reviews.map(r => `
                <li style="margin-bottom:16px;">
                    <span style="font-weight:bold;">${r.title}</span><br>
                    <span style="display:inline-block;margin-left:10px;">${r.review}</span>
                    <div style="font-size:13px;margin:2px 0 0 10px;color:#555;">
                        Sentiment: <span style="font-weight:bold;">${Number(r.score).toFixed(2)}</span>
                    </div>
                </li>
            `).join('')}
            </ul>
        `;
    } catch (error) {
        console.error('Error loading sentiment analysis:', error);
    }
}

let allMoviesData = []; // store all movies globally

async function loadAllMovies() {
    try {
        const response = await fetch('/all_movies');
        const data = await response.json();
        allMoviesData = data.movies || [];
        displayMovies(allMoviesData);
    } catch (error) {
        console.error("Failed to load all movies:", error);
    }
}

function displayMovies(movies) {
    const container = document.getElementById('allMoviesList');
    container.innerHTML = '';

    movies.forEach(movie => {
        const li = document.createElement('li');
        li.innerHTML = `${movie.movie_title}<br><span style="font-size:0.9em; color:#555;">(${movie.genres})</span>`;
        container.appendChild(li);
    });
}

function sortMovies() {
    const order = document.getElementById('sortOrder').value;
    let sortedMovies = [...allMoviesData];

    if (order === 'asc') {
        sortedMovies.sort((a, b) => a.movie_title.localeCompare(b.movie_title));
    } else if (order === 'desc') {
        sortedMovies.sort((a, b) => b.movie_title.localeCompare(a.movie_title));
    }

    displayMovies(sortedMovies);
}


function showSection(sectionId) {
    document.querySelectorAll('.tabContent').forEach(s => (s.style.display = 'none'));
    const target = document.getElementById(sectionId);
    if (target) target.style.display = 'block';

    if (sectionId === 'sentimentSection') loadSentimentAnalysis();
    if (sectionId === "topReviews") loadMovies('top_movies');
    else if (sectionId === "worstReviews") loadMovies('worst_movies');
}

async function compareMovies() {
    const movie1 = document.getElementById('compareMovie1').value.trim();
    const movie2 = document.getElementById('compareMovie2').value.trim();
    const resultDiv = document.getElementById('comparisonResult');
    
    if (!movie1 || !movie2) {
        resultDiv.innerHTML = "<p>Please enter both movie names.</p>";
        return;
    }

    resultDiv.innerHTML = "<p>Comparing...</p>";

    try {
        const response = await fetch(`/compare_movies?movie1=${encodeURIComponent(movie1)}&movie2=${encodeURIComponent(movie2)}`);
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
            return;
        }

        // Display results in a readable format
        resultDiv.innerHTML = `
            <h4>Comparison Results:</h4>
            <table border="1" cellpadding="8" style="border-collapse: collapse;">
                <tr>
                    <th>Movie</th>
                    <th>Average Sentiment</th>
                    <th>Number of Reviews</th>
                </tr>
                ${Object.entries(data).map(([title, stats]) => `
                    <tr>
                        <td>${title}</td>
                        <td>${stats.average_sentiment?.toFixed(2) ?? "N/A"}</td>
                        <td>${stats.review_count ?? "N/A"}</td>
                    </tr>
                `).join('')}
            </table>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
}


document.addEventListener("DOMContentLoaded", () => {
    showSection('homeSection'); // Show home by default
    loadAllMovies(); // Load movies immediately
});