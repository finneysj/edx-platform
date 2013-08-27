// Fetch data about badges via JSONP, so that the progress page does
// not fail to load if the badge service is failing.

$(document).ready(function() {

  badges_element = $("#badges");

  badges_element.css("position", "relative");
  badges_element.css("text-align", "center");

  var get_badges = function() {
    var url = badge_service_url + "v1/badges/?format=jsonp&email=" + email + "&badgeclass__issuer__course=" + course_id + "&callback=?";
    return $.getJSON(url, function(data){});
  };

  var get_badgeclasses = function() {
    var url = badge_service_url + "v1/badgeclasses/?format=jsonp&issuer__course=" + course_id + "&callback=?";
    return $.getJSON(url, function(data){});
  };

  var render_badges = function() {
    //I'd like to terminate this process after a certain time, to prevent hanging when get_badges and
    //get_badgeclasses are pinging the wrong URL. Not sure whether this is possible for a when().
    $.when(get_badges(), get_badgeclasses()).done(function(badges_data, badgeclasses_data) {
      var badges_list = badges_data[0].results;
      var badgeclasses_list = badgeclasses_data[0].results;

      if (badgeclasses_list.length !== 0) {

        for (var j=0; j<badgeclasses_list.length; j++) {
          var badgeclass = badgeclasses_list[j];
          badgeclass['is_earned'] = is_earned(badgeclass, badges_list);
        }

        var data = {
          "badgeclasses": badgeclasses_list,
        };

        //Render the mustache template in `badges_Element` using the information in `data`.
        //Replace the html in `badges_element` with the new rendered html.
        var template = badges_element.html();
        var badges_html = Mustache.to_html(template, data);
        badges_element.html(badges_html);

        //Unhide the div. (It was hidden to hide the unrendered template)
        badges_element.css('display', 'inline');
      }
    });
  };

  //Determine whether a badgeclass has been earned -- whether it is in badges_list. Return true or false.
  var is_earned = function(badgeclass, badges_list) {
    for (var i=0; i<badges_list.length; i++) {
      if (badges_list[i].badge.indexOf(badgeclass.edx_href) != -1) {
        return true;
      }
    }
    return false;
  };

  render_badges();

});
