// function updateUserInfo(username, photoProfile) {
//     const userInfoElement = document.getElementById('userInfo');
//     const profilePictureElement = document.getElementById('profilePicture');
//     if (username) {
//         const usernameDisplay = document.createElement('div');
//         usernameDisplay.id = 'usernameDisplay';
//         usernameDisplay.textContent = username;

//         // Insérer cet élément après la photo de profil
//         profilePictureElement.parentNode.insertBefore(usernameDisplay, profilePictureElement.nextSibling);

//         document.getElementById('logoutButton').style.display = 'block';
//         document.querySelector('.auth-button').style.display = 'none';
//         if (photoProfile) {
//             profilePictureElement.style.backgroundImage = `url(/static/images/${username}.jpg)`;
//         } else {
//             profilePictureElement.style.backgroundImage = 'url(/static/images/base_pfp.png)';
//         }
//     } else {
//         const usernameDisplay = document.getElementById('usernameDisplay');
//         if (usernameDisplay) {
//             usernameDisplay.remove();
//         }

//         document.getElementById('logoutButton').style.display = 'none';
//         document.querySelector('.auth-button').style.display = 'block';
//         profilePictureElement.style.backgroundImage = 'url(/static/images/base_pfp.png)';
//     }

//     // Masquer l'ancien élément userInfo dans la navbar
//     userInfoElement.style.display = 'none';
// }

// function checkLoginStatus() {
//     fetch('/api/user/', {
//         method: 'GET',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         credentials: 'include'
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.username) {
//             updateUserInfo(data.username, data.photoProfile, data.alias);
//         } else {
//             updateUserInfo(null);
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         updateUserInfo(null);
//     });
// }

// document.addEventListener('DOMContentLoaded', function() {
//     checkLoginStatus();
//     const loginForm = document.getElementById('loginForm');
//     const signupForm = document.getElementById('signupForm');

//     loginForm.addEventListener('submit', function(e) {
//         e.preventDefault();
//         const alias = document.getElementById('loginAlias').value;
//         const username = document.getElementById('loginUsername').value;
//         const password = document.getElementById('loginPassword').value;

//         fetch('/api/login/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ username, alias, password }),
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.message === "Connexion réussie") {
//                 // alert('Connexion réussie');
//                 const authModal = bootstrap.Modal.getInstance(document.getElementById('authModal'));
//                 authModal.hide();
//                 updateUserInfo(data.user.username, data.user.photoProfile, data.user.alias);
//                 // window.location.reload();
//             } else {
//                 alert('Erreur de connexion: ' + data.message);
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             alert('Erreur de connexion');
//         });
//     });

//     signupForm.addEventListener('submit', function(e) {
//         e.preventDefault();
//         const username = document.getElementById('signupUsername').value;
//         const alias = document.getElementById('signupAlias').value;
//         const email = document.getElementById('signupEmail').value;
//         const password = document.getElementById('signupPassword').value;
//         const photoProfile = document.getElementById('profilePhoto').files[0];

//         const formData = new FormData();
//         const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
//         formData.append('csrfmiddlewaretoken', csrftoken);
//         formData.append('username', username);
//         formData.append('alias', alias);
//         formData.append('email', email);
//         formData.append('password', password);
//         if (photoProfile) {
//             formData.append('photoProfile', photoProfile);
//         }

//         fetch('/api/signup/', {
//             method: 'POST',
//             body: formData,
//             headers: {
//                 'X-CSRFToken': getCsrfToken(),
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.message === "Inscription réussie") {
//                 alert('Inscription réussie');
//                 const authModal = bootstrap.Modal.getInstance(document.getElementById('authModal'));
//                 authModal.hide();
//                 updateUserInfo(data.user.username, data.user.photoProfile, data.user.alias);
//             } else {
//                 alert('Erreur d\'inscription: ' + data.message);
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             alert('Erreur d\'inscription');
//         });
//     });

//     logoutButton.addEventListener('click', function() {
//         fetch('/api/logout/', {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.message === "Déconnexion réussie") {
//                 // alert('Déconnexion réussie');
//                 updateUserInfo(null);
//                 // window.location.reload();
//             } else {
//                 alert('Erreur de déconnexion: ' + data.message);
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             alert('Erreur de déconnexion');
//         });
//     });
// });


function updateCsrfToken() {
    return fetch('/api/get-csrf-token/', {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('[name=csrfmiddlewaretoken]').value = data.csrfToken;
    });
}

//requête avec le token CSRF à jour
function fetchWithCsrf(url, options = {}) {
    return updateCsrfToken()
        .then(() => {
            options.headers = options.headers || {};
            options.headers['X-CSRFToken'] = getCsrfToken();
            options.credentials = 'include';
            return fetch(url, options);
        });
}

function updateUserInfo(username, photoProfile) {
    const userInfoElement = document.getElementById('userInfo');
    const profilePictureElement = document.getElementById('profilePicture');
    if (username) {
        const usernameDisplay = document.createElement('div');
        usernameDisplay.id = 'usernameDisplay';
        usernameDisplay.textContent = username;

        profilePictureElement.parentNode.insertBefore(usernameDisplay, profilePictureElement.nextSibling);

        document.getElementById('logoutButton').style.display = 'block';
        document.querySelector('.auth-button').style.display = 'none';
        if (photoProfile) {
            profilePictureElement.style.backgroundImage = `url(/static/images/${username}.jpg)`;
        } else {
            profilePictureElement.style.backgroundImage = 'url(/static/images/base_pfp.png)';
        }
    } else {
        const usernameDisplay = document.getElementById('usernameDisplay');
        if (usernameDisplay) {
            usernameDisplay.remove();
        }

        document.getElementById('logoutButton').style.display = 'none';
        document.querySelector('.auth-button').style.display = 'block';
        profilePictureElement.style.backgroundImage = 'url(/static/images/base_pfp.png)';
    }

    userInfoElement.style.display = 'none';
}

function checkLoginStatus() {
    return fetchWithCsrf('/api/user/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.username) {
            updateUserInfo(data.username, data.photoProfile, data.alias);
        } else {
            updateUserInfo(null);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        updateUserInfo(null);
    });
}

function login(username, password) {
    return fetchWithCsrf('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Connexion réussie") {
            updateUserInfo(data.user.username, data.user.photoProfile);
            return data.user;
        } else {
            throw new Error(data.message);
        }
    });
}

function signup(formData) {
    return fetchWithCsrf('/api/signup/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Inscription réussie") {
            updateUserInfo(data.user.username, data.user.photoProfile, data.user.alias);
            return data.user;
        } else {
            throw new Error(data.message);
        }
    });
}

function logout() {
    return fetchWithCsrf('/api/logout/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Déconnexion réussie") {
            updateUserInfo(null);
        } else {
            throw new Error(data.message);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const logoutButton = document.getElementById('logoutButton');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        login(username, password)
            .then(() => {
                const authModal = bootstrap.Modal.getInstance(document.getElementById('authModal'));
                authModal.hide();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion: ' + error.message);
            });
    });

    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        signup(formData)
            .then(() => {
                alert('Inscription réussie');
                const authModal = bootstrap.Modal.getInstance(document.getElementById('authModal'));
                authModal.hide();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur d\'inscription: ' + error.message);
            });
    });

    logoutButton.addEventListener('click', function() {
        logout()
            .then(() => {
                // Pas besoin d'alerte ici, updateUserInfo gère déjà l'UI
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de déconnexion: ' + error.message);
            });
    });
});
