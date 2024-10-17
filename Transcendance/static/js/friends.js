document.addEventListener('DOMContentLoaded', () => {
    const followingList = document.getElementById('followingList');
    const followersList = document.getElementById('followersList');
    const addFriendForm = document.getElementById('addFriendForm');
    const friendProfileModal = new bootstrap.Modal(document.getElementById('friendProfileModal'));
    const unfollowButton = document.getElementById('unfollowButton');

    // Charger la liste des amis
    function loadFriendLists() {
        fetch('/api/following/')
            .then(response => response.json())
            .then(data => {
                followingList.innerHTML = data.map(user => `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        ${user.username}
                        <button class="btn btn-sm btn-info view-profile" data-user-id="${user.id}">Voir profil</button>
                    </li>
                `).join('');
            });

        fetch('/api/followers/')
            .then(response => response.json())
            .then(data => {
                followersList.innerHTML = data.map(user => `
                    <li class="list-group-item">
                        ${user.username}
                    </li>
                `).join('');
            });
    }

    // Ajouter un ami
    addFriendForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const friendUsername = document.getElementById('friendUsername').value;
        fetch(`/api/users/${friendUsername}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Utilisateur non trouvé');
                }
                return response.json();
            })
            .then(data => {
                if (!data.id) {
                    throw new Error('ID de l\'utilisateur non trouvé');
                }
                return fetch(`/api/addfriend/${data.id}/`, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors de l\'ajout de l\'ami');
                }
                return response.json();
            })
            .then(data => {
                alert(data.detail || 'Ami ajouté avec succès');
                loadFriendLists();
            })
            .catch(error => {
                alert(error.message);
            });
    });

    // Voir le profil d'un ami
    followingList.addEventListener('click', (e) => {
        if (e.target.classList.contains('view-profile')) {
            const userId = e.target.dataset.userId;
            fetch(`/api/user_profile/${userId}/`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('friendProfileContent').innerHTML = `
                        <p><strong>Nom d'utilisateur:</strong> ${data.username}</p>
                        <p><strong>Alias:</strong> ${data.alias}</p>
                        <p><strong>Parties jouées:</strong> ${data.nbPartiesJouees}</p>
                        <p><strong>Victoires:</strong> ${data.nbVictoires}</p>
                        <p><strong>Défaites:</strong> ${data.nbDefaites}</p>
                    `;
                    unfollowButton.dataset.userId = userId;
                    friendProfileModal.show();
                });
        }
    });

    // Se désabonner d'un ami
    unfollowButton.addEventListener('click', () => {
        const userId = unfollowButton.dataset.userId;
        fetch(`/api/unfollow/${userId}/`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                alert(data.detail);
                friendProfileModal.hide();
                loadFriendLists();
            })
            .catch(error => {
                alert("Erreur lors du désabonnement");
            });
    });

    // Charger la liste des amis au chargement de la page
    loadFriendLists();

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});