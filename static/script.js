document.getElementById("upload-btn").addEventListener("click", async () => {
    const fileInput = document.getElementById("file-upload");
    const mediaType = document.getElementById("media-type").value; // Get selected media type
    const statusElement = document.getElementById("upload-status");

    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file to upload.");
        return;
    }

    // Determine the endpoint based on the media type
    const endpoint = mediaType === "image" ? "/predict-image" : "/predict-video";

    const formData = new FormData();
    formData.append("file", file);

    try {
        statusElement.textContent = "Uploading and analyzing the file...";
        
        // Send file to the backend
        const response = await fetch(endpoint, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to process the file. Please try again.");
        }

        const result = await response.json();
        statusElement.textContent = `Result: ${result.result}. Confidence: ${result.confidence}`;
    } catch (error) {
        console.error("Error:", error);
        statusElement.textContent = "An error occurred while processing the file.";
    }
});
