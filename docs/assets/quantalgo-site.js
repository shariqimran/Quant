const cursorLight = document.querySelector(".cursor-light");

if (cursorLight && window.matchMedia("(pointer: fine)").matches) {
  window.addEventListener("pointermove", (event) => {
    cursorLight.style.opacity = "1";
    cursorLight.style.left = `${event.clientX}px`;
    cursorLight.style.top = `${event.clientY}px`;
  });

  window.addEventListener("pointerleave", () => {
    cursorLight.style.opacity = "0";
  });
}

const revealItems = document.querySelectorAll(".section-reveal");

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { rootMargin: "0px 0px -12% 0px", threshold: 0.14 }
  );

  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
}

const dashboard = document.querySelector(".dashboard-frame");

if (dashboard && window.matchMedia("(pointer: fine)").matches) {
  dashboard.addEventListener("pointermove", (event) => {
    const rect = dashboard.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    dashboard.style.transform = `rotateX(${4 - y * 4}deg) rotateY(${-8 + x * 5}deg) translateY(-4px)`;
  });

  dashboard.addEventListener("pointerleave", () => {
    dashboard.style.transform = "";
  });
}
