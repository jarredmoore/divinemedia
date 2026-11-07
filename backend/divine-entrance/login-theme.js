(() => {
  function mount() {
    const nativePage = document.querySelector('.loginPage');
    const form = nativePage?.querySelector('#loginForm');
    if (!form || window.self !== window.top || document.querySelector('.dm-auth-shell')) return;
    // Move the existing nodes: never clone inputs, replace the form, or intercept authentication.
    const shell = document.createElement('main');
    shell.className = 'dm-auth-shell';
    shell.innerHTML = `<header class="dm-header"><a class="dm-brand" href="/" aria-label="Divine Media home"><img src="/divine-entrance/mark.svg" width="42" height="42" alt=""><span>DIVINE<span class="dm-brand-light">MEDIA</span></span></a><a class="dm-auth-back" href="https://watch.divinecreativegroup.com/">Back to exploring <span aria-hidden="true"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg></span></a></header><div class="dm-auth-layout"><section class="dm-auth-story"><p class="dm-eyebrow"><span></span> THE VOICES BEHIND THE STORIES</p><h1>Your voice.<br>Your vision.<br><em>Your next chapter.</em></h1><p>A space for independent minds to make their mark. Sign in and keep creating.</p><div class="dm-auth-art" aria-hidden="true"><div class="dm-orbit dm-orbit-one"></div><div class="dm-light-beam"></div><div class="dm-stage-monogram">D<span></span></div></div><span class="dm-auth-story-note">INDEPENDENT BY DESIGN.</span></section><section class="dm-auth-card" aria-label="Creator sign-in"><div class="dm-auth-welcome"><p class="dm-eyebrow">CREATOR ACCESS</p><h2>Welcome back.</h2><p>Sign in to your Divine Media account.</p></div><div class="dm-native-host"></div><div class="dm-auth-note">Just here to watch or listen?<br><a href="https://watch.divinecreativegroup.com/">Explore Divine Media <span aria-hidden="true"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg></span></a></div></section></div><footer class="dm-footer"><p>A Divine Creative Group platform.</p><a href="/view/">Media library <span aria-hidden="true"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg></span></a></footer>`;
    shell.querySelector('.dm-native-host').append(nativePage);
    document.body.prepend(shell);
    document.body.classList.add('dm-auth-ready');
    document.title = 'Creator sign-in | Divine Media';
    form.querySelector('#inputUser')?.setAttribute('autocomplete', 'username');
    form.querySelector('#inputPassword')?.setAttribute('autocomplete', 'current-password');
    for (const id of ['inputUser', 'inputPassword']) {
      const input = form.querySelector('#' + id);
      const label = input?.closest('.form-group')?.querySelector('label');
      if (label) label.htmlFor = id;
    }
    const icon = document.createElement('link');
    icon.rel = 'icon'; icon.type = 'image/svg+xml'; icon.href = '/divine-entrance/mark.svg';
    document.head.append(icon);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once: true});
  else mount();
})();
