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
