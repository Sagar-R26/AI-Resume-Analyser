document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('resume');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const maxSize = 16 * 1024 * 1024;
                if (file.size > maxSize) {
                    alert('File is too large. Maximum size is 16MB.');
                    this.value = '';
                }
            }
        });
    }
});
