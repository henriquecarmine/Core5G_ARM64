// ============================================================================
// i18n do painel — dicionários pt/en/es/fr + helper.
// Fase F1: login + topbar. (F2: index completo · F3: topologia · F4: scripts)
//
// Regras:
// - pt é o idioma CANÔNICO; fallback de chave: <lang> → en → pt → a própria chave.
// - Termos 3GPP/O-RAN (AMF, CUPS, slice, E2SM-KPM, PDU Session…) NÃO se
//   traduzem — traduz-se a explicação, nunca o termo (decisão didática).
// - Toda chave nova PRECISA existir nos 4 idiomas (test/i18n-parity.js falha
//   se faltar).
// - Uso: data-i18n / data-i18n-title / data-i18n-ph no HTML; I18N.t(chave,
//   {params}) no JS; I18N.set(lang) troca e persiste (localStorage c5g-lang).
// ============================================================================
const I18N_DICTS = {
  pt: {
    'ui.lang_title': 'Idioma',
    'ui.theme_to_light': 'Mudar para o tema claro',
    'ui.theme_to_dark': 'Mudar para o tema escuro',
    'login.subtitle': 'Painel de controle do laboratório 5G',
    'login.user': 'Usuário',
    'login.pass': 'Senha',
    'login.enter': 'Entrar',
    'login.or_student': 'ou entre como aluno',
    'login.guest_hint': 'Acompanhe a aula ao vivo (somente leitura). Informe seu nome e e-mail para entrar — é o registro de presença da turma.',
    'login.ph_name': 'Seu nome completo',
    'login.ph_email': 'Seu e-mail',
    'login.enter_student': 'Entrar como aluno (acompanhar ao vivo)',
    'login.err_invalid': 'Usuário ou senha inválidos.',
    'login.err_conn': 'Falha de conexão. Tente novamente.',
    'login.err_name': 'Informe seu nome completo.',
    'login.err_email': 'Informe um e-mail válido.',
    'login.credits': 'Coordenação Prof. Dr. Jonas A. Kunzler · mantido por Henrique Carmine',
    'topbar.panel': '— Painel',
    'topbar.no_project': 'Nenhum projeto no ar',
    'topbar.p1_on': 'Projeto 1 · Open5GS no ar',
    'topbar.p2_on': 'Projeto 2 · OAI/RIC no ar',
    'topbar.loading': 'carregando...',
    'topbar.role_professor': 'Professor',
    'topbar.role_student': 'Aluno',
    'topbar.students': '{n} alunos',
    'topbar.student_one': '1 aluno',
    'topbar.projection': '⛶ Projeção',
    'topbar.projection_title': 'Modo projeção — tela limpa para o datashow (Esc para sair)',
    'topbar.exit_projection': '✕ Sair da projeção',
    'topbar.logout': '⎋ Sair',
    'topbar.logout_title_admin': 'Sair (logout) — libera a vaga de professor para outro entrar',
    'topbar.logout_title_guest': 'Sair (logout) do painel',
    'topbar.logout_confirm': 'Sair do painel?',
    'topbar.logout_confirm_admin': 'Sair do painel?\n\nIsso libera a vaga de professor para outro entrar.',
  },
  en: {
    'ui.lang_title': 'Language',
    'ui.theme_to_light': 'Switch to light theme',
    'ui.theme_to_dark': 'Switch to dark theme',
    'login.subtitle': '5G laboratory control panel',
    'login.user': 'Username',
    'login.pass': 'Password',
    'login.enter': 'Sign in',
    'login.or_student': 'or join as a student',
    'login.guest_hint': 'Follow the class live (read-only). Enter your name and e-mail to join — this is the class attendance record.',
    'login.ph_name': 'Your full name',
    'login.ph_email': 'Your e-mail',
    'login.enter_student': 'Join as a student (watch live)',
    'login.err_invalid': 'Invalid username or password.',
    'login.err_conn': 'Connection failed. Please try again.',
    'login.err_name': 'Please enter your full name.',
    'login.err_email': 'Please enter a valid e-mail.',
    'login.credits': 'Coordinated by Prof. Dr. Jonas A. Kunzler · maintained by Henrique Carmine',
    'topbar.panel': '— Panel',
    'topbar.no_project': 'No project running',
    'topbar.p1_on': 'Project 1 · Open5GS running',
    'topbar.p2_on': 'Project 2 · OAI/RIC running',
    'topbar.loading': 'loading...',
    'topbar.role_professor': 'Professor',
    'topbar.role_student': 'Student',
    'topbar.students': '{n} students',
    'topbar.student_one': '1 student',
    'topbar.projection': '⛶ Projection',
    'topbar.projection_title': 'Projection mode — clean screen for the projector (Esc to exit)',
    'topbar.exit_projection': '✕ Exit projection',
    'topbar.logout': '⎋ Sign out',
    'topbar.logout_title_admin': 'Sign out — frees the professor slot for someone else',
    'topbar.logout_title_guest': 'Sign out of the panel',
    'topbar.logout_confirm': 'Sign out of the panel?',
    'topbar.logout_confirm_admin': 'Sign out of the panel?\n\nThis frees the professor slot for someone else.',
  },
  es: {
    'ui.lang_title': 'Idioma',
    'ui.theme_to_light': 'Cambiar al tema claro',
    'ui.theme_to_dark': 'Cambiar al tema oscuro',
    'login.subtitle': 'Panel de control del laboratorio 5G',
    'login.user': 'Usuario',
    'login.pass': 'Contraseña',
    'login.enter': 'Entrar',
    'login.or_student': 'o entra como alumno',
    'login.guest_hint': 'Sigue la clase en vivo (solo lectura). Escribe tu nombre y correo para entrar — es el registro de asistencia del grupo.',
    'login.ph_name': 'Tu nombre completo',
    'login.ph_email': 'Tu correo electrónico',
    'login.enter_student': 'Entrar como alumno (seguir en vivo)',
    'login.err_invalid': 'Usuario o contraseña inválidos.',
    'login.err_conn': 'Fallo de conexión. Inténtalo de nuevo.',
    'login.err_name': 'Escribe tu nombre completo.',
    'login.err_email': 'Escribe un correo válido.',
    'login.credits': 'Coordinación Prof. Dr. Jonas A. Kunzler · mantenido por Henrique Carmine',
    'topbar.panel': '— Panel',
    'topbar.no_project': 'Ningún proyecto en marcha',
    'topbar.p1_on': 'Proyecto 1 · Open5GS en marcha',
    'topbar.p2_on': 'Proyecto 2 · OAI/RIC en marcha',
    'topbar.loading': 'cargando...',
    'topbar.role_professor': 'Profesor',
    'topbar.role_student': 'Alumno',
    'topbar.students': '{n} alumnos',
    'topbar.student_one': '1 alumno',
    'topbar.projection': '⛶ Proyección',
    'topbar.projection_title': 'Modo proyección — pantalla limpia para el proyector (Esc para salir)',
    'topbar.exit_projection': '✕ Salir de la proyección',
    'topbar.logout': '⎋ Salir',
    'topbar.logout_title_admin': 'Salir (logout) — libera el puesto de profesor para otra persona',
    'topbar.logout_title_guest': 'Salir (logout) del panel',
    'topbar.logout_confirm': '¿Salir del panel?',
    'topbar.logout_confirm_admin': '¿Salir del panel?\n\nEsto libera el puesto de profesor para otra persona.',
  },
  fr: {
    'ui.lang_title': 'Langue',
    'ui.theme_to_light': 'Passer au thème clair',
    'ui.theme_to_dark': 'Passer au thème sombre',
    'login.subtitle': 'Tableau de bord du laboratoire 5G',
    'login.user': 'Utilisateur',
    'login.pass': 'Mot de passe',
    'login.enter': 'Se connecter',
    'login.or_student': 'ou entrez comme étudiant',
    'login.guest_hint': "Suivez le cours en direct (lecture seule). Indiquez votre nom et votre e-mail pour entrer — c'est le registre de présence du groupe.",
    'login.ph_name': 'Votre nom complet',
    'login.ph_email': 'Votre e-mail',
    'login.enter_student': 'Entrer comme étudiant (suivre en direct)',
    'login.err_invalid': 'Utilisateur ou mot de passe invalide.',
    'login.err_conn': 'Échec de connexion. Réessayez.',
    'login.err_name': 'Indiquez votre nom complet.',
    'login.err_email': 'Indiquez un e-mail valide.',
    'login.credits': 'Coordination Prof. Dr. Jonas A. Kunzler · maintenu par Henrique Carmine',
    'topbar.panel': '— Tableau de bord',
    'topbar.no_project': 'Aucun projet en cours',
    'topbar.p1_on': 'Projet 1 · Open5GS en cours',
    'topbar.p2_on': 'Projet 2 · OAI/RIC en cours',
    'topbar.loading': 'chargement...',
    'topbar.role_professor': 'Professeur',
    'topbar.role_student': 'Étudiant',
    'topbar.students': '{n} étudiants',
    'topbar.student_one': '1 étudiant',
    'topbar.projection': '⛶ Projection',
    'topbar.projection_title': 'Mode projection — écran épuré pour le vidéoprojecteur (Échap pour quitter)',
    'topbar.exit_projection': '✕ Quitter la projection',
    'topbar.logout': '⎋ Quitter',
    'topbar.logout_title_admin': 'Se déconnecter — libère la place de professeur',
    'topbar.logout_title_guest': 'Se déconnecter du panneau',
    'topbar.logout_confirm': 'Quitter le panneau ?',
    'topbar.logout_confirm_admin': 'Quitter le panneau ?\n\nCela libère la place de professeur pour quelqu\'un d\'autre.',
  },
};

const I18N = (() => {
  const HTML_LANG = { pt: 'pt-BR', en: 'en', es: 'es', fr: 'fr' };
  let lang = 'pt';
  const listeners = [];

  function detect() {
    try {
      const saved = localStorage.getItem('c5g-lang');
      if (saved && I18N_DICTS[saved]) return saved;
    } catch (e) { /* sem localStorage (ex.: teste) */ }
    if (typeof navigator !== 'undefined') {
      const nav = (navigator.language || '').slice(0, 2).toLowerCase();
      if (I18N_DICTS[nav]) return nav;
    }
    return 'pt';
  }

  // Fallback: <lang> → en → pt → a própria chave (nunca quebra a tela).
  function t(key, params) {
    for (const l of [lang, 'en', 'pt']) {
      const v = I18N_DICTS[l] && I18N_DICTS[l][key];
      if (v !== undefined) {
        return params ? v.replace(/\{(\w+)\}/g, (_, k) => (params[k] !== undefined ? params[k] : '{' + k + '}')) : v;
      }
    }
    return key;
  }

  function apply(root) {
    const scope = root || document;
    scope.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
    scope.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.dataset.i18nTitle); });
    scope.querySelectorAll('[data-i18n-ph]').forEach(el => { el.placeholder = t(el.dataset.i18nPh); });
    document.documentElement.lang = HTML_LANG[lang] || 'pt-BR';
  }

  function set(l) {
    if (!I18N_DICTS[l]) return;
    lang = l;
    try { localStorage.setItem('c5g-lang', l); } catch (e) { /* ok */ }
    apply();
    listeners.forEach(f => { try { f(l); } catch (e) { /* listener não derruba os demais */ } });
  }

  function onChange(f) { listeners.push(f); }

  lang = detect();
  return { t, set, apply, onChange, get lang() { return lang; } };
})();

// Auto-aplica e liga o seletor 🌐 (id="lang-sel") quando houver DOM.
if (typeof document !== 'undefined' && document.addEventListener) {
  document.addEventListener('DOMContentLoaded', () => {
    I18N.apply();
    const sel = document.getElementById('lang-sel');
    if (sel) {
      sel.value = I18N.lang;
      sel.title = I18N.t('ui.lang_title');
      sel.addEventListener('change', () => { I18N.set(sel.value); sel.title = I18N.t('ui.lang_title'); });
    }
  });
}
