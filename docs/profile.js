/*
EDIT ONLY THE VALUES INSIDE QUOTES.

Anything entered here becomes public on GitHub Pages.
Leave linkedin or phone as "" to hide them.
*/
window.PORTFOLIO_PROFILE = {
  fullName: "Eva S.",
  displayName: "Eva S.",
  email: "euaggeliass01@gmail.com",
  location: "Europe — Greece / Germany",
  linkedin: "",
  phone: ""
};

document.addEventListener("DOMContentLoaded", function () {
  const p = window.PORTFOLIO_PROFILE;

  document.querySelectorAll("[data-profile-display-name]").forEach(el => el.textContent = p.displayName);
  document.querySelectorAll("[data-profile-full-name]").forEach(el => el.textContent = p.fullName);
  document.querySelectorAll("[data-profile-email-text]").forEach(el => el.textContent = p.email);
  document.querySelectorAll("[data-profile-email-link]").forEach(el => el.href = "mailto:" + p.email);
  document.querySelectorAll("[data-profile-location]").forEach(el => el.textContent = p.location);

  document.querySelectorAll("[data-profile-linkedin]").forEach(el => {
    if (p.linkedin) {
      el.href = p.linkedin;
      el.hidden = false;
    } else {
      el.hidden = true;
    }
  });

  document.querySelectorAll("[data-profile-phone]").forEach(el => {
    if (p.phone) {
      el.textContent = p.phone;
      el.href = "tel:" + p.phone.replace(/\s+/g, "");
      el.hidden = false;
    } else {
      el.hidden = true;
    }
  });

  document.title = document.title.replace("Eva S.", p.fullName);
  const description = document.querySelector('meta[name="description"]');
  if (description) description.content = description.content.replace("Eva S.", p.fullName);
});