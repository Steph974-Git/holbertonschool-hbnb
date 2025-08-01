console.log("JS chargé !");

/* 
  Fichier principal pour la gestion du front HBnB.
*/

// ------------------------------------------------------
// Au chargement de la page, on lance tout notre JS "front" principal
// ------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
    // === 1. Gestion du formulaire de login ===
    // (Uniquement sur la page login.html)
    const loginForm = document.getElementById('login-form');
    const screamerWelcome = document.getElementById('screamer-welcome'); // Message "Bienvenue !" animé
    const screamAudio = document.getElementById('scream-audio'); // Son d'ambiance

    if (loginForm) {
        // Ajoute un écouteur sur la soumission du formulaire de login
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Empêche le rechargement de la page

            // On récupère les valeurs du formulaire
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Fonction interne qui effectue réellement la connexion
            async function loginUser(email, password) {
                try {
                    // Appel API : envoie les identifiants à l'API
                    const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    
                    if (response.ok) {
                        // Connexion réussie !
                        const data = await response.json();
                        document.cookie = `token=${data.access_token}; path=/`; // Stocke le token JWT

                        // --- Effets "horror" visuels et sonores ---
                        // 1. Lance le son screamer
                        if (screamAudio) {
                            screamAudio.currentTime = 0;
                            screamAudio.play();
                        }
                        // 2. Affiche le message "Bienvenue !" avec effet animé
                        if (screamerWelcome) {
                            screamerWelcome.style.display = 'flex';
                            screamerWelcome.classList.add('show');
                            setTimeout(() => {
                                screamerWelcome.classList.remove('show');
                                screamerWelcome.style.display = 'none';
                            }, 3500); // Même durée que l'animation CSS
                        }
                        // 3. Redirige vers la page d’accueil après l’animation
                        setTimeout(() => {
                            window.location.href = 'index.html';
                        }, 3500);
                    } else {
                        // Connexion échouée : affiche le message d’erreur renvoyé par l’API
                        await showApiError(response, "Erreur lors de la connexion.");
                    }
                } catch (error) {
                    // Erreur réseau (serveur down, mauvaise URL, etc.)
                    await showApiError({json: async () => ({message: "Erreur réseau."})});
                }
            }

            // On lance le login à partir des valeurs du formulaire (pas d’animation avant le login, tout est après)
            await loginUser(email, password);
        });
    }

    // === 2. Affichage dynamique du bouton Login/Logout + chargement des lieux ===
    checkAuthentication();

    // === 3. Génération dynamique du filtre par prix ===
    populatePriceFilter();

    // Ajoute l’écouteur pour le changement de filtre de prix sur la liste des lieux
    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
        priceFilter.addEventListener('change', filterPlacesByPrice);
    }

    // === 4. Détail d’un lieu (uniquement sur place.html) ===
    const placeDetailsSection = document.getElementById('place-details');
    if (placeDetailsSection) {
        const placeId = getPlaceIdFromURL();
        if (!placeId) {
            // Pas d’ID dans l’URL → message d’erreur
            placeDetailsSection.innerHTML = "<p>Erreur : aucun ID de lieu fourni.</p>";
        } else {
            const token = getCookie('token');
            // Affiche la section "ajouter un avis" seulement si utilisateur connecté
            const addReviewSection = document.getElementById('add-review');
            if (addReviewSection) {
                addReviewSection.style.display = token ? 'block' : 'none';
            }
            // Charge les détails du lieu + reviews depuis l’API
            await fetchPlaceDetails(token, placeId);
        }
    }

    // === 5. Gestion du formulaire d'ajout d'avis (review) ===
    // (Seulement sur la page détail de lieu)
    const reviewForm = document.getElementById('review-form');
    const placeId = getPlaceIdFromURL();
    const token = getCookie('token');

    if (reviewForm && placeId && token) {
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            // On récupère le texte de l’avis (nom du textarea peut varier selon la page)
            let comment = '';
            const reviewTextarea = document.getElementById('review');
            const commentTextarea = document.getElementById('comment');
            if (reviewTextarea) comment = reviewTextarea.value;
            if (commentTextarea) comment = commentTextarea.value;

            const rating = document.getElementById('rating').value;

            try {
                // Envoie la review à l’API (avec le JWT)
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
                    // Succès : avertit l’utilisateur et recharge la liste des reviews
                    alert('Avis ajouté avec succès !');
                    reviewForm.reset();
                    await fetchPlaceDetails(token, placeId);
                } else {
                    // Erreur API (ex : déjà review, avis sur sa propre place, etc.)
                    await showApiError(response, "Erreur lors de l'ajout de l'avis.");
                }
            } catch (error) {
                await showApiError({json: async () => ({message: "Erreur réseau."})});
            }
        });
    }

});

// ------------------------------------------------------
// Vérifie si l'utilisateur est connecté, et gère l'affichage du bouton login (ou fetch les places si connecté)
// ------------------------------------------------------
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    // Sur les pages protégées, redirige si non connecté
    if (!token && window.location.pathname.endsWith('place.html')) {
        window.location.href = 'index.html';
    }
    // Gère l’affichage du bouton Login/Logout
    if (!loginLink) return;
    if (!token) {
        loginLink.style.display = 'block';
    } else {
        loginLink.style.display = 'none';
        fetchPlaces(token); // Charge la liste des lieux si connecté
    }
}

// ------------------------------------------------------
// Récupère la valeur d'un cookie donné par son nom (ex: token)
// ------------------------------------------------------
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

// ------------------------------------------------------
// Récupère la liste des lieux via l’API, et l’affiche (pour la page d'accueil/index.html)
// ------------------------------------------------------
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
        window.allPlaces = places; // Stockage global (pour filtrer sans re-fetch)
        displayPlaces(places);
    } else {
        await showApiError(response, "Impossible de charger les lieux.");
    }
}

// ------------------------------------------------------
// Affiche dynamiquement chaque lieu sous forme de "carte" (card) sur la page d'accueil
// ------------------------------------------------------
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;
    placesList.innerHTML = '';

    // Crée une card HTML pour chaque lieu
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
        card.dataset.price = place.price; // Pour le filtrage client
        placesList.appendChild(card);
    });
}

// ------------------------------------------------------
// Génère le menu déroulant de prix pour filtrer la liste (10/50/100/All)
// ------------------------------------------------------
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

// ------------------------------------------------------
// Filtre les lieux selon le prix choisi dans le menu déroulant
// ------------------------------------------------------
function filterPlacesByPrice() {
    const maxPrice = document.getElementById('price-filter').value;
    if (window.allPlaces && Array.isArray(window.allPlaces) && window.allPlaces.length > 0) {
        let filtered = window.allPlaces;
        if (maxPrice !== 'All') {
            filtered = filtered.filter(place => Number(place.price) <= Number(maxPrice));
        }
        displayPlaces(filtered);
    } else {
        // Fallback si la liste globale n'est pas dispo (ex : tout était en HTML, non JS)
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

// ------------------------------------------------------
// Extrait l'ID du lieu dans l’URL (ex : place.html?id=12 → "12")
// ------------------------------------------------------
function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// ------------------------------------------------------
// Récupère les détails d'un lieu et toutes ses reviews, puis les affiche
// ------------------------------------------------------
async function fetchPlaceDetails(token, placeId) {
    try {
        // 1. D’abord, récupère les détails du lieu
        const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            }
        });
        if (response.ok) {
            const place = await response.json();

            // 2. Ensuite, récupère toutes les reviews de ce lieu
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

// ------------------------------------------------------
// Affiche dynamiquement tous les détails d’un lieu + ses reviews
// ------------------------------------------------------
function displayPlaceDetails(place) {
    // Conteneur principal
    const placeDetails = document.getElementById('place-details');
    placeDetails.innerHTML = '';

    // Affiche l’image du lieu (ou une image par défaut)
    let imageTag = '';
    if (place.images) {
        imageTag = `<img src="${place.images}" alt="${place.title || place.name}" class="place-img">`;
    } else {
        imageTag = `<img src="images/default.jpg" alt="No image" class="place-img">`;
    }

    // Bloc principal d’infos sur le lieu
    const infoDiv = document.createElement('div');
    infoDiv.className = 'place-info';
    infoDiv.innerHTML = `
        ${imageTag}
        <h2>${place.title || place.name || 'Sans titre'}</h2>
        <p><strong>Host:</strong> ${place.owner ? (place.owner.first_name + ' ' + place.owner.last_name) : 'N/A'}</p>
        <p><strong>Price per night:</strong> $${place.price}</p>
        <p><strong>Description:</strong> ${place.description || ''}</p>
        <p><strong>Amenities:</strong> ${place.amenities ? place.amenities.map(a => a.name).join(', ') : 'Aucun'}</p>
    `;
    placeDetails.appendChild(infoDiv);

    // Affiche les reviews (ou un message si aucune review)
    let reviewsList = document.getElementById('reviews-list');
    if (!reviewsList) {
        reviewsList = document.createElement('div');
        reviewsList.id = 'reviews-list';
        placeDetails.parentNode.insertBefore(reviewsList, placeDetails.nextSibling);
    }
    reviewsList.innerHTML = '';

    if (place.reviews && place.reviews.length > 0) {
        place.reviews.forEach(review => {
            const reviewDiv = document.createElement('div');
            reviewDiv.className = 'review-card';
            reviewDiv.innerHTML = `
                <p><strong>User:</strong> ${review.first_name ? review.first_name + ' ' + review.last_name : (review.user_name || 'Anonyme')}</p>
                <p>"${review.text || ''}"</p>
                <p><strong>Rating:</strong> ${review.rating || 'N/A'}/5</p>
            `;
            reviewsList.appendChild(reviewDiv);
        });
    } else {
        const noReview = document.createElement('p');
        noReview.textContent = 'No reviews yet.';
        reviewsList.appendChild(noReview);
    }
}

/**
 * Affiche un message d’erreur venant de l’API (dans une div dédiée),
 * ou un message par défaut si pas trouvé dans la réponse.
 */
async function showApiError(response, defaultMsg = "Erreur lors de l’opération.") {
    let errorMsg = defaultMsg;
    try {
        // On tente de lire l’erreur renvoyée par l’API (JSON)
        const data = await response.json();
        if (data && (data.message || data.error || data.detail)) {
            errorMsg = data.message || data.error || data.detail;
        }
    } catch (e) {
        // Cas où la réponse n’est pas du JSON
        console.log("showApiError CATCH", e);
    }

    // Affiche le message dans la div dédiée à l’erreur
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = errorMsg;
        errorDiv.style.display = 'block';
        // Masque automatiquement l’erreur après 5 secondes
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}
