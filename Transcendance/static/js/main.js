// document.addEventListener('DOMContentLoaded', function() {
//     const canvas = document.getElementById('gameCanvas');
//     const playForm = document.getElementById('playForm');

//     // S'assurer que le canvas est caché et que le formulaire est visible au chargement
//     canvas.classList.add('hidden');
//     canvas.classList.remove('visible');
//     playForm.classList.add('visible');
//     playForm.classList.remove('hidden');
// });

function updateUI(state) {
    // Ici, vous mettrez la logique pour mettre à jour votre UI
    // en fonction de l'état actuel
    console.log('Updating UI with state:', state);

    // Exemple : mise à jour du contenu principal
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.innerHTML = `<h1>${state.title}</h1><p>${state.content}</p>`;
    }

    // Mise à jour du titre de la page
    document.title = state.title;
}

// Fonction pour naviguer vers une nouvelle "page"
function navigateTo(title, url, content) {
    const state = { title, content };
    history.pushState(state, title, url);
    updateUI(state);
}

// Écouteur d'événements pour les clics sur les liens
document.addEventListener('click', (e) => {
    if (e.target.tagName === 'A') {
        e.preventDefault();
        const url = e.target.href;
        const title = e.target.textContent;
        const content = `Content for ${title}`; // Simulé, à remplacer par du vrai contenu
        navigateTo(title, url, content);
    }
});

// Écouteur pour l'événement popstate (navigation avant/arrière)
window.addEventListener('popstate', (e) => {
    if (e.state) {
        updateUI(e.state);
    } else {
        // Gérer le cas où il n'y a pas d'état (par exemple, la page initiale)
        updateUI({ title: 'Home', content: 'Welcome to the home page' });
    }
});

// Initialisation de l'état initial
history.replaceState({ title: 'Home', content: 'Welcome to the home page' }, 'Home', '/');
updateUI({ title: 'Home', content: 'Welcome to the home page' });

document.getElementById('playForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const gameMode = document.querySelector('input[name="game_mode"]:checked').value;
    let remote, nbPlayers;

    switch (gameMode) {
        case 'remote_1v1':
            remote = true;
            nbPlayers = 2;
            break;
        case 'remote_2v2':
            remote = true;
            nbPlayers = 4;
            break;
        case 'local_1v1':
            remote = false;
            nbPlayers = 2;
            break;
        case 'local_2v2':
            remote = false;
            nbPlayers = 4;
            break;
    }

    const data = {
        remote: remote,
        nb_players: nbPlayers
    };

    fetch(`api/play/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        const gameId = result.id;
        const newUrl = `/game/${gameId}`;
        const newTitle = `Pong Game ${gameId}`;
        const newContent = `Playing Pong Game ${gameId}`;
        navigateTo(newTitle, newUrl, newContent);
        const canvas = document.getElementById('gameCanvas');
        const playForm = document.getElementById('playForm');

        // Hide the form and show the canvas
        playForm.classList.remove('visible');
        playForm.classList.add('hidden');
        canvas.classList.remove('hidden');
        canvas.classList.add('visible');

        const ctx = canvas.getContext('2d');
        const paddleWidth = 10, paddleHeight = 100, ballSize = 10;

        let gameState = {};
        let keyState = { w: false, s: false, ArrowUp: false, ArrowDown: false, t: false, g: false, i: false, k: false };
        let gameLoopInterval;

        socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

        socket.onmessage = function(e) {
            gameState = JSON.parse(e.data);
            console.log('Received data:', gameState);
            draw();
        };

        socket.onclose = function(e) {
            console.error('WebSocket closed unexpectedly');
            clearInterval(gameLoopInterval);
        };

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = 'white';

            if (gameState.ball) {
                ctx.beginPath();
                ctx.arc(gameState.ball[0], gameState.ball[1], ballSize, 0, Math.PI * 2);
                ctx.fill();
            }

            for (let i = 1; i <= nbPlayers; i++) {
                const player = gameState[`player_${i}`];
                if (player) {
                    ctx.fillRect(player[0], player[1], paddleWidth, paddleHeight);
                }
            }

            ctx.font = '48px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`${gameState.score_team_1} - ${gameState.score_team_2}`, canvas.width / 2, 50);

            if (gameState.score_team_1 === 3 || gameState.score_team_2 === 3) {
                endGame(gameState.score_team_1 > gameState.score_team_2 ? 1 : 2);
            }
        }

        function endGame(winningTeam) {
            const language = localStorage.getItem('language') || 'fr';
            let message;
            if (nbPlayers === 2) {
                message = winningTeam === 1 ? translations[language].player1Wins : translations[language].player2Wins;
            } else {
                message = winningTeam === 1 ? translations[language].team1Wins : translations[language].team2Wins;
            }

            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = 'white';
            ctx.font = '36px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(message, canvas.width / 2, canvas.height / 2);

            clearInterval(gameLoopInterval);

            setTimeout(() => {
                // Hide the canvas and show the form
                canvas.classList.remove('visible');
                canvas.classList.add('hidden');
                playForm.classList.remove('hidden');
                playForm.classList.add('visible');

                // Clear the canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = 'black';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }, 2000);
        }

        function sendPaddleMovement(player, direction) {
            socket.send(JSON.stringify({ 'player': player, 'move': direction }));
        }

        document.addEventListener('keydown', function(event) {
            if (event.key in keyState) {
                keyState[event.key] = true;
            }
        });

        document.addEventListener('keyup', function(event) {
            if (event.key in keyState) {
                keyState[event.key] = false;
            }
        });

        function updatePaddlePositions() {
            if (keyState.w) sendPaddleMovement(1, 'up');
            if (keyState.s) sendPaddleMovement(1, 'down');
            if (keyState.t) sendPaddleMovement(3, 'up');
            if (keyState.g) sendPaddleMovement(3, 'down');
            if (keyState.i) sendPaddleMovement(4, 'up');
            if (keyState.k) sendPaddleMovement(4, 'down');
            if (keyState.ArrowUp) sendPaddleMovement(2, 'up');
            if (keyState.ArrowDown) sendPaddleMovement(2, 'down');
        }

        gameLoopInterval = setInterval(updatePaddlePositions, 1000 / 60);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
