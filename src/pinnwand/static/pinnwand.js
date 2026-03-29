const INDENT_STORAGE_KEY = "pinnwand-indent";

function getIndentString() {
    let raw = localStorage.getItem(INDENT_STORAGE_KEY);
    let cfg;
    try { cfg = JSON.parse(raw); } catch(e) { cfg = null; }
    let useTabs = cfg?.useTabs ?? false;
    let size = cfg?.size ?? 4;
    return useTabs ? "\t" : " ".repeat(size);
}

function saveIndentPreference(useTabs, size) {
    localStorage.setItem(INDENT_STORAGE_KEY, JSON.stringify({ useTabs, size }));
}

function addIndentToolbar(fileMeta) {
    if (fileMeta.querySelector(".indent-toolbar")) return;

    let raw = localStorage.getItem(INDENT_STORAGE_KEY);
    let cfg;
    try { cfg = JSON.parse(raw); } catch(e) { cfg = null; }
    let useTabs = cfg?.useTabs ?? false;
    let size = cfg?.size ?? 4;

    const toolbar = document.createElement("div");
    toolbar.className = "indent-toolbar";

    // Mode select: Spaces / Tabs
    const modeSelect = document.createElement("select");
    modeSelect.className = "indent-mode-select";
    [["spaces", "Spaces"], ["tabs", "Tabs"]].forEach(([val, label]) => {
        const opt = document.createElement("option");
        opt.value = val;
        opt.textContent = label;
        if ((val === "tabs") === useTabs) opt.selected = true;
        modeSelect.appendChild(opt);
    });
    toolbar.appendChild(modeSelect);

    // Size select: 2 / 4 / 8
    const sizeSelect = document.createElement("select");
    sizeSelect.className = "indent-size-select";
    [2, 4, 8].forEach(n => {
        const opt = document.createElement("option");
        opt.value = n;
        opt.textContent = n;
        if (n === size) opt.selected = true;
        sizeSelect.appendChild(opt);
    });
    sizeSelect.style.display = useTabs ? "none" : "";
    toolbar.appendChild(sizeSelect);

    modeSelect.addEventListener("change", () => {
        const nowTabs = modeSelect.value === "tabs";
        const nowSize = parseInt(sizeSelect.value);
        saveIndentPreference(nowTabs, nowSize);
        updateAllToolbars();
    });

    sizeSelect.addEventListener("change", () => {
        const nowTabs = modeSelect.value === "tabs";
        const nowSize = parseInt(sizeSelect.value);
        saveIndentPreference(nowTabs, nowSize);
    });

    fileMeta.appendChild(toolbar);
}

function updateAllToolbars() {
    let raw = localStorage.getItem(INDENT_STORAGE_KEY);
    let cfg;
    try { cfg = JSON.parse(raw); } catch(e) { cfg = null; }
    let useTabs = cfg?.useTabs ?? false;
    let size = cfg?.size ?? 4;

    document.querySelectorAll(".indent-toolbar").forEach(toolbar => {
        const modeSelect = toolbar.querySelector(".indent-mode-select");
        const sizeSelect = toolbar.querySelector(".indent-size-select");
        modeSelect.value = useTabs ? "tabs" : "spaces";
        sizeSelect.value = size;
        sizeSelect.style.display = useTabs ? "none" : "";
    });
}

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

    addIndentToolbar(template.querySelector("div.file-meta"));
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
    let keyCode = event.keyCode || event.which;
    let indent = getIndentString();

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
		var addedChars = 0;
		for (var i = 0; i < selectedLines.length; i++)
		{
		    lines[selectedLines[i]] = indent + lines[selectedLines[i]];
		    addedChars += indent.length;
		}

		this.value = lines.join("\n");
		this.selectionStart = start + indent.length;
		this.selectionEnd = end + addedChars;
    } else if (keyCode == 13) {
		event.preventDefault();

		var start = this.selectionStart;
		var end = this.selectionEnd;
        var v = this.value;

        // Find the current line's content (backwards from cursor)
        var lineStart = start - 1;
        while (lineStart >= 0 && v[lineStart] !== "\n") lineStart--;
        lineStart++;
        var currentLine = v.slice(lineStart, start);

        // Count leading whitespace characters (spaces or tabs)
        var leadingWhitespace = "";
        for (var i = 0; i < currentLine.length; i++) {
            if (currentLine[i] === " " || currentLine[i] === "\t") {
                leadingWhitespace += currentLine[i];
            } else {
                break;
            }
        }

        var insertion = "\n" + leadingWhitespace;
        this.value = v.slice(0, start) + insertion + v.slice(end);
        this.selectionStart = start + insertion.length;
        this.selectionEnd = start + insertion.length;
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

    let fileMetas = document.querySelectorAll('section.file-part div.file-meta');
    for (let i = 0; i < fileMetas.length; i++) {
        addIndentToolbar(fileMetas[i]);
    }
    updateAllToolbars();

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
