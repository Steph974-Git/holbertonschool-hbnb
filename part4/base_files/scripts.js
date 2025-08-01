console.log("JS chargé !");

/* 
  Fichier principal pour la gestion du front HBnB.
  Toutes les instructions sont commentées en français pour faciliter la compréhension.
*/

// 1. Exécution du code une fois que la page est entièrement chargée
document.addEventListener('DOMContentLoaded', async () => {
    // ----- Gestion du formulaire de login (uniquement sur la page login) -----
    const loginForm = document.getElementById('login-form');
    const screamerWelcome = document.getElementById('screamer-welcome');
    const screamAudio = document.getElementById('scream-audio');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            // Joue le son de screamer si présent
            if (screamAudio) {
                screamAudio.currentTime = 0;
                screamAudio.play();
            }

            // Affiche l'effet "Bienvenue !" fantomatique si présent
            if (screamerWelcome) {
                screamerWelcome.style.display = 'flex';
                screamerWelcome.classList.add('show');

                // Supprime la classe show et masque après l'animation CSS
                setTimeout(() => {
                    screamerWelcome.classList.remove('show');
                    screamerWelcome.style.display = 'none';
                }, 3500); // Même durée que l'animation CSS !
            }

            // Démarre le login après l'animation + petit délai
            setTimeout(async () => {
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                await loginUser(email, password);

                // Fonction de login utilisateur
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
                        await showApiError(response, "Erreur lors de la connexion.");
                    }
                }
            }, 3500); // Idem ici, égal à la durée de l'animation
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
            event.preventDefault();

            // Récupère la valeur du textarea selon l'id disponible (review ou comment)
            let comment = '';
            const reviewTextarea = document.getElementById('review');
            const commentTextarea = document.getElementById('comment');
            if (reviewTextarea) comment = reviewTextarea.value;
            if (commentTextarea) comment = commentTextarea.value;

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
                    await fetchPlaceDetails(token, placeId);
                } else {
                    await showApiError(response, "Erreur lors de l'ajout de l'avis.");
                }
            } catch (error) {
                await showApiError({json: async () => ({message: "Erreur réseau."})});
            }
        });
    }

    // Suppression de la génération des .magic-bubble pour n'avoir que les bulles canvas
    // (rien à faire ici)
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
        await showApiError(response, "Impossible de charger les lieux.");
    }
}

// ----- Génère dynamiquement les cards pour chaque lieu (index.html) -----
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;
    placesList.innerHTML = '';

    // Pour chaque lieu, crée une card et l'ajoute à la liste
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
        // Fallback si la liste globale n'est pas dispo
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
    // Affiche les infos principales du lieu
    const placeDetails = document.getElementById('place-details');
    placeDetails.innerHTML = '';

    // Ajout de l'image du lieu
    let imageTag = '';
    if (place.images) {
        imageTag = `<img src="${place.images}" alt="${place.title || place.name}" class="place-img">`;
    } else {
        imageTag = `<img src="images/default.jpg" alt="No image" class="place-img">`;
    }

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

    // Affiche les reviews sous la place
    let reviewsList = document.getElementById('reviews-list');
    if (!reviewsList) {
        reviewsList = document.createElement('div');
        reviewsList.id = 'reviews-list';
        // Ajoute-le juste après place-details
        placeDetails.parentNode.insertBefore(reviewsList, placeDetails.nextSibling);
    }
    reviewsList.innerHTML = ''; // On vide d'abord

    // Affiche chaque review ou un message s'il n'y en a pas
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

// ----- Gestion de l'animation du canvas d'ombres mouvantes -----
const canvas = document.getElementById("shadow-bg");
const ctx = canvas.getContext("2d");

// Redimensionne le canvas à la taille de la fenêtre
function resizeShadowCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resizeShadowCanvas();
window.addEventListener('resize', resizeShadowCanvas);

// Génère un nombre aléatoire entre min et max
function random(min, max) {
  return Math.random() * (max - min) + min;
}

// Classe représentant une tache/silhouette mouvante
class MovingShadow {
  constructor() {
    this.radius = random(120, 350);
    this.x = random(-100, canvas.width + 100);
    this.y = random(canvas.height * 0.2, canvas.height * 0.93);
    this.ampX = random(60, 210);
    this.ampY = random(20, 75);
    this.speed = random(0.09, 0.25);
    this.offset = random(0, Math.PI * 2);
    this.alpha = random(0.08, 0.19);
    this.blur = random(60, 130);
    this.lifetime = random(18, 32); // secondes avant de “mourir”
    this.birth = performance.now() / 1000;
    this.verticalDrift = random(-0.08, 0.08);
  }

  get age() {
    return (performance.now() / 1000) - this.birth;
  }
  get dead() {
    return this.age > this.lifetime;
  }

  // Met à jour la position de la tache
  update(dt) {
    const t = this.age + this.offset;
    this.x += Math.sin(t * this.speed) * this.ampX * 0.0005 * dt;
    this.y += Math.sin(t * this.speed * 0.6) * this.ampY * 0.0009 * dt + this.verticalDrift * dt * 0.018;
    // Déplacement lent latéral : le “brouillard” glisse
    this.x += (this.ampX > 110 ? 0.03 : -0.05) * dt * 0.018;
  }

  // Dessine la tache sur le canvas
  draw(ctx) {
    ctx.save();
    ctx.globalAlpha = this.alpha * (1 - (this.age / this.lifetime) * 0.7); // s'estompe doucement
    ctx.filter = `blur(${this.blur}px)`;
    ctx.beginPath();
    ctx.ellipse(
      this.x,
      this.y,
      this.radius * (1 + Math.sin(this.age * 0.23 + this.offset) * 0.12),
      this.radius * (0.85 + Math.cos(this.age * 0.19 - this.offset) * 0.15),
      Math.sin(this.age * 0.18 + this.offset) * 0.8,
      0, Math.PI * 2
    );
    ctx.fillStyle = "#000";
    ctx.fill();
    ctx.restore();
    ctx.filter = "none";
  }
}

let shadows = [];
// Ajoute une nouvelle tache si besoin
function addShadow() {
  if (shadows.length < 7 && Math.random() > 0.4) {
    shadows.push(new MovingShadow());
  }
}

let lastTime = 0;
// Boucle d'animation principale pour les ombres mouvantes
function animateShadow(time) {
  let dt = (time - lastTime) || 16;
  lastTime = time;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Met à jour et dessine chaque tache
  shadows.forEach(s => s.update(dt));
  shadows.forEach(s => s.draw(ctx));
  shadows = shadows.filter(s => !s.dead);

  // Ajoute des nouvelles taches
  addShadow();

  requestAnimationFrame(animateShadow);
}
animateShadow(0);

/**
 * Affiche une alerte avec le message d’erreur venant de l’API,
 * ou un message par défaut si pas trouvé.
 * Peut être amélioré pour afficher dans le DOM si tu préfères.
 */
async function showApiError(response, defaultMsg = "Erreur lors de l’opération.") {
    let errorMsg = defaultMsg;
    try {
        const data = await response.json();
        if (data && (data.message || data.error || data.detail)) {
            errorMsg = data.message || data.error || data.detail;
        }
    } catch (e) {console.log("showApiError CATCH", e); // <- TEST
        }

    // Affiche dans la div (si elle existe)
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = errorMsg;
        errorDiv.style.display = 'block';
        // Efface après 5 secondes
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}
