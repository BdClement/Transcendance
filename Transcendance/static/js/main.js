// Fonction pour obtenir l'URL actuelle sans le domaine
// function getCurrentPath() {
//     return window.location.pathname.substring(1); // Supprimer le '/' initial
// }

function getCurrentPath() {
    let path = window.location.pathname.substring(1); // Supprimer le '/' initial
    return path.endsWith('/') ? path.slice(0, -1) : path; // Enlever le '/' final si présent
}

// Fonction pour afficher le contenu basé sur l'URL
function displayContent() {
    const path = getCurrentPath();
    const appElement = document.getElementById('app');

    if (path === 'home') {
        appElement.innerHTML = `
        <h1>Welcome on Transcendance</h1>
        <button onclick="navigate(event, 'home/play')">Jouer</button>
        <button onclick="testWebSocket()">Test WebSocket</button>
    `;
    }else if (path === 'home/play'){
        appElement.innerHTML = `
        <h1>Let's Play!</h1>
        <p>This is the play page content.</p>
    `;
    } else {
		appElement.innerHTML = '<p>Page not found</p>';
		// appElement.innerHTML = path;
    }
}

// Fonction pour gérer la navigation
function navigate(event, path) {
    event.preventDefault(); // Empêche le rechargement de la page
    history.pushState({}, '', `/${path}`); // Met à jour l'URL sans recharger
    displayContent(); // Affiche le contenu correspondant à la nouvelle URL
}

// Gérer la navigation avec le bouton "Retour" du navigateur
window.addEventListener('popstate', displayContent);

// Exécuter la fonction displayContent lorsque le DOM est complètement chargé
document.addEventListener('DOMContentLoaded', displayContent);


// Créer une connexion WebSocket
let socket;

function createWebSocket() {
    // socket = new WebSocket('ws/game/1://localhost:6379'); // Remplacez l'URL par celle de votre serveur WebSocket
    socket = new WebSocket('ws://localhost:8000/ws/game/'); // Remplacez l'URL par celle de votre serveur WebSocket

    socket.onopen = function() {
        console.log('Connexion WebSocket ouverte');
        // Connexion ouverte, vous pouvez maintenant envoyer des messages
        socket.send('Hello from client!');
        console.log('Message envoyé : Hello from client!');
    };

    // Gérer les messages reçus
    socket.onmessage = function(event) {
        console.log('Message reçu du serveur :', event.data);
    };

    // Gérer les erreurs
    socket.onerror = function(error) {
        console.error('Erreur WebSocket :', error);
    };

    // Gérer la fermeture de la connexion
    socket.onclose = function() {
        console.log('Connexion WebSocket fermée');
    };

    // console.log('Connexion WebSocket créée');
}

// Fonction pour tester le WebSocket en envoyant un message
function testWebSocket() {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.log('Création de la connexion WebSocket...');
        createWebSocket();
    }

    // Assurez-vous que la connexion est ouverte avant d'envoyer le message
    // if (socket.readyState === WebSocket.OPEN) {
    //     socket.send('Hello from client!');
    //     console.log('Message envoyé : Hello from client!');
    // } else {
    //     console.log('Connexion WebSocket n\'est pas encore ouverte');
    // }
}
