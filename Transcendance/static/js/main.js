// // Fonction pour obtenir l'URL actuelle sans le domaine
// // function getCurrentPath() {
// //     return window.location.pathname.substring(1); // Supprimer le '/' initial
// // }

// function getCurrentPath() {
//     let path = window.location.pathname.substring(1); // Supprimer le '/' initial
//     return path.endsWith('/') ? path.slice(0, -1) : path; // Enlever le '/' final si présent
// }

// // Fonction pour afficher le contenu basé sur l'URL
// function displayContent() {
//     const path = getCurrentPath();
//     const appElement = document.getElementById('app');

//     if (path === 'home') {
//         appElement.innerHTML = `
//         <h1>Welcome on Transcendance</h1>
//         <button onclick="navigate(event, 'home/play')">Jouer</button>
//         <button onclick="testWebSocket()">Test WebSocket</button>
//     `;
//     }else if (path === 'home/play'){
//         appElement.innerHTML = `
//         <h1>Let's Play!</h1>
//         <p>This is the play page content.</p>
//     `;
//     } else {
// 		appElement.innerHTML = '<p>Page not found</p>';
// 		// appElement.innerHTML = path;
//     }
// }

// // Fonction pour gérer la navigation
// function navigate(event, path) {
//     event.preventDefault(); // Empêche le rechargement de la page
//     history.pushState({}, '', `/${path}`); // Met à jour l'URL sans recharger
//     displayContent(); // Affiche le contenu correspondant à la nouvelle URL
// }

// // Gérer la navigation avec le bouton "Retour" du navigateur
// window.addEventListener('popstate', displayContent);

// // Exécuter la fonction displayContent lorsque le DOM est complètement chargé
// document.addEventListener('DOMContentLoaded', displayContent);


// Fonction pour obtenir l'URL actuelle sans le domaine
// function getCurrentPath() {
//     return window.location.pathname.substring(1); // Supprimer le '/' initial
// }

// Fonction pour obtenir l'URL actuelle sans le domaine
// function getCurrentPath() {
//     return window.location.pathname.substring(1); // Supprimer le '/' initial
// }

const translations = {
    en: {
        play: "Play",
        local_1v1: "Local 1v1",
        local_2v2: "Local 2v2",
        remote_1v1: "Remote 1v1",
        remote_2v2: "Remote 2v2",
        language: "Language",
        player1Wins: "Player 1 Wins!",
        player2Wins: "Player 2 Wins!",
        team1Wins: "Team 1 Wins!",
        team2Wins: "Team 2 Wins!"
    },
    fr: {
        play: "Jouer",
        local_1v1: "Local 1c1",
        local_2v2: "Local 2c2",
        remote_1v1: "Distant 1c1",
        remote_2v2: "Distant 2c2",
        language: "Langue",
        player1Wins: "Joueur 1 gagne !",
        player2Wins: "Joueur 2 gagne !",
        team1Wins: "L'équipe 1 gagne !",
        team2Wins: "L'équipe 2 gagne !"
    },
    viet: {
        play: "Chơi",
        local_1v1: "ở gần 1t1",
        local_2v2: "ở gần 2t2",
        remote_1v1: "Khoảng 1t1",
        remote_2v2: "Khoảng 2t2",
        language: "Ngôn ngữ",
        player1Wins: "Người chơi 1 thắng!",
        player2Wins: "Người chơi 2 thắng!",
        team1Wins: "Đội 1 thắng!",
        team2Wins: "Đội 2 thắng!"
    }
};

function applyTranslations(language) {
    document.querySelector('button .gradient-text').textContent = translations[language].play;
    document.querySelector('label[for="local_1v1"] .gradient-text').textContent = translations[language].local_1v1;
    document.querySelector('label[for="local_2v2"] .gradient-text').textContent = translations[language].local_2v2;
    document.querySelector('label[for="remote_1v1"] .gradient-text').textContent = translations[language].remote_1v1;
    document.querySelector('label[for="remote_2v2"] .gradient-text').textContent = translations[language].remote_2v2;
}

function changeLanguage(language) {
    applyTranslations(language);
    localStorage.setItem('language', language);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedLanguage = localStorage.getItem('language') || 'fr';
    document.getElementById('language').value = savedLanguage;
    applyTranslations(savedLanguage);
});

document.getElementById('language').addEventListener('change', function() {
    const selectedLanguage = this.value;
    changeLanguage(selectedLanguage);
});

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
        const canvas = document.getElementById('gameCanvas');
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
