function toggleVisibility(segmentId) {
    var content = document.getElementById(segmentId);
    if (content.style.display === "none") {
        content.style.display = "block";
    } else {
        content.style.display = "none";
    }
}
function filterByDate() {
    var startDate = document.getElementById('startDate').value;
    var endDate = document.getElementById('endDate').value;
    var transcriptions = document.getElementById('transcriptions').children;

    for (var i = 0; i < transcriptions.length; i++) {
        var transcriptionDate = transcriptions[i].getAttribute('data-date');

        if (transcriptionDate >= startDate && transcriptionDate <= endDate) {
            transcriptions[i].style.display = '';
        } else {
            transcriptions[i].style.display = 'none';
        }
    }
}

function highlightSearchTerm(searchTerm, containerId) {
    if (!searchTerm) return;

    const container = document.getElementById(containerId);
    let content = container.innerHTML;
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    content = content.replace(regex, '<span class="highlight">$1</span>');
    container.innerHTML = content;
}
