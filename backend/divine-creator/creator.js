(() => {
  function mount() {
    if (window.self !== window.top || document.body.classList.contains('dm-creator')) return;
    const compact = new URLSearchParams(location.search).get('noNavbar');
    if (compact && compact !== '0' && compact !== 'false') return;
    const encoder = /^\/Encoder\/(?:view\/index\.php|index\.php)?$/.test(location.pathname);
    const fileForm = document.querySelector('form#upload input[type=file][name=upl]')?.form;
    const connectForm = encoder && document.querySelector('#loginForm #siteURL')?.form;
    if (!fileForm && !encoder) return;
    if (encoder && !connectForm && !document.querySelector('#fileupload,#mainTabs,#basicOptions')) return;
    const native = encoder ? document.querySelector('.main-container') : fileForm.closest('.container');
    if (!native) return;
    document.body.classList.add('dm-creator', encoder ? 'dm-creator-encoder' : 'dm-creator-direct');
    if (connectForm) document.body.classList.add('dm-creator-connect');
    const brand = document.createElement('header');
    brand.className = 'dmc-header';
    brand.innerHTML = `<a class="dmc-brand" href="/" aria-label="Divine Media home"><img src="/divine-creator/mark.svg" width="38" height="38" alt=""><span>DIVINE<small>MEDIA</small></span></a><span class="dmc-workspace-label">CREATOR WORKSPACE</span><a class="dmc-watch" href="https://divinemedia.us/">View the platform <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg></a>`;
    document.body.prepend(brand);
    const main = document.createElement('main');main.className = 'dmc-main';
    const title = connectForm ? 'Connect your media account.' : encoder ? 'Prepare your next release.' : 'Your next story starts here.';
    const description = connectForm ? 'Use your media site address and existing account to enter the Encoder.' : encoder ? 'Upload source files, choose your settings, and follow the processing queue.' : 'Add ready-to-play audio and video to your media library.';
    main.innerHTML = `<section class="dmc-intro"><div><p class="dmc-eyebrow">DIVINE MEDIA / ${encoder ? 'ENCODER' : 'UPLOAD'}</p><h1>${title}</h1><p class="dmc-description">${description}</p></div><nav class="dmc-tabs" aria-label="Creator workspace"><a href="/upload"${!encoder ? ' aria-current="page"' : ''}>Direct upload</a><a href="/Encoder/"${encoder ? ' aria-current="page"' : ''}>Encoder</a></nav></section><section class="dmc-native" aria-label="${connectForm ? 'Connect to your media site' : 'Native upload controls'}"></section><footer class="dmc-footer"><span>A Divine Creative Group platform.</span><a href="/view/">Media library <span aria-hidden="true">&rarr;</span></a></footer>`;
    native.before(main);main.querySelector('.dmc-native').append(native);
    native.classList.add('dmc-native-container');
    // Keep every existing form/input/button node and its native listeners intact.
    const drop = native.querySelector('#drop');
    if (drop) {
      const emblem = document.createElement('span');emblem.className='dmc-upload-icon';emblem.setAttribute('aria-hidden','true');
      emblem.innerHTML='<svg viewBox="0 0 48 48"><path d="M24 31V9m-9 9 9-9 9 9M10 29v9a2 2 0 0 0 2 2h24a2 2 0 0 0 2-2v-9"/></svg>';
      drop.prepend(emblem);
      const note = document.createElement('p');note.className='dmc-upload-note';note.textContent='Files start uploading when selected.';drop.append(note);
    }
    const directRow = !encoder && fileForm.closest('.row');
    if (directRow) directRow.classList.add('dmc-upload-layout');
    const utility = document.querySelector('#mainNavBar,body>nav.navbar');
    if (utility) utility.classList.add('dmc-utility-nav');
    document.title=(encoder ? 'Encoder' : 'Upload media')+' | Divine Media';
    const icon=document.createElement('link');icon.rel='icon';icon.type='image/svg+xml';icon.href='/divine-creator/mark.svg';document.head.append(icon);
  }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})();
