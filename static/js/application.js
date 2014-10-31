window.Allsite = Ember.Application.create();

Todos.ApplicationAdapter = DS.FixtureAdapter.extend();

Allsite.Router.map(function() {
      this.resource('allsite', { path: '/' });
});
