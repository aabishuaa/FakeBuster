document.addEventListener("DOMContentLoaded", function() {
    async function uploadFile() {
        const formData = new FormData();
        const fileInput = document.getElementById("file-upload");
        const file = fileInput.files[0];
        const mediaType = document.getElementById("media-type").value;

        if (!file) {
            document.getElementById("upload-status").innerText = "Please select a file!";
            return;
        }

        formData.append("file", file);
        const endpoint = mediaType === "image" ? "/predict-image" : "/predict-video";

        // Show the modal with loading spinner
        const modal = document.getElementById("result-modal");
        const loadingSpinner = document.getElementById("loading-spinner");
        const uploadedImage = document.getElementById("uploaded-image");
        const resultText = document.getElementById("prediction-result");
        const confidenceBar = document.getElementById("confidence-bar");
        const fakeProgress = document.getElementById("fake-confidence");
        const realProgress = document.getElementById("real-confidence");

        // Show modal and loading spinner
        modal.style.display = "flex";
        loadingSpinner.style.display = "block";
        confidenceBar.style.display = "none";  // Hide confidence bar initially

        try {
            const response = await fetch(`http://127.0.0.1:5001${endpoint}`, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();

            // Show uploaded image
            const reader = new FileReader();
            reader.onloadend = () => {
                uploadedImage.src = reader.result;
            };
            reader.readAsDataURL(file);

            // Hide loading spinner and show confidence for images
            loadingSpinner.style.display = "none";

            // Set result text
            resultText.innerText = `Prediction: ${data.result}`;

            if (mediaType === "image") {
                // Only show the confidence bar for images
                confidenceBar.style.display = "block";

                // Set confidence bar widths
                fakeProgress.style.width = `${parseFloat(data.confidence.FAKE)}%`;  // Set FAKE confidence bar width
                realProgress.style.width = `${parseFloat(data.confidence.REAL)}%`;  // Set REAL confidence bar width

                // Display the confidence percentages
                const fakeConfidenceText = `${data.confidence.FAKE}`;
                const realConfidenceText = `${data.confidence.REAL}`;
                document.getElementById("fake-confidence-text").innerText = `FAKE Confidence: ${fakeConfidenceText}`;
                document.getElementById("real-confidence-text").innerText = `REAL Confidence: ${realConfidenceText}`;
            } else {
                // Hide confidence bar for videos
                confidenceBar.style.display = "none";
            }

            // Set modal border color based on prediction
            if (data.result === "FAKE") {
                modal.classList.add("fake");
                modal.classList.remove("real");
            } else {
                modal.classList.add("real");
                modal.classList.remove("fake");
            }

        } catch (error) {
            console.error("Error:", error);
            document.getElementById("upload-status").innerText = "An error occurred!";
            modal.style.display = "none"; // Close modal on error
        }
    }

    // Event listener for the upload button
    const uploadButton = document.getElementById("upload-btn");
    if (uploadButton) {
        uploadButton.addEventListener("click", uploadFile);
    }

    // Event listener for the exit button
    const exitButton = document.getElementById("exit-btn");
    if (exitButton) {
        exitButton.addEventListener("click", function() {
            document.getElementById("result-modal").style.display = "none";  // Close modal
        });
    }
});
