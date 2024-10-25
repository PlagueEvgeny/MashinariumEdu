const buttons = document.querySelectorAll(".course__detail__module__toggle");

buttons.forEach((button) => {
  button.addEventListener("click", btnClick);
});

function btnClick(event) {
  const button = event.target;
  const moduleSection = button.closest(".course__detail__module__section");
  const content = moduleSection.querySelector(".course__detail__module__desc");

  const isHidden = content.classList.contains("course__detail__module__desc__hidden");
  button.textContent = isHidden ? "-" : "+";

  content.classList.toggle("course__detail__module__desc__hidden");
}