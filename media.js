// Looping clips in .shot figures. Each <source> starts as data-src, so nothing
// downloads until the clip is near the screen; clips pause when scrolled away
// and a click pauses or resumes one. Without JavaScript, or with reduced motion
// turned on, the poster image stays.
(function () {
  var videos = document.querySelectorAll(".shot video");
  if (!videos.length || !("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  function load(video) {
    video.querySelectorAll("source[data-src]").forEach(function (source) {
      source.src = source.getAttribute("data-src");
      source.removeAttribute("data-src");
    });
    video.load();
  }

  function play(video) {
    var started = video.play();
    if (started) started.catch(function () {}); // autoplay blocked: poster stays
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var video = entry.target;
      if (entry.isIntersecting) {
        if (video.querySelector("source[data-src]")) load(video);
        if (!video.dataset.userPaused) play(video);
      } else if (!video.paused) {
        video.pause();
      }
    });
  }, { rootMargin: "200px 0px" });

  videos.forEach(function (video) {
    observer.observe(video);
    video.addEventListener("click", function () {
      if (video.paused) {
        delete video.dataset.userPaused;
        play(video);
      } else {
        video.dataset.userPaused = "1";
        video.pause();
      }
    });
  });
})();
