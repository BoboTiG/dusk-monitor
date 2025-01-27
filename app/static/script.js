// Highly inspired by https://github.com/LucaCuello/CircularCountdownTemplate
const countdownContainer = document.getElementById("countdown");

countdownContainer.innerHTML = `<svg id="progress-wrapper" width="500" height="500" viewBox="0 0 500 500">
<circle cx="250" cy="250" r="200" stroke="#000" stroke-width="50" fill="transparent" id="progress" />
</svg>`;
countdownContainer.style.position = "relative";

const progressWrapper = document.getElementById("progress-wrapper"),
  progress = document.getElementById("progress"),
  options = {
    duration: +countdownContainer.dataset.duration,
    transition: countdownContainer.dataset.transition,
    color: countdownContainer.dataset.color,
    size: +countdownContainer.dataset.size,
  },
  circularCountdown = ({duration, transition, color, size}) => {
    progressWrapper.style.width = `${size}px`;
    progressWrapper.style.height = `${size}px`;
    progressWrapper.style.transform = 'rotate(270deg)';
    progress.style.stroke = color;
    progressWrapper.style.strokeDasharray = progress.getTotalLength();
    progressWrapper.style.animation = `progress ${transition} ${duration}s forwards`;
  },
  initCountdown = () => {
    circularCountdown(options);
  };

initCountdown();
