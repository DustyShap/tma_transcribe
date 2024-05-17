let queryCount = 1;
function addQueryInput() {
    if (queryCount < 5) {
        queryCount++;
        const div = document.createElement('div');
        div.innerHTML = `<input type="text" name="query${queryCount}" placeholder="Search transcriptions...">`;
        document.getElementById('queryInputs').appendChild(div);
    }
}

function toggleVisibility(segmentId) {
    var content = document.getElementById(segmentId);
    if (content.style.display === "none") {
        content.style.display = "block";
    } else {
        content.style.display = "none";
    }
}

function toggleAudioPlayer(id) {
    var player = document.getElementById(id);
    player.style.display = player.style.display === "none" ? "block" : "none";
}

document.addEventListener('DOMContentLoaded', function() {
    const yearDropdown = document.getElementById('yearDropdown');
    const monthDropdown = document.getElementById('monthDropdown');
    const dayDropdown = document.getElementById('dayDropdown');

    yearDropdown.addEventListener('change', function() {
        // Check if a year is selected
        if (this.value) {
            monthDropdown.removeAttribute('disabled');
            dayDropdown.removeAttribute('disabled');// Enable the month dropdown
        } else {
            monthDropdown.setAttribute('disabled', 'disabled'); // Disable the month dropdown
            dayDropdown.setAttribute('disabled', 'disabled'); // Disable the day dropdown
            monthDropdown.value = ''; // Optionally reset the month value
        }
    });
});
// Add this to your scripts.js or directly in a <script> tag in your HTML
function showSpinner() {
  document.getElementById('loadingSpinner').style.display = 'flex';
}

// Optional: Add an event listener to hide the spinner when the page loads
window.addEventListener('load', function() {
  document.getElementById('loadingSpinner').style.display = 'none';
});

function toggleVisibility(segmentId) {
    var content = document.getElementById(segmentId);
    var closeButton = document.getElementById('closeButton');
    if (content.style.display === "none") {
        // Hide any other open transcriptions
        var allContent = document.querySelectorAll('.content');
        allContent.forEach(function(el) {
            el.style.display = "none";
        });

        // Show the selected transcription
        content.style.display = "block";

        // Show the close button
        closeButton.style.display = "block";

        // Scroll to the selected transcription
        document.getElementById('transcription' + segmentId.replace('content', '')).scrollIntoView({ behavior: 'smooth' });
    } else {
        content.style.display = "none";
        closeButton.style.display = "none";
    }
}

function closeCurrentTranscription() {
    // Hide all open transcriptions
    var allContent = document.querySelectorAll('.content');
    allContent.forEach(function(el) {
        el.style.display = "none";
    });

    // Hide the close button
    var closeButton = document.getElementById('closeButton');
    closeButton.style.display = "none";
}