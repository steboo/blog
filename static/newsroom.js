function slugify(text) {
    return text.toLowerCase().replace(/[!*'();:@\$,\/#\[\].]/g, '').replace(/\s+/g, '-').replace(/--+/g, '-').replace(/^-+/, '').replace(/-+$/, '');
}

var slugEl = document.getElementById('slug');
document.getElementById('headline').addEventListener('keyup', function (e) {
    slugEl.value = slugify(e.target.value);
});
