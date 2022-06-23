(function () {
	"use strict";

	/**
	 * Easy selector helper function
	 */
	const select = (el, all = false) => {
		el = el.trim();
		if (all) {
			return [...document.querySelectorAll(el)];
		} else {
			return document.querySelector(el);
		}
	};

	/**
	 * Scroll with ofset on page load with hash links in the url
	 */
	window.addEventListener("load", () => {
		if (window.location.hash) {
			if (select(window.location.hash)) {
				scrollto(window.location.hash);
			}
		}
	});
})();
