var options = "";
const THIS_YEAR = (new Date()).getFullYear();
for (var i = 2014; i <= 2019; i++) {
    if (i === THIS_YEAR) options += '<option selected="selected">' + i + '</option>';
    else options += "<option>" + i + "</option>";
}
document.getElementById("yearList").innerHTML = options;

const degreeList = new Set();
const degreeCodes = {};
let fdd = false;
$.ajax({
    url: 'degree/all',
    success: function (data) {
        let degreeDicts = [];
        for (i in data.response) {
            degreeDicts.push({name: data.response[i].title});
            degreeList.add(data.response[i].title);
            degreeCodes[data.response[i].title] = data.response[i].code;
        }
        $('.typeahead').typeahead({source: degreeDicts});
    }
});
let degreeInputs = $('input.typeahead');
degreeInputs.popover({
    trigger: 'manual',
    placement: 'bottom',
    html: true,
    content: '<div class="degreeWrongPopover">Please choose a degree from the list.</div>'
});
$('#fdd-button').click(function (e) {
    e.preventDefault();
    if (fdd) {
        $(this).text('Double Degree');
    } else {
        $(this).text('Single Degree')
    }
    $('#fdd-row').toggle();
    fdd = !fdd;
});
$('#planform').submit(function (e) {
    const fddField = $(degreeInputs[1]);
    for (let i = 0; i < degreeInputs.length; i++) {
        if (!(i === 0 || fdd)) continue;
        const field = $(degreeInputs[i]);
        if (!degreeList.has(field.val())) {
            e.preventDefault();
            field.popover('show');
            errorPopoverSetup(field);
        }
        $($('input.degree-code')[i]).val(degreeCodes[field.val()]);
    }
    if (fdd && fddField.val() === $(degreeInputs[0]).val()) {
        e.preventDefault();
        fddField.popover('show');
        const popover = $(fddField.data('bs.popover').tip);
        popover.find('.degreeWrongPopover').text('You cannot add two of the same degree.');
        errorPopoverSetup(fddField);
    }
    new CookieStore().clearCode();
});

function errorPopoverSetup(source) {
    popover = $(source.data('bs.popover').tip);
    popover.addClass('popover-error');
    popover.click(function () {
        source.popover('hide')
    });
    popover.css('cursor', 'pointer');
    source.keydown(function () {
        source.popover('hide')
    });
}
