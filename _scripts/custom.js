/* Project-specific motion and homepage carousel behavior. */

{
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const initReveals = () => {
    const targets = [...document.querySelectorAll("[data-reveal]")];
    if (!targets.length || reducedMotion.matches || !("IntersectionObserver" in window)) {
      targets.forEach((target) => target.classList.add("is-visible"));
      return;
    }

    document.documentElement.classList.add("reveal-enabled");
    targets.forEach((target, index) => {
      target.style.setProperty("--reveal-delay", `${Math.min(index % 4, 3) * 55}ms`);
    });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8%", threshold: 0.08 }
    );
    targets.forEach((target) => observer.observe(target));
  };

  const initSecondaryHeader = () => {
    const header = document.querySelector("body > header.background:not([data-big])");
    if (!header) return;

    const update = () => header.classList.toggle("is-scrolled", window.scrollY > 16);
    update();
    window.addEventListener("scroll", update, { passive: true });
  };

  const initCarousel = (carousel) => {
    const track = carousel.querySelector("[data-carousel-track]");
    const slides = [...carousel.querySelectorAll("[data-carousel-slide]")];
    const dots = [...carousel.querySelectorAll("[data-carousel-dot]")];
    const previous = carousel.querySelector("[data-carousel-prev]");
    const next = carousel.querySelector("[data-carousel-next]");
    const status = carousel.querySelector("[data-carousel-status]");
    if (!track || slides.length < 1) return;

    let current = 0;
    let timer = null;
    let pointerStart = null;
    const seconds = Math.min(Math.max(Number(carousel.dataset.autoplaySeconds) || 6, 5), 12);

    const render = (index, announce = false) => {
      current = (index + slides.length) % slides.length;
      track.style.transform = `translate3d(${-100 * current}%, 0, 0)`;
      slides.forEach((slide, slideIndex) => {
        slide.setAttribute("aria-hidden", String(slideIndex !== current));
      });
      dots.forEach((dot, dotIndex) => {
        dot.setAttribute("aria-current", String(dotIndex === current));
      });
      if (announce && status) {
        status.textContent = `${current + 1} / ${slides.length}`;
      }
    };

    const stop = () => {
      if (timer) window.clearInterval(timer);
      timer = null;
    };

    const start = () => {
      stop();
      if (slides.length < 2 || reducedMotion.matches || document.hidden) return;
      timer = window.setInterval(() => render(current + 1), seconds * 1000);
    };

    previous?.addEventListener("click", () => {
      render(current - 1, true);
      start();
    });
    next?.addEventListener("click", () => {
      render(current + 1, true);
      start();
    });
    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        render(Number(dot.dataset.carouselDot), true);
        start();
      });
    });

    carousel.addEventListener("mouseenter", stop);
    carousel.addEventListener("mouseleave", start);
    carousel.addEventListener("focusin", stop);
    carousel.addEventListener("focusout", (event) => {
      if (!carousel.contains(event.relatedTarget)) start();
    });
    carousel.addEventListener("pointerdown", (event) => {
      pointerStart = event.clientX;
      stop();
    });
    carousel.addEventListener("pointerup", (event) => {
      if (pointerStart === null) return;
      const distance = event.clientX - pointerStart;
      pointerStart = null;
      if (Math.abs(distance) > 45) render(current + (distance < 0 ? 1 : -1), true);
      start();
    });
    carousel.addEventListener("pointercancel", () => {
      pointerStart = null;
      start();
    });
    document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
    reducedMotion.addEventListener?.("change", start);

    render(0);
    start();
  };

  const init = () => {
    initSecondaryHeader();
    initReveals();
    document.querySelectorAll("[data-carousel]").forEach(initCarousel);
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
}
