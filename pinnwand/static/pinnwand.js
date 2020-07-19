window.addEventListener("load", function(event) {
    var storage = window.localStorage;
    var colorSchemeButton = document.getElementById("toggle-color-scheme");

    if(storage.getItem("other-color") == "true") {
        var html = document.querySelector("html");
        html.classList.toggle("other-color");
    }

    if(colorSchemeButton != null) {
        colorSchemeButton.addEventListener("click", function(event) {
            if(storage.getItem("other-color") == "true") {
                storage.setItem("other-color", "false");
            } else {
                storage.setItem("other-color", "true");
            }

            var html = document.querySelector("html");
            html.classList.toggle("other-color");
        });
    }

    var bar = document.querySelector("section.paste-submit");

    if(!bar) {
        // Not the new paste page.
        var wordWrapButton = document.getElementById("toggle-word-wrap");
        if(wordWrapButton != null) {
            wordWrapButton.addEventListener("click", function(event) {
                var codeBlocks = document.querySelectorAll("div.code");
                for(var i = 0; i < codeBlocks.length; i++) {
                    codeBlocks[i].classList.toggle("no-word-wrap");
                }
            });
        }

        var copyButtons = document.querySelectorAll("button.copy-button");

        for(var i = 0; i < copyButtons.length; i++) {
            var copyButton = copyButtons[i];

            copyButton.addEventListener("click", function(event) {
                event.preventDefault();

                var textarea = event.target.parentNode.parentNode.querySelector("textarea.copy-area");
                var listener = (function(event) {
                    event.preventDefault();
                    event.clipboardData.setData("text/plain", textarea.value);
                });

                document.addEventListener('copy', listener);
                document.execCommand('copy');
                document.removeEventListener('copy', listener);
            });
        };

        return false;
    }

    var removes = document.querySelectorAll("button.remove");

    for(var i = 0; i < removes.length; i++) {
        var remove = removes[i];

        remove.addEventListener("click", function(event) {
            event.preventDefault();

            var section = event.target.parentNode.parentNode;

            document.querySelector("main.page-create").removeChild(section);
        });
    };

    var but = document.createElement("button");

    but.innerText = "Add another file.";
    but.className = "add";
    but.href = "#";

    but.addEventListener("click", function(event) {
        event.preventDefault();

        new_file_add();
    })

    bar.appendChild(but);
});

function new_file_add() {
    var template = document.querySelector("section.file-template").cloneNode(true);
    template.className = "file-part file-extra";
    template.querySelector("button.remove").addEventListener("click", function(event) {
        event.preventDefault();

        var section = event.target.parentNode.parentNode;

        document.querySelector("main.page-create").removeChild(section);
    });

    document.querySelector("main.page-create").insertBefore(
        template,
        document.querySelector("section.paste-submit")
    );
}
