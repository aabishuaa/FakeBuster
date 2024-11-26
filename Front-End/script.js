
document.getElementById('upload-btn').addEventListener('click', () => {
    const fileInput = document.getElementById('file-upload');
    if (fileInput.files.length === 0) {
        alert('Please select a file to upload.');
    } else {
        alert('File uploaded successfully!');
    
    }
});
