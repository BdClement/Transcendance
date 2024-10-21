const tournamentModal = document.getElementById('tournamentModal');
const tournamentForm = document.getElementById('tournamentForm');
const playerCountSelect = document.getElementById('playerCount');
const aliasInputs = document.getElementById('aliasInputs');
const tournamentLink = document.getElementById('tournamentLink');

function openTournamentModal() {
    const modal = new bootstrap.Modal(tournamentModal);
    modal.show();
}

tournamentLink.addEventListener('click', (e) => {
    e.preventDefault();
    history.pushState(null, '', '/tournaments');
    openTournamentModal();
});

window.addEventListener('popstate', (event) => {
    if (window.location.pathname === '/tournaments') {
        openTournamentModal();
    } else {
        const modal = bootstrap.Modal.getInstance(tournamentModal);
        if (modal) {
            modal.hide();
        }
    }
});

tournamentModal.addEventListener('hidden.bs.modal', () => {
    if (window.location.pathname === '/tournaments') {
        history.pushState(null, '', '/');
    }
});

playerCountSelect.addEventListener('change', updateAliasInputs);

function updateAliasInputs() {
    const playerCount = parseInt(playerCountSelect.value);
    aliasInputs.innerHTML = '';

    for (let i = 1; i <= playerCount; i++) {
        const input = document.createElement('div');
        input.classList.add('mb-3');
        input.innerHTML = `
            <p for="alias${i}" class="form-label" data-i18n="playerAlias">Alias du joueur ${i}</p>
            <input type="text" class="form-control" id="alias${i}" required>
        `;
        aliasInputs.appendChild(input);
    }
}

tournamentForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const playerCount = parseInt(playerCountSelect.value);
    const aliasNames = [];

    for (let i = 1; i <= playerCount; i++) {
        const aliasInput = document.getElementById(`alias${i}`);
        if (aliasInput && aliasInput.value.trim() !== '') {
            aliasNames.push(aliasInput.value.trim());
        }
    }

    if (aliasNames.length !== playerCount) {
        alert(`Veuillez entrer ${playerCount} alias valides.`);
        return;
    }

    try {
        const response = await fetchWithCsrf('/api/tournaments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                nb_players: playerCount,
                alias_names: aliasNames,
            }),
        });

        if (response.status === 201) {
            const tournamentData = await response.json();
            bootstrap.Modal.getInstance(tournamentModal).hide();
            startTournament(tournamentData.id);
        } else {
            const errorData = await response.json();
            alert(`Erreur : ${errorData.message}`);
        }
    } catch (error) {
        console.error('Erreur lors de la création du tournoi:', error);
        alert('Une erreur est survenue lors de la création du tournoi.');
    }
});

async function startTournament(tournamentId) {
    let tournamentFinished = false;

    while (!tournamentFinished) {
        try {
            const response = await fetch(`/api/tournaments/${tournamentId}/next-play/`);
            const data = await response.json();

            if (response.status === 200) {
                console.log('Lancer la partie:', data.play_id);
                console.log('Joueurs:', data.players);
                const newUrl = `/game/${data.play_id}`;
                const newTitle = `Pong Game ${data.play_id}`;
                const newContent = `Playing Pong Game ${data.play_id}`;
                PongGame.navigateTo(newTitle, newUrl, newContent, data.play_id);
                PongGame.initializeGame(data.play_id, 2);
                await waitForGameCompletion(data.play_id);
            } else if (response.status === 410) {
                tournamentFinished = true;
                await displayTournamentResults(tournamentId);
            } else {
                throw new Error('Erreur inattendue');
            }
        } catch (error) {
            console.error('Erreur lors du déroulement du tournoi:', error);
            alert('Une erreur est survenue lors du déroulement du tournoi.');
            tournamentFinished = true;
        }
    }
}

function waitForGameCompletion(playId) {
    return new Promise((resolve) => {
        const checkInterval = setInterval(() => {
            PongGame.fetchGameDetails(playId)
                .then(gameDetails => {
                    if (gameDetails.is_finished) {
                        clearInterval(checkInterval);
                        resolve();
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la vérification de l\'état du jeu:', error);
                    clearInterval(checkInterval);
                    resolve();
                });
        }, 15000); // verifie toutes les 15 secondes pour etre sur que la websocket de la partie precedente est close
    });
}

PongGame.fetchGameDetails = function(gameId) {
    return fetch(`/api/play/detail/${gameId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
};

async function displayTournamentResults(tournamentId) {
    try {
        const response = await fetch(`/api/tournaments/${tournamentId}/`);
        const data = await response.json();

        if (response.status === 200) {
            console.log('Résultats du tournoi:', data);
        } else {
            throw new Error('Erreur inattendue');
        }
    } catch (error) {
        console.error('Erreur lors de l\'affichage des résultats du tournoi:', error);
        alert('Une erreur est survenue lors de l\'affichage des résultats du tournoi.');
    }
}

updateAliasInputs();

if (window.location.pathname === '/tournaments') {
    openTournamentModal();
}
