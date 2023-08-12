const fileInput = document.getElementById("fileInput");
const dropZone = document.getElementById("dropZone");
const originalImage = document.getElementById("originalImage");
const segmentedImage = document.getElementById("segmentedImage");
const downloadLink = document.getElementById("downloadLink");

let currentFile = null;

function handleFile(file) {
    currentFile = file;
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {
        originalImage.src = reader.result;
    };
}

function handleDrop(e) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFile(file);
}

function dataURLtoFile(dataurl, filename) {
    let arr = dataurl.split(','),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);

    for (let i = 0; i < n; i++) {
        u8arr[i] = bstr.charCodeAt(i);
    }
    return new File([u8arr], filename, { type: mime });
}

async function predict() {
    if (!originalImage.src) {
        console.error("No image selected.");
        return;
    }

    // Получить выбранный сервер
    const server = document.querySelector('input[name="server"]:checked').value;

    const formData = new FormData();
    formData.append("image", dataURLtoFile(originalImage.src, "input.png"));


    try {
        const response = await fetch(`${server}/process_image`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        // Получить сегментированное изображение и установить его как src у segmentedImage
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        segmentedImage.src = blobUrl;
        downloadLink.href = blobUrl;
    } catch (error) {
        console.error(error);
    }
}

fileInput.addEventListener("change", function() {
    handleFile(this.files[0]);
});

dropZone.addEventListener("dragover", function(e) {
    e.preventDefault();
});

dropZone.addEventListener("drop", handleDrop);
