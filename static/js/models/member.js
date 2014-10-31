Allsite.Member = DS.Model.extend({
    name: DS.attr('string'),
    airport: DS.attr('string')
});

Allsite.Member.FIXTURES = [
    {
        name: "liz",
        airport: "BOS"
    },
    {
        name: "idan",
        airport: "TLV"
    },
    {
        name: "dane",
        airport: "SFO"
    }
]
