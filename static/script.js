let mediaRecorder;
let audioChunks = [];

document.getElementById("recordBtn").addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    audioChunks = [];
    mediaRecorder.start();
    document.getElementById("status").innerText = "Recording...";

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };
});

document.getElementById("stopBtn").addEventListener("click", () => {
    if (!mediaRecorder) return;

    mediaRecorder.stop();
    document.getElementById("status").innerText = "Processing...";

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");

        const response = await fetch("/record", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        document.getElementById("status").innerText = "";
        document.getElementById("result").innerText = data.text || "Speech not recognized";
    };
});
