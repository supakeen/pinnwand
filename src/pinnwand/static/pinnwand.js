let indents = {
    "python": " ".repeat(4),
    "python2": " ".repeat(4),
};

document.addEventListener('keydown', e => {
    if ((e.ctrlKey && !e.altKey) && e.key === 's') {
        let submitButton = document.querySelector("button");
        // Only trigger on pages that have a submit button
        if (submitButton) {
            // Prevent the Save dialog from opening
            e.preventDefault();
            submitButton.click();
        }
    }
});

window.addEventListener("load", (event) => {
    setupColorScheme();

    if(document.querySelector("section.paste-submit")) {
        setupCreatePage();
        addRemoveButtons();
    } else {
        setupShowPage();
    }
});


function getFirstEmptyFilePartSection() {
    for (let node of document.querySelectorAll("section.file-part")) {
        if (
            (node.querySelector("input[name='filename']").value === '')
            && (node.querySelector("textarea[name='raw']").value === '')
        ) {
            return node
        }
    }
}

function addRemoveButtons() {
    const tag = "button";
    const className = "remove";
    const label = "Remove this file";
    const selector = `${tag}.${className}`;

    const main = document.querySelector("main.page-create");

    const fileParts = document.querySelectorAll('.file-part .file-meta');
    if (fileParts.length < 2) {
        return;
    }

    fileParts.forEach(el => {
        if (el.querySelector(selector)) {
            return;
        }
        const removeButton = document.createElement(tag);
        removeButton.innerText = label;
        removeButton.className = className;
        el.appendChild(removeButton);

        const removeSection = (section) => {
            main.removeChild(section);
            const fileParts = document.querySelectorAll('.file-part .file-meta');
            if (fileParts.length < 2) {
                document.querySelector(selector)?.remove();
            }
        };

        removeButton.addEventListener("click", (event) => {
            event.preventDefault();
            const section = event.target.parentNode.parentNode;
            const sectionContent = section.querySelector('textarea').value;
            if (sectionContent) {
                const popover = document.querySelector(".confirmation-popover");
                popover.removeAttribute("hidden");
                popover.querySelector(".confirm").focus();
                popover.querySelector(".cancel").addEventListener("click", (event) => event.target.parentNode.parentNode.setAttribute("hidden", true));
                popover.querySelector(".confirm").addEventListener("click", (event) => {
                    event.target.parentNode.parentNode.setAttribute("hidden", true);
                    removeSection(section);
                });
            } else {
                removeSection(section);
            }
        });
    });
};

function addNewFile() {
    let template = document.querySelector("section.file-template").cloneNode(true);
    template.className = "file-part file-extra";

    template.querySelector("textarea").addEventListener("keydown", indent_textarea);

    document.querySelector("main.page-create").insertBefore(
        template,
        document.querySelector("section.paste-submit")
    );
    addRemoveButtons();
    return template;
}

function upload_file(file) {
    let filePartSectionToUse = getFirstEmptyFilePartSection();
    if (filePartSectionToUse === undefined) {
        filePartSectionToUse  = addNewFile();
    }

    const {filename, content} = file
    filePartSectionToUse.querySelector("input[name='filename']").value = filename;
    filePartSectionToUse.querySelector("textarea[name='raw']").value = content;
    filePartSectionToUse.querySelector("select[name='lexer']").value = 'autodetect';
}



function indent_textarea(event) {
	let selector = event.target.parentNode.parentNode.querySelector("select[name='lexer']"),
	    lexer = selector.options[selector.selectedIndex].text

	if(!(lexer && lexer.toLowerCase().indexOf("python") == 0)) {
		return
	}

    let indent = " ".repeat(4);
	let keyCode = event.keyCode || event.which;

	if (keyCode == 9) {
		event.preventDefault();
		var start = this.selectionStart;
        var end = this.selectionEnd;
		var v = this.value;
		if (start == end) {
		    this.value = v.slice(0, start) + indent + v.slice(start);
		    this.selectionStart = start + indent.length;
		    this.selectionEnd = start + indent.length;
		    return;
		}

		var selectedLines = [];
		var inSelection = false;
		var lineNumber = 0;
		for (var i = 0; i < v.length; i++) {
		    if (i == start) {
                inSelection = true;
                selectedLines.push(lineNumber);
		    }
		    if (i >= end)
                inSelection = false;

		    if (v[i] == "\n") {
			lineNumber++;
			if (inSelection)
			    selectedLines.push(lineNumber);
		    }
		}
		var lines = v.split("\n");
		for (var i = 0; i < selectedLines.length; i++)
		{
		    lines[selectedLines[i]] = indent + lines[selectedLines[i]];
		}

		this.value = lines.join("\n");
    } else if (keyCode == 13) {
		event.preventDefault();

		var start = this.selectionStart;
		var end = this.selectionEnd;
        var v = this.value;
        var thisLine = "";
        var indentation = 1;

        for (var i = start-1; i >= 0 && v[i] != "\n"; i--) {
            thisLine = v[i] + thisLine;
        }

        for (var i = 0; i < thisLine.length && thisLine[i] == " "; i++) {
            indentation++;
        }

        this.value = v.slice(0, start) + "\n" + " ".repeat(indentation-1) + v.slice(start);
        this.selectionStart = start + indentation;
        this.selectionEnd = end + indentation;
	}
}

function setupColorScheme() {
    let storage = window.localStorage,
        colorSchemeButton = document.getElementById("toggle-color-scheme");

    if(storage.getItem("other-color") == "true") {
        document.querySelector("html").classList.toggle("other-color");
    }

    if(colorSchemeButton != null) {
        colorSchemeButton.addEventListener("click", function(event) {
            if(storage.getItem("other-color") == "true") {
                storage.setItem("other-color", "false");
            } else {
                storage.setItem("other-color", "true");
            }

            document.querySelector("html").classList.toggle("other-color");
        });
    }
}

function setupShowPage() {
    let wordWrapButton = document.getElementById("toggle-word-wrap");
    if(wordWrapButton != null) {
        wordWrapButton.addEventListener("click", function(event) {
            let codeBlocks = document.querySelectorAll("div.code");
            for(let i = 0; i < codeBlocks.length; i++) {
                codeBlocks[i].classList.toggle("no-word-wrap");
            }
        });
    }

    let copyButtons = document.querySelectorAll("button.copy-button");

    for(let i = 0; i < copyButtons.length; i++) {
        let copyButton = copyButtons[i];

        copyButton.addEventListener("click", function(event) {
            event.preventDefault();

            let textarea = event.target.parentNode.parentNode.querySelector("textarea.copy-area");
            let listener = (event) => {
                event.preventDefault();
                event.clipboardData.setData("text/plain", textarea.value);
            };

            document.addEventListener('copy', listener);
            document.execCommand('copy');
            document.removeEventListener('copy', listener);
        });
    };

    return false;
}

function setupCreatePage() {
    setupFileDrop();

    let but = document.createElement("button");

    but.innerText = "Add another file.";
    but.className = "add";
    but.href = "#";

    but.addEventListener("click", function(event) {
        event.preventDefault();
        addNewFile();
    })

    document.querySelector("section.paste-submit").appendChild(but);

    let textareas = document.querySelectorAll('section.file-part textarea');
    for(let i = 0; i < textareas.length; i++) {
        textareas[i].addEventListener("keydown", indent_textarea);
    }
}

function setupFileDrop() {
    const filedrop = document.getElementById('file-drop');
    const fileInput = document.getElementById('file-input');

    filedrop.addEventListener('dragenter', handleDragEnter, false);
    filedrop.addEventListener('dragover', handleDragOver, false);
    filedrop.addEventListener('dragleave', handleDragLeave, false);
    filedrop.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFilePick);

    function handleDragEnter(event) {
        event.preventDefault();
        filedrop.classList.add('dragover');
    }

    function handleDragOver(event) {
        event.preventDefault();
    }

    function handleDragLeave(event) {
        filedrop.classList.remove('dragover');
    }

    async function handleDrop(event) {
        event.preventDefault();
        filedrop.classList.remove('dragover');

        const files = event.dataTransfer.files;
        await handleFiles(files);
    }

    async function handleFilePick(event) {
        const files = event.target.files;
        await handleFiles(files);
        // Reset input to blank state, otherwise we will double upload next time this triggers.
        fileInput.value = null;
    }

    async function handleFiles(files) {
        for (let file of files) {
            upload_file({
                filename: file.name,
                content: await file.text()
            });
        }
    }
}

(() => {

let fileTableBodies;
let hashChangedByClick = false;
let highlightLineSpecification = {};

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
    // Sync internal state with the new ground truth
    highlightLineSpecification = getHighlightSpecificationFromHash(newUrl.hash);
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
                let clickedLineIndex = parseInt(lineNumber, 10) - 1;
                let shiftKey = event.shiftKey;

                let existingStartIndex;
                let existingEndIndex;

                if (highlightLineSpecification[fileIndex] !== undefined) {
                    [existingStartIndex, existingEndIndex] = highlightLineSpecification[fileIndex];
                }

                if (existingStartIndex !== undefined && existingEndIndex !== undefined && shiftKey) {
                    // Extend highlighted line range forward or backward
                    let startIndex = Math.min(clickedLineIndex, existingStartIndex);
                    let endIndex = Math.max(clickedLineIndex, existingEndIndex);
                    highlightLineSpecification[fileIndex] = [startIndex, endIndex];
                } else {
                    // Single click, override the highlighted line for that file
                    highlightLineSpecification[fileIndex] = [clickedLineIndex, clickedLineIndex];
                }
                updateFileLineHash();
                hashChangedByClick = true;
            }
        });
    }
}

function highlightLine({ hash, scrollIntoView }) {
    let highlightSpecification = getHighlightSpecificationFromHash(hash);
    let codeToScrollTo;

    Object.entries(highlightSpecification).forEach(
        ([fileIndex, [startIndex, endIndex]]) => {
            if (fileIndex >= fileTableBodies.length) {
                return
            }
            let tableRows = fileTableBodies[fileIndex].children;
            for (let index = startIndex; index <= Math.min(endIndex, tableRows.length); index++){
                let tableRow = tableRows[index];
                let code = tableRow.querySelector("td.code");
                code.classList.toggle("highlighted");
                codeToScrollTo = codeToScrollTo ?? code;
            }
        }
    )

    if (scrollIntoView) {
        codeToScrollTo.scrollIntoView();
    }
}

function getHighlightSpecificationFromHash(hash) {
    // Supported format:
    //  - 1L2        [First file, select line 2 only]
    //  - 1L2-L3     [First file, select line 2 to line 3 only]
    // Highlight for many files can be defined using comma-separated style:
    // e.g. 1L2-L3,2L3-L4
    // The last specification for the same file take precedence.
    // Returns a mapping of fileNumber -> [startIndex, endIndex]
    const regex = /(?<fileNumber>\d+)L(?<startLine>\d+)(?:-L(?<endLine>\d+))?/g;
    const matches = Array.from(hash.matchAll(regex));

    const result = {};
    for (const match of matches) {
        const fileNumber = parseInt(match.groups.fileNumber) - 1;
        const startLine = parseInt(match.groups.startLine) - 1;
        const endLine = match.groups.endLine ? parseInt(match.groups.endLine) - 1: startLine;
        result[fileNumber] = [startLine, endLine];
    }

    return result;
}

function updateFileLineHash() {
    window.location.hash = Object.entries(highlightLineSpecification).map(
        ([fileIndex, [startIndex, endIndex]]) => {
            return `${parseInt(fileIndex) + 1}L${parseInt(startIndex) + 1}-L${parseInt(endIndex) + 1}`
        }
    ).reduce(
        (prev, curr) => {
            return prev.concat(",", curr)
        }
    );
}

})();
