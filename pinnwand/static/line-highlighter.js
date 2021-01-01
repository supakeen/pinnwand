(() => {

let fileTableBodies;
let hashChangedByClick = false;

window.addEventListener("DOMContentLoaded", () => {
    fileTableBodies = document.querySelectorAll("table.sourcetable tbody");
    if (fileTableBodies.length === 0) {
        return;
    }

    window.addEventListener("hashchange", onHashChange);
    addEventListenerToFileTableBodies();

    if (window.location.hash !== "") {
        highlightLine({ hash: window.location.hash, scrollIntoView: true });
    }
});

function onHashChange(event) {
    let oldUrl = new URL(event.oldURL);
    let newUrl = new URL(event.newURL);
    highlightLine({ hash: oldUrl.hash, scrollIntoView: false });
    highlightLine({ hash: newUrl.hash, scrollIntoView: !hashChangedByClick });
    hashChangedByClick = false;
}

function addEventListenerToFileTableBodies() {
    for (let fileIndex = 0; fileIndex < fileTableBodies.length; fileIndex++) {
        let fileTableBody = fileTableBodies[fileIndex];
        fileTableBody.addEventListener("click", (event) => {
            let lineNumber;
            let t = event.target;
            if (t.classList.contains("linenos")) {
                lineNumber = t.firstElementChild.dataset.lineNumber;
            } else if (t.dataset.hasOwnProperty("lineNumber")) {
                lineNumber = t.dataset.lineNumber;
            }
            if (lineNumber) {
                setFileLineHash(fileIndex + 1, parseInt(lineNumber, 10));
                hashChangedByClick = true;
            }
        });
    }
}

function highlightLine({ hash, scrollIntoView }) {
    let { fileIndex, lineIndex } = getFileLineIndexFromHash(hash);
    if (fileIndex === null || fileIndex >= fileTableBodies.length) {
        return;
    }
    let tableRows = fileTableBodies[fileIndex].children;
    if (lineIndex >= tableRows.length) {
        return;
    }
    let tableRow = tableRows[lineIndex];
    let code = tableRow.querySelector("td.code");
    code.classList.toggle("highlighted");
    if (scrollIntoView) {
        code.scrollIntoView();
    }
}

function getFileLineIndexFromHash(hash) {
    let splitHash = hash.substring(1).split("L");
    let [ fileIndex, lineIndex ] = splitHash.map((x) => {
        return parseInt(x, 10) - 1;
    });
    if (isNaN(fileIndex) || isNaN(lineIndex)
            || fileIndex < 0 || lineIndex < 0) {
        return { fileIndex: null, lineIndex: null };
    } else {
        return { fileIndex, lineIndex };
    }
}

function setFileLineHash(fileNumber, lineNumber) {
    window.location.hash = `${fileNumber}L${lineNumber}`;
}

})();
