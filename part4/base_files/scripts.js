console.log("JS chargé !");

/* 
  Fichier principal pour la gestion du front HBnB.
  Toutes les instructions sont commentées en français pour faciliter la compréhension.
*/

// 1. Exécution du code une fois que la page est entièrement chargée
document.addEventListener('DOMContentLoaded', async () => {
    // ----- Gestion du formulaire de login (uniquement sur la page login) -----
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            await loginUser(email, password);

            async function loginUser(email, password) {
                const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.access_token}; path=/`;
                    window.location.href = 'index.html';
                } else {
                    alert('Login failed: ' + response.statusText);
                }
            }
        });
    }

    // ----- Gestion de l'affichage du bouton Login et du chargement de la liste des lieux -----
    checkAuthentication();

    // ----- Génération dynamique du menu déroulant pour filtrer les lieux par prix -----
    populatePriceFilter();

    // ----- Ajoute un écouteur d'événement sur le filtre de prix pour mettre à jour la liste -----
    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
        priceFilter.addEventListener('change', filterPlacesByPrice);
    }

    // ----- Détail d’un lieu (page place.html uniquement) -----
    const placeDetailsSection = document.getElementById('place-details');
    if (placeDetailsSection) {
        const placeId = getPlaceIdFromURL();
        if (!placeId) {
            placeDetailsSection.innerHTML = "<p>Erreur : aucun ID de lieu fourni.</p>";
        } else {
            const token = getCookie('token');
            // Affiche/masque la section "ajouter un avis" selon l’authentification
            const addReviewSection = document.getElementById('add-review');
            if (addReviewSection) {
                addReviewSection.style.display = token ? 'block' : 'none';
            }
            await fetchPlaceDetails(token, placeId);
        }
    }

    // ----- Gestion du formulaire d'ajout d'avis (page place.html uniquement) -----
    const reviewForm = document.getElementById('review-form');
    const placeId = getPlaceIdFromURL();
    const token = getCookie('token');

    if (reviewForm && placeId && token) {
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Empêche le rechargement et l'ajout à l'URL

            const comment = document.getElementById('comment').value;
            const rating = document.getElementById('rating').value;

            try {
                const response = await fetch(`http://127.0.0.1:5000/api/v1/reviews/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        text: comment,
                        rating: rating,
                        place_id: placeId
                    })
                });
                if (response.ok) {
                    alert('Avis ajouté avec succès !');
                    reviewForm.reset();
                    // Optionnel : recharger les reviews
                    await fetchPlaceDetails(token, placeId);
                } else {
                    alert('Erreur lors de l\'ajout de l\'avis.');
                }
            } catch (error) {
                alert('Erreur réseau.');
            }
        });
    }
});

// ----- Vérifie si l’utilisateur est connecté, gère l’affichage du lien login (sur toutes les pages où il existe) -----
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    // Redirige uniquement si on est sur une page protégée
    if (!token && window.location.pathname.endsWith('place.html')) {
        window.location.href = 'index.html';
    }
    if (!loginLink) return;
    if (!token) {
        loginLink.style.display = 'block';
    } else {
        loginLink.style.display = 'none';
        fetchPlaces(token);
    }
}

// ----- Récupère la valeur d'un cookie à partir de son nom -----
function getCookie(cookieName) {
    const cookies = document.cookie.split('; ');
    for (const cookie of cookies) {
        const [name, value] = cookie.split('=');
        if (name === cookieName) {
            return decodeURIComponent(value);
        }
    }
    return null;
}

// ----- Requête AJAX pour récupérer la liste des lieux (pour index.html) -----
async function fetchPlaces(token) {
    const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
    });

    if (response.ok) {
        const places = await response.json();
        window.allPlaces = places;
        displayPlaces(places);
    } else {
        const placesList = document.getElementById('places-list');
        if (placesList) {
            placesList.innerHTML = '<p>Failed to load places.</p>';
        }
    }
}

// ----- Génère dynamiquement les cards pour chaque lieu (index.html) -----
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;
    placesList.innerHTML = '';

    places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.innerHTML = `
            <img src="${place.images || 'images/default.jpg'}" alt="${place.title || place.name}" class="place-img">
            <h3>${place.title || place.name}</h3>
            <p>Price per night: $${place.price}</p>
            <p>${place.description || ''}</p>
            <p>Location: Lat. ${place.latitude}, Long. ${place.longitude}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;
        card.dataset.price = place.price;
        placesList.appendChild(card);
    });
}

// ----- Génère les options du menu déroulant de prix pour le filtre client -----
function populatePriceFilter() {
    const priceFilter = document.getElementById('price-filter');
    if (!priceFilter) return;
    priceFilter.innerHTML = '';
    [10, 50, 100, 'All'].forEach(val => {
        const opt = document.createElement('option');
        opt.value = val;
        opt.textContent = val === 'All' ? 'All' : `$${val}`;
        priceFilter.appendChild(opt);
    });
    priceFilter.value = 'All';
}

// ----- Filtre la liste des lieux selon le prix sélectionné -----
function filterPlacesByPrice() {
    const maxPrice = document.getElementById('price-filter').value;
    if (window.allPlaces && Array.isArray(window.allPlaces) && window.allPlaces.length > 0) {
        let filtered = window.allPlaces;
        if (maxPrice !== 'All') {
            filtered = filtered.filter(place => Number(place.price) <= Number(maxPrice));
        }
        displayPlaces(filtered);
    } else {
        document.querySelectorAll('.place-card').forEach(card => {
            const priceP = Array.from(card.querySelectorAll('p')).find(p => p.textContent.includes('Price per night'));
            if (!priceP) return;
            const priceMatch = priceP.textContent.match(/\$?(\d+)/);
            const price = priceMatch ? parseInt(priceMatch[1]) : 0;
            if (maxPrice === 'All' || price <= parseInt(maxPrice)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
}

// ----- Récupère l'ID d'un lieu dans l'URL de la page détail -----
function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// ----- Requête AJAX pour récupérer les détails d'un lieu et ses reviews -----
async function fetchPlaceDetails(token, placeId) {
    try {
        // 1. Récupère les détails du lieu
        const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            }
        });
        if (response.ok) {
            const place = await response.json();

            // 2. Récupère les reviews du lieu
            const reviewsResponse = await fetch(`http://127.0.0.1:5000/api/v1/reviews/places/${placeId}/reviews`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                }
            });
            if (reviewsResponse.ok) {
                place.reviews = await reviewsResponse.json();
            } else {
                place.reviews = [];
            }

            displayPlaceDetails(place);
        } else {
            document.getElementById('place-details').innerHTML = '<p>Erreur de chargement du lieu.</p>';
        }
    } catch (error) {
        document.getElementById('place-details').innerHTML = '<p>Erreur réseau.</p>';
    }
}

// ----- Génère dynamiquement le détail d'un lieu (et ses reviews) -----
function displayPlaceDetails(place) {
    const placeDetails = document.getElementById('place-details');
    placeDetails.innerHTML = '';

    // Bloc principal d'infos sur le lieu
    const infoDiv = document.createElement('div');
    infoDiv.className = 'place-info';

    infoDiv.innerHTML = `
        <h2>${place.title || place.name || 'Sans titre'}</h2>
        <p><strong>Host:</strong> ${place.owner ? (place.owner.first_name + ' ' + place.owner.last_name) : 'N/A'}</p>
        <p><strong>Price per night:</strong> $${place.price}</p>
        <p><strong>Description:</strong> ${place.description || ''}</p>
        <p><strong>Amenities:</strong> ${place.amenities ? place.amenities.map(a => a.name).join(', ') : 'Aucun'}</p>
    `;
    placeDetails.appendChild(infoDiv);

    // Ajout des reviews s'il y en a
    if (place.reviews && place.reviews.length > 0) {
        const reviewsList = document.createElement('div');
        reviewsList.id = 'reviews-list';
        place.reviews.forEach(review => {
            const reviewCard = document.createElement('article');
            reviewCard.className = 'review-card';
            reviewCard.innerHTML = `
                <p>"${review.text || review.comment || ''}"</p>
                <span>
                    par ${review.first_name || ''} ${review.last_name || review.user_name || 'Anonyme'}
                    - Note : ${review.rating || 'N/A'}/5
                </span>
            `;
            reviewsList.appendChild(reviewCard);
        });
        placeDetails.appendChild(reviewsList);
    } else {
        const noReview = document.createElement('p');
        noReview.textContent = 'No reviews yet.';
        placeDetails.appendChild(noReview);
    }
}
