document.addEventListener('DOMContentLoaded', function() {
  const buttons = document.querySelectorAll('.quantity-button');
  buttons.forEach(btn => {
    btn.addEventListener('click', function() {
      const index = this.getAttribute('data-index');
      const action = this.getAttribute('data-action');
      const valueSpan = document.getElementById('quantity-' + index);
      let value = parseInt(valueSpan.textContent, 10);
      if (action === 'increment') {
        if (value === 8760) {
          value = 1;
        } else if (value < 8760) {
          value++;
        }
      } else if (action === 'decrement') {
        if (value === 1) {
          value = 8760;
        } else if (value > 1) {
          value--;
        }
      }
      valueSpan.textContent = value;
    });
  });
}); 