function openModal() {
    document.getElementById("addModal").style.display = "block";
  }
  
  function closeModal() {
    document.getElementById("addModal").style.display = "none";
  }
  
  window.onclick = function(event) {
    const modal = document.getElementById("addModal");
    if (event.target == modal) {
      closeModal();
    }
  };
  
  document.getElementById("relationForm")?.addEventListener("submit", function(e) {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const relation = document.getElementById("relation").value;
  
    alert(`Added ${name} (${relation})`); // Placeholder for actual logic
    closeModal();
    this.reset();
  });
  