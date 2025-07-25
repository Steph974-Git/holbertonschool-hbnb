/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

document.addEventListener('DOMContentLoaded', () => {
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
                    headers: {
                        'Content-Type': 'application/json'
                    },
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
});

function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (!token) {
        loginLink.style.display = 'block';
    } else {
        loginLink.style.display = 'none';
        // Fetch places data if the user is authenticated
        fetchPlaces(token);
    }
}

function getCookie(cookieName) {
    // Découpe tous les cookies en un tableau
    const cookies = document.cookie.split('; ');
    // Parcourt chaque cookie
    for (const cookie of cookies) {
        // Sépare le nom et la valeur du cookie
        const [name, value] = cookie.split('=');
        // Si le nom correspond à celui recherché, retourne la valeur décodée
        if (name === cookieName) {
            return decodeURIComponent(value);
        }
    }
    // Retourne null si le cookie n'est pas trouvé
    return null;
}
async function fetchPlaces(token) {
                const response = await fetch('http://127.0.0.1:5000/api/v1/auth/places', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                        (token && { 'Authorization': `Bearer ${token}` }) // Ajoute le token si présent
                    }
        });

        if (response.ok) {
            const places = await response.json(); // Récupère les données des lieux
            displayPlaces(places); // Affiche les lieux
        } else {
            document.getElementById('places-list').innerHTML = '<p>Failed to load places.</p>';
        }
            }
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = ''; // 1. Vide la liste

    // 2. Parcourt chaque lieu
    places.forEach(place => {
        // 3. Crée la card
        const card = document.createElement('div');
        card.className = 'place-card';

    }
}