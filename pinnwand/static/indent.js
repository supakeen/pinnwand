/// There should be a better way to handle the lexer
/// I think :)


function make_indent(event) {

	var selector = document.querySelector("div.file-meta select[name='lexer']") // select the `select` under the file-meta div
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
		this.value = val.substring(0, start) + " ".repeat(4) + val.substring(end);
		
		// put caret at right position again
		this.selectionStart =
		this.selectionEnd = start + 4; // replace tab with 4 space, should make this configurable ?
	} 
	else if (keyCode == 13) { // check if an `enter` is pressed
		setTimeout(function(that) {
			var data = that.value;

			// the idea here is to trim the text in the `textarea`
			// trim it and split it by newlines and then
			// get the last line and check the number of spaces in the line
			// before a nonspace character appear
			text_lines = data.trim().split("\n")
			last_line = text_lines[text_lines.length-1]
			var indent = 0;
			for(i=0; i < last_line.length; i++) {
				if ( last_line[i] == ' ' ) indent++;
				else break;
			}
			start = that.selectionStart + indent;
			end = that.selectionEnd + indent;
			that.value = data.slice(0, start) + " ".repeat(indent) + data.slice(end)
		}, 0.01, this);
	}
}

window.onload = function() {
	/*
	var selector = document.querySelector("div.file-meta select[name='lexer']") // select the `select` under the file-meta div
	var lexer = selector.options[selector.selectedIndex].text

	console.log("lexer", lexer)
	// only indenting for python at the moment
	if ( lexer && lexer.toLowerCase().indexOf("python") == 0 ) {
		var textarea = document.querySelector('textarea');
		textarea.onkeydown = make_indent;
	}
	*/
		var textarea = document.querySelector('textarea');
		textarea.onkeydown = make_indent;
}
