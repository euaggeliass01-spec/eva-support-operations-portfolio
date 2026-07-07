(function(){
  const button = document.getElementById('launch-playground');
  if(!button) return;

  const isPublicHttps =
    location.protocol === 'https:' &&
    location.hostname !== 'localhost' &&
    location.hostname !== '127.0.0.1';

  if(isPublicHttps){
    const base = new URL('.', location.href);
    const blueprint = new URL('woocommerce-lab/blueprint.json', base).href;
    button.href = 'https://playground.wordpress.net/?blueprint-url=' + encodeURIComponent(blueprint);
    button.target = '_blank';
    button.rel = 'noopener';
    button.textContent = 'Launch WooCommerce lab';
  } else {
    button.href = 'woocommerce-lab/index.html';
    button.removeAttribute('target');
    button.textContent = 'View WooCommerce lab';
  }
})();