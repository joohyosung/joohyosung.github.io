// Keep section navigation in sync with the section currently being read.
const navigationLinks = [...document.querySelectorAll('nav a[href^="#"]')];
const navigationSections = navigationLinks.map(link => document.querySelector(link.hash)).filter(Boolean);
if ('IntersectionObserver' in window) {
  const visibleSections = new Map();
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => visibleSections.set(entry.target.id, entry.isIntersecting));
    const current = navigationSections.find(section => visibleSections.get(section.id));
    navigationLinks.forEach(link => {
      if (current && link.hash === `#${current.id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }, { rootMargin: '-90px 0px -45% 0px', threshold: 0 });
  navigationSections.forEach(section => observer.observe(section));
}
