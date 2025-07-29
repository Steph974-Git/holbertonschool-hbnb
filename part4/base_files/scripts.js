console.log("JS chargé !");

/* 
  Fichier principal pour la gestion du front HBnB.
  Toutes les instructions sont commentées en français pour faciliter la compréhension.
*/

// 1. Exécution du code une fois que la page est entièrement chargée
document.addEventListener('DOMContentLoaded', () => {
    // ----- Gestion du formulaire de login (uniquement sur la page login) -----
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Empêche la soumission classique du formulaire

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            await loginUser(email, password);

            // Fonction interne de login AJAX
            async function loginUser(email, password) {
                const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    // Stocke le token JWT dans les cookies pour l’authentification future
                    document.cookie = `token=${data.access_token}; path=/`;
                    // Redirige l'utilisateur vers la page d'accueil après connexion
                    window.location.href = 'index.html';
                } else {
                    // Affiche une alerte si la connexion a échoué
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
    // Si la page contient la section place-details, alors on est sur la page détail d'un lieu
    const placeDetailsSection = document.getElementById('place-details');
    if (placeDetailsSection) {
        const placeId = getPlaceIdFromURL(); // Récupère l’ID du lieu via l’URL
        if (!placeId) {
            placeDetailsSection.innerHTML = "<p>Erreur : aucun ID de lieu fourni.</p>";
        } else {
            const token = getCookie('token');
            // Gère l’affichage du formulaire d’ajout de review selon connexion
            const addReviewSection = document.getElementById('add-review');
            if (addReviewSection) {
                addReviewSection.style.display = token ? 'block' : 'none';
            }
            fetchPlaceDetails(token, placeId); // Charge et affiche dynamiquement les infos du lieu
        }
    }
});

// ----- Vérifie si l’utilisateur est connecté, gère l’affichage du lien login (sur toutes les pages où il existe) -----
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    if (!loginLink) {
        // Pas de lien login sur cette page : rien à faire
        return;
    }
    if (!token) {
        // Pas de token : on affiche le bouton login
        loginLink.style.display = 'block';
    } else {
        // Token trouvé : on cache le bouton login et on charge la liste des lieux (index.html)
        loginLink.style.display = 'none';
        fetchPlaces(token);
    }
}

// ----- Récupère la valeur d'un cookie à partir de son nom -----
function getCookie(cookieName) {
    // On récupère tous les cookies et on les sépare par '; '
    const cookies = document.cookie.split('; ');
    for (const cookie of cookies) {
        const [name, value] = cookie.split('=');
        if (name === cookieName) {
            // On retourne la valeur décodée si le nom correspond
            return decodeURIComponent(value);
        }
    }
    // Si pas trouvé, retourne null
    return null;
}

// ----- Requête AJAX pour récupérer la liste des lieux (pour index.html) -----
async function fetchPlaces(token) {
    const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            // Ajoute le token JWT si disponible pour les routes protégées
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
    });

    if (response.ok) {
        // On stocke tous les lieux dans une variable globale pour le filtrage
        const places = await response.json();
        window.allPlaces = places;
        displayPlaces(places); // Affiche dynamiquement les cards de lieux
    } else {
        // Affiche un message d'erreur si la récupération échoue
        document.getElementById('places-list').innerHTML = '<p>Failed to load places.</p>';
    }
}

// ----- Génère dynamiquement les cards pour chaque lieu (index.html) -----
function displayPlaces(places) {
    console.log("places reçues :", places);
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = ''; // On vide avant de remplir

    places.forEach(place => {
        // Crée une card pour chaque lieu
        const card = document.createElement('div');
        card.className = 'place-card';
        card.innerHTML = `
            <h3>${place.title}</h3>
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
    priceFilter.value = 'All'; // Affiche tout par défaut
}

// ----- Filtre la liste des lieux selon le prix sélectionné -----
function filterPlacesByPrice() {
    const maxPrice = document.getElementById('price-filter').value;
    let filtered = window.allPlaces || [];
    if (maxPrice !== 'All') {
        filtered = filtered.filter(place => Number(place.price) <= Number(maxPrice));
    }
    displayPlaces(filtered);
}

// ----- Récupère l'ID d'un lieu dans l'URL de la page détail -----
function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// ----- Requête AJAX pour récupérer les détails d'un lieu et ses reviews -----
async function fetchPlaceDetails(token, placeId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            }
        });
        if (response.ok) {
            const place = await response.json();
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
    placeDetails.innerHTML = ''; // Vide le bloc avant d'afficher

    // Bloc principal d'infos sur le lieu
    const infoDiv = document.createElement('div');
    infoDiv.className = 'place-info';

    // Affiche le titre, le propriétaire, le prix, la description, les amenities
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
        place.reviews.forEach(review => {
            const reviewDiv = document.createElement('div');
            reviewDiv.className = 'review-card';
            reviewDiv.innerHTML = `
                <p><strong>User:</strong> ${review.user_name || review.user_id || 'Anonyme'}</p>
                <p>"${review.text || ''}"</p>
                <p><strong>Rating:</strong> ${review.rating || 'N/A'}/5</p>
            `;
            placeDetails.appendChild(reviewDiv);
        });
    } else {
        // Si aucune review, affiche un message
        const noReview = document.createElement('p');
        noReview.textContent = 'No reviews yet.';
        placeDetails.appendChild(noReview);
    }
}
