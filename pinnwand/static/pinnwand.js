window.addEventListener("load", function(event) {
    var bar = document.querySelector("section.paste-submit");

    if(!bar) {
        return false;
    }

    var removes = document.querySelectorAll("a.remove");

    for(var i = 0; i < removes.length; i++) {
        var remove = removes[i];

        remove.addEventListener("click", function(event) {
            event.preventDefault();

            var section = event.target.parentNode.parentNode;

            document.querySelector("main.page-create").removeChild(section);
        });
    };

    var but = document.createElement("a");

    but.text = "Add another file.";
    but.className = "add";
    but.href = "#";

    but.addEventListener("click", function(event) {
        event.preventDefault();

        new_file_add();
    })

    bar.appendChild(but);

    /// textarea indent
    var textarea = document.querySelector('section.file-part textarea');
    textarea.onkeydown = make_indent;

});

function new_file_add() {
    var template = document.querySelector("section.file-template").cloneNode(true);
    template.className = "file-part file-extra";

    template.querySelector("a.remove").addEventListener("click", function(event) {
        event.preventDefault();

        var section = event.target.parentNode.parentNode;

        document.querySelector("main.page-create").removeChild(section);
    });

    document.querySelector("main.page-create").insertBefore(
        template,
        document.querySelector("section.paste-submit")
    );
}


function make_indent(event) {

	//var selector = document.querySelector("div.file-meta select[name='lexer']") // select the `select` under the file-meta div
	var selector = event.target.parentNode.parentNode.querySelector("select[name='lexer']") // select the `select` under the file-meta div
	var lexer = selector.options[selector.selectedIndex].text

	// only indenting for python at the moment
	if ( ! (lexer && lexer.toLowerCase().indexOf("python") == 0) ) {
		return
	}

	var keyCode = event.keyCode || event.which;
	if (keyCode == 9) { // check if a `tab` is pressed
		event.preventDefault();
		var start = this.selectionStart;
		var end = this.selectionEnd;

		// set textarea value to: text before caret + tab + text after caret
		val = this.value;

		// replace `tab` with 4 `space`
		this.value = val.substring(0, start) + " ".repeat(4) ; //+ val.substring(start);
		
		// put caret at right position again
		//this.selectionEnd = start + 4;
		// it works even without setting the selection end,
		// which makes me uncomfotable not knowing why
	}
	else if (keyCode == 13) { // check if an `enter` is pressed
		event.preventDefault();

		// the idea here is to trim the text in the `textarea`
		// trim it and split it by newlines and then
		// get the last line and check the number of spaces in the line
		// before a nonspace character appear
		var data = this.value;
		var text_lines = data.trim().split("\n")
		var last_line = text_lines[text_lines.length-1]
		var indent = 0;
		for(i=0; i < last_line.length; i++) {
			if ( last_line[i] == ' ' ) indent++;
			else break;
		}

		var start = this.selectionStart;
		var end = this.selectionEnd;

		// match the indent of the previous line and
		// add that amount of space to the start of the new line
		this.value = data.substr(0, start) + "\n" + " ".repeat(indent); // + data.substr(start)
		this.selectionEnd += indent;

	}
}
