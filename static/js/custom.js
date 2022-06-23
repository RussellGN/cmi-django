function clickNext(obj) {
	obj.nextElementSibling.click();
}
function passNameAndURL(name, deleteURL) {
	document.getElementById("removeLabel").innerHTML = "Remove " + name;
	document.getElementById("removeLink").href = deleteURL
}


