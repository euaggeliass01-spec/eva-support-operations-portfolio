/*
EDIT ONLY THE VALUES INSIDE QUOTES.

Using "Eva S." publicly is completely acceptable.
Your full legal name can remain only in your CV and application.

Anything entered here becomes public on GitHub Pages.
*/
window.PORTFOLIO_PROFILE = {
  fullName: "Eva S.",
  displayName: "Eva S.",
  email: "euaggeliass01@gmail.com",
  location: "Europe — Greece / Germany"
};

document.addEventListener("DOMContentLoaded", function () {
  const p = window.PORTFOLIO_PROFILE;

  document.querySelectorAll("[data-profile-display-name]").forEach(
    el => el.textContent = p.displayName
  );
  document.querySelectorAll("[data-profile-full-name]").forEach(
    el => el.textContent = p.fullName
  );
  document.querySelectorAll("[data-profile-email-text]").forEach(
    el => el.textContent = p.email
  );
  document.querySelectorAll("[data-profile-email-link]").forEach(
    el => el.href = "mailto:" + p.email
  );
  document.querySelectorAll("[data-profile-location]").forEach(
    el => el.textContent = p.location
  );

  document.title = document.title.replace("Eva S.", p.fullName);
  const description = document.querySelector('meta[name="description"]');
  if (description) {
    description.content = description.content.replace("Eva S.", p.fullName);
  }
});