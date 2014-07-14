function getLanguageFromBrowser() {
    var lang = navigator.language || navigator.userLanguage;
    if (lang.indexOf("de") >= 0) {
        return "german"
    }
    return "english"
}
