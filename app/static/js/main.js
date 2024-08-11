// Add any custom JavaScript here
document.addEventListener('DOMContentLoaded', function() {
    // Example: Auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        });
    }, 5000);
});
