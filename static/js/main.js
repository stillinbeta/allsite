var sample = [
  {
    city: "TLV",
    total_price: '$1444',
    result_lines: [
    {
      name: 'liz',
      price: '$1444'
    },
    {
      name: 'idan',
      price: '$0'
    }
    ]
  },
  {
    city: "BOS",
    total_price: '$2000',
    result_lines: [
    {
      name: 'liz',
      price: '$0'
    },
    {
      name: 'idan',
      price: '$2000'
    }
    ]
  },
  {
    city: "NYC",
    total_price: '$1900',
    result_lines: [
    {
      name: 'liz',
      price: '$300'
    },
    {
      name: 'idan',
      price: '$1600'
    }
    ]
  }
]


$(function() {
  member_count = 0;
  city_count = 0;
  var member_template = Handlebars.compile($('#member').html());
  var extra_city_template = Handlebars.compile($('#extra-city').html());
  var result_template = Handlebars.compile($('#result').html());
  var error_template = Handlebars.compile($('#error').html());

  function add_member() {
    $('#members').append(member_template({id: member_count}));
    member_count++;
  }

  function add_city() {
    $('#extra-cities').append(extra_city_template({id: city_count}));
    city_count++;
  }

  function collect_data() {
    var members = [];
    for(var i = 0; i < member_count; i++) {
      var name = $('#member-' + i  + '-name').val();
      var airport = $('#member-' + i  + '-airport').val();
      if (name !== "" && airport !== "") {
        members.push({
          name: name,
          airport: airport
        });
      }
    }
    var cities = []
    for(var i = 0; i < city_count; i++) {
      var city = $('#extra-city-' + i).val();
      if (city !== "") {
        cities.push(city);
      }
    }
    var start_date = $('#start').val();
    var end_date = $('#end').val();

    return {
      members: members,
      cities: cities,
      start_date: start_date,
      end_date: end_date
    };
  }


  $('#add-member').click(add_member);
  $('#add-city').click(add_city);
  add_member();
  add_member();

  $('#search').click(function() {
    data = collect_data()
    console.debug(data)
    $.ajax({url: '/search',
            data: JSON.stringify(data),
            type: 'POST',
            dataType: 'json'})
      .done(function(data) {
        console.debug(data);
        $('#results').html(result_template(data));
      })
      .fail(function(data) {
        $('#results').html(error_template(data));
      })
  });
});
