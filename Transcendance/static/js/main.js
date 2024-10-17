let currentGameId = null;
let socket = null;
let gameLoopInterval = null;
let isLocalGame = false;
let gameModal = null;
let gameState = {};
let keyState = { w: false, s: false, ArrowUp: false, ArrowDown: false, t: false, g: false, i: false, k: false };

document.addEventListener('DOMContentLoaded', function() {
    gameModal = new bootstrap.Modal(document.getElementById('gameModal'));

    document.getElementById('gameModal').addEventListener('hidden.bs.modal', function () {
        terminateGame();
        navigateTo('Home', '/', 'The game has been terminated.');
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

        isLocalGame = !remote;

        if (remote && nbPlayers === 2) {
            fetchAvailableGames();
        } else {
            createNewGame(remote, nbPlayers);
        }
    });

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

    initializeLanguageSelector();

    function fetchAvailableGames() {
        fetch('/api/play/list')
            .then(response => response.json())
            .then(games => {
                if (games.length > 0) {
                    displayAvailableGames(games);
                } else {
                    createNewGame(true, 2);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                createNewGame(true, 2);
            });
    }

    function displayAvailableGames(games) {
        let container = document.querySelector('.main-content');
        if (!container) {
            container = document.createElement('div');
            container.className = 'main-content';
            document.body.insertBefore(container, document.getElementById('gameModal'));
        }

        container.innerHTML = '';

        const title = document.createElement('h1');
        title.textContent = 'Available Games';
        container.appendChild(title);

        if (games.length > 0) {
            const gameList = document.createElement('ul');
            games.forEach(game => {
                const listItem = document.createElement('li');
                listItem.textContent = `Game ${game.id} (${game.player_connected}/${game.nb_players} players)`;
                listItem.addEventListener('click', () => joinGame(game.id));
                gameList.appendChild(listItem);
            });
            container.appendChild(gameList);
        } else {
            const noGamesMessage = document.createElement('p');
            noGamesMessage.textContent = 'No available games found.';
            container.appendChild(noGamesMessage);
        }

        const newGameButton = document.createElement('button');
        newGameButton.textContent = 'Create New Game';
        newGameButton.addEventListener('click', () => createNewGame(true, 2));
        container.appendChild(newGameButton);

        const playForm = document.getElementById('playForm');
        if (playForm) {
            playForm.style.display = 'none';
        }
    }

    function joinGame(gameId) {
        const newUrl = `/game/${gameId}`;
        const newTitle = `Pong Game ${gameId}`;
        const newContent = `Playing Pong Game ${gameId}`;
        navigateTo(newTitle, newUrl, newContent, gameId);
        initializeGame(gameId, 2);
    }

    function createNewGame(remote, nbPlayers) {
        const data = {
            remote: remote,
            nb_players: nbPlayers
        };

        return fetchWithCsrf(`api/play/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(data),
            credentials: 'include'
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            const gameId = result.id;
            const newUrl = `/game/${gameId}`;
            const newTitle = `Pong Game ${gameId}`;
            const newContent = `Playing Pong Game ${gameId}`;
            navigateTo(newTitle, newUrl, newContent, gameId);
            initializeGame(gameId, nbPlayers);
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message);
        });
    }

    function updateUI(state) {
        const mainContent = document.querySelector('.main-content');
        const playForm = document.getElementById('playForm');

        if (state.gameId) {
            playForm.classList.add('d-none');
            gameModal.show();
            currentGameId = state.gameId;
        } else {
            gameModal.hide();
            playForm.classList.remove('d-none');
            terminateGame();
        }

        if (mainContent) {
            mainContent.innerHTML = `<h1>${state.title}</h1><p>${state.content}</p>`;
        }

        document.title = state.title;
    }

    function navigateTo(title, url, content, gameId = null) {
        const state = { title, content, gameId };
        history.pushState(state, title, url);
        updateUI(state);
    }

    function terminateGame() {
        if (socket) {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ 'action': 'disconnect', 'player': 'all' }));
            }
            console.log("JAFGOIAGIOEGOBQEGBOENGPE");
            socket.close();
            socket = null;
        }
        if (gameLoopInterval) {
            clearInterval(gameLoopInterval);
            gameLoopInterval = null;
        }
        currentGameId = null;
        isLocalGame = false;

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    function initializeGame(gameId, nbPlayers) {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.message === 'end_game') {
                fetchGameDetails(currentGameId);
            } else {
                gameState = data;
                draw(ctx);
            }
        };

        socket.onclose = function(e) {
            console.error('WebSocket closed unexpectedly');
            terminateGame();
        };

        gameLoopInterval = setInterval(updatePaddlePositions, 1000 / 60);
    }

    function draw(ctx) {
        const canvas = ctx.canvas;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'white';

        const paddleWidth = 10, paddleHeight = 100, ballSize = 10;

        if (gameState.ball) {
            ctx.beginPath();
            ctx.arc(gameState.ball[0], gameState.ball[1], ballSize, 0, Math.PI * 2);
            ctx.fill();
        }

        for (let i = 1; i <= 4; i++) {
            const player = gameState[`player_${i}`];
            if (player) {
                ctx.fillRect(player[0], player[1], paddleWidth, paddleHeight);
            }
        }

        ctx.font = '48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${gameState.score_team_1} - ${gameState.score_team_2}`, canvas.width / 2, 50);
    }

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

    function sendPaddleMovement(player, direction) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ 'player': player, 'move': direction }));
        }
    }

    function fetchGameDetails(gameId) {
        fetch(`/api/play/detail/${gameId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Affichage du retour API', data);
                endGame(data);
            })
            .catch(error => {
                endGame({
                    is_finished: true,
                    nb_players: gameState.player_2 ? 2 : 4,
                    results: null
                });
            });
    }

    function endGame(gameDetails) {
        let message;
        const language = localStorage.getItem('language') || 'fr';

        if (gameDetails && gameDetails.is_finished) {
            if (gameDetails.nb_players === 2) {
                let player1Score = gameDetails.results ? gameDetails.results.score.player1 : gameState.score_team_1;
                let player2Score = gameDetails.results ? gameDetails.results.score.player2 : gameState.score_team_2;
                message = player1Score > player2Score
                    ? translations[language].player1Wins
                    : translations[language].player2Wins;
            } else if (gameDetails.nb_players === 4) {
                let team1Score = gameDetails.results
                    ? (gameDetails.results.score.player1 || 0) + (gameDetails.results.score.player3 || 0)
                    : gameState.score_team_1;
                let team2Score = gameDetails.results
                    ? (gameDetails.results.score.player2 || 0) + (gameDetails.results.score.player4 || 0)
                    : gameState.score_team_2;
                message = team1Score > team2Score
                    ? translations[language].team1Wins
                    : translations[language].team2Wins;
            }
        } else {
            message = translations[language].gameEndedUnexpectedly || 'Game ended unexpectedly';
        }

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = 'white';
        ctx.font = '36px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(message, canvas.width / 2, canvas.height / 2);

        clearInterval(gameLoopInterval);

        setTimeout(() => {
            gameModal.hide();
            const playForm = document.getElementById('playForm');
            playForm.classList.remove('d-none');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            navigateTo('Home', '/', 'The game has been terminated.');
        }, 2000);
    }

    function initializeLanguageSelector() {
        const languageSelector = document.getElementById('language');
        if (languageSelector) {
            languageSelector.addEventListener('change', function() {
                const selectedLanguage = this.value;
                localStorage.setItem('language', selectedLanguage);
                location.reload();
            });

            const currentLanguage = localStorage.getItem('language') || 'fr';
            languageSelector.value = currentLanguage;
        }
    }

    window.addEventListener('popstate', (e) => {
        if (isLocalGame) {
            e.preventDefault();
            terminateGame();
            navigateTo('Home', '/', 'The local game has been terminated.');
            return;
        }

        if (e.state) {
            updateUI(e.state);
        } else {
            updateUI({ title: 'Home', content: 'Welcome to the home page' });
        }
    });

    history.replaceState({ title: 'Home', content: 'Welcome to the home page' }, 'Home', '/');
    updateUI({ title: 'Home', content: 'Welcome to the home page' });
});
