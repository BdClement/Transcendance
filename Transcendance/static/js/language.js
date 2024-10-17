const translations = {
    en: {
        play: "Play",
        local_1v1: "Local 1v1",
        local_2v2: "Local 2v2",
        remote_1v1: "Remote 1v1",
        language: "Language",
        player1Wins: "Player 1 Wins!",
        player2Wins: "Player 2 Wins!",
        team1Wins: "Team 1 Wins!",
        team2Wins: "Team 2 Wins!",
        gameEndedUnexpectedly: "The game ended unexpectedly.",
        gameEnded: "The game has ended.",
        gameTerminated: "The game has been terminated by the server.",
        logout: "Logout",
        authButton: "Sign Up/Login",
        authModalTitle: "Authentication",
        loginTab: "Login",
        signupTab: "Sign Up",
        username: "Username",
        email: "Email",
        password: "Password",
        profilePhoto: "Profile Photo",
        loginButton: "Log In",
        signupButton: "Sign Up"
    },
    fr: {
        play: "Jouer",
        local_1v1: "Local 1c1",
        local_2v2: "Local 2c2",
        remote_1v1: "Distant 1c1",
        language: "Langue",
        player1Wins: "Joueur 1 gagne !",
        player2Wins: "Joueur 2 gagne !",
        team1Wins: "L'équipe 1 gagne !",
        team2Wins: "L'équipe 2 gagne !",
        gameEndedUnexpectedly: "La partie s'est terminée de manière inattendue.",
        gameEnded: "La partie est terminée.",
        gameTerminated: "La partie a été interrompue par le serveur.",
        logout: "Déconnexion",
        authButton: "S'inscrire/Connexion",
        authModalTitle: "Authentification",
        loginTab: "Connexion",
        signupTab: "Inscription",
        username: "Nom d'utilisateur",
        email: "Email",
        password: "Mot de passe",
        profilePhoto: "Photo de profil",
        loginButton: "Se connecter",
        signupButton: "S'inscrire"
    },
    viet: {
        play: "Chơi",
        local_1v1: "ở gần 1t1",
        local_2v2: "ở gần 2t2",
        remote_1v1: "Khoảng 1t1",
        language: "Ngôn ngữ",
        player1Wins: "Người chơi 1 thắng!",
        player2Wins: "Người chơi 2 thắng!",
        team1Wins: "Đội 1 thắng!",
        team2Wins: "Đội 2 thắng!",
        gameEndedUnexpectedly: "Trò chơi kết thúc bất ngờ.",
        gameEnded: "Trò chơi đã kết thúc.",
        gameTerminated: "Trò chơi đã bị máy chủ chấm dứt.",
        logout: "Đăng xuất",
        authButton: "Đăng ký/Đăng nhập",
        authModalTitle: "Xác thực",
        loginTab: "Đăng nhập",
        signupTab: "Đăng ký",
        username: "Tên người dùng",
        email: "Email",
        password: "Mật khẩu",
        profilePhoto: "Ảnh hồ sơ",
        loginButton: "Đăng nhập",
        signupButton: "Đăng ký"
    }
};

function applyTranslations(language) {
    document.querySelector('button[type="submit"] .gradient-text').textContent = translations[language].play;
    document.querySelector('label[for="local_1v1"] .gradient-text').textContent = translations[language].local_1v1;
    document.querySelector('label[for="local_2v2"] .gradient-text').textContent = translations[language].local_2v2;
    document.querySelector('label[for="remote_1v1"] .gradient-text').textContent = translations[language].remote_1v1;
    
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.textContent = translations[language].logout;
    }

    const authButton = document.querySelector('.auth-button');
    if (authButton) {
        authButton.textContent = translations[language].authButton;
    }

    const authModal = document.getElementById('authModal');
    if (authModal) {
        authModal.querySelector('.modal-title').textContent = translations[language].authModalTitle;
        authModal.querySelector('#login-tab').textContent = translations[language].loginTab;
        authModal.querySelector('#signup-tab').textContent = translations[language].signupTab;

        const loginForm = authModal.querySelector('#loginForm');
        if (loginForm) {
            loginForm.querySelector('label[for="loginUsername"]').textContent = translations[language].username;
            loginForm.querySelector('label[for="loginPassword"]').textContent = translations[language].password;
            loginForm.querySelector('button[type="submit"]').textContent = translations[language].loginButton;
        }

        const signupForm = authModal.querySelector('#signupForm');
        if (signupForm) {
            signupForm.querySelector('label[for="signupUsername"]').textContent = translations[language].username;
            signupForm.querySelector('label[for="signupEmail"]').textContent = translations[language].email;
            signupForm.querySelector('label[for="signupPassword"]').textContent = translations[language].password;
            signupForm.querySelector('label[for="profilePhoto"]').textContent = translations[language].profilePhoto;
            signupForm.querySelector('button[type="submit"]').textContent = translations[language].signupButton;
        }
    }
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
