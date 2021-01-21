#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.DevelopmentConfig')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database
# [DONE]
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String())
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(),default='')
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500), default='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60')
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(), default='')
    shows = db.relationship('Show',backref='venue', lazy=True, cascade='save-update,delete')

    def __repr__(self):
      return f'<Venue name:{self.name} genres:{self.genres} city:{self.city} address:{self.address}' \
             f'state:{self.state} phone{self.phone} fascebook:{self.facebook_link}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # [DONE]
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), default='https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80')
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(),default='')
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(), default='')
    shows = db.relationship('Show', backref='artist', lazy=True, cascade='save-update,delete')

    def __repr__(self):
      return f'<Artist name:{self.name} genres:{self.genres} city:{self.city} ' \
             f'state:{self.state} phone{self.phone} fascebook:{self.facebook_link}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # [DONE]


class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
  start_date = db.Column(db.DateTime())

  def __repr__(self):
    return f'<SHOW VENUE:{self.venue_id}, ARTIST:{self.artist_id}, DATE:{self.start_date}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# [DONE]
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helper Functions.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  venues_data = []
  distinct_cities = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  venue_tuples = Venue.query.all()
  for city in distinct_cities:
    city_dict = {
      "city":city[0],
      "state":city[1],
      "venues":[]
    }
    for venue in venue_tuples:
      if(venue.city == city[0]):
        upcoming_shows = [show for show in venue.shows if show.start_date>datetime.now() ]
        venue_dict = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows),
        }
        city_dict['venues'].append(venue_dict)

    venues_data.append(city_dict)
  return render_template('pages/venues.html', areas=venues_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  filtered_venues = Venue.query.filter(Venue.name.ilike('%'+request.form['search_term']+'%')).all()
  search_result = {
    "count":len(filtered_venues),
    "data":[]
  }
  for venue in filtered_venues:
    upcoming_shows = [show for show in venue.shows if show.start_date>datetime.now()]
    search_result['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(upcoming_shows),
    })

  return render_template('pages/search_venues.html', results=search_result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  target_venue = Venue.query.get(venue_id)
  # render venue data only if venue exsists
  if(target_venue != None):
    past_shows = []
    upcoming_shows = []
    show_data = {}
    for show in target_venue.shows:
      show_data = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_date
      }
      if show.start_date > datetime.now():
        upcoming_shows.append(show_data)
      else:
        past_shows.append(show_data)
      #  debug
      print(show_data['start_time'])
    target_venue_data = {
      "id": target_venue.id,
      "name": target_venue.name,
      "genres": target_venue.genres.split(','),
      "address": target_venue.address,
      "city": target_venue.city,
      "state": target_venue.state,
      "phone": target_venue.phone,
      "website": None if target_venue.website_link == '' else target_venue.website,
      "facebook_link": target_venue.facebook_link,
      "seeking_talent": target_venue.seeking_talent,
      "seeking_description": target_venue.seeking_description,
      "image_link": target_venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_venue.html', venue=target_venue_data)
  # if venue doesn't exist in the database render home page and show corresponding notifications
  else:
    flash('The Venue with id:'+str(venue_id)+' Doesnot Exist')
    return render_template('pages/home.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # [DONE]
  try:
    genres = request.form.getlist('genres')
    genres = ','.join(genres)
    # Debug
    print(genres)

    new_venue = Venue(name=request.form['name'], city=request.form['city'],
                        state=request.form['state'], phone=request.form['phone'],
                        address=request.form['address'],
                        genres=genres,
                        facebook_link=request.form['facebook_link'])

    # Debug
    print(new_venue)

    db.session.add(new_venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # [DONE]
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    target_venue_record = Venue.query.filter_by(id=venue_id).first()
    db.session.delete(target_venue_record)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists_tuples = Artist.query.all()
  artists_data = []
  for artist in artists_tuples:
    artists_data.append({
      "id":artist.id,
      "name":artist.name
    })
  return render_template('pages/artists.html', artists=artists_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  filtered_artists = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
  search_result = {
    "count": len(filtered_artists),
    "data": []
  }
  for artist in filtered_artists:
    upcoming_shows = [show for show in artist.shows if show.start_date > datetime.now()]
    search_result['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcoming_shows),
    })
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=search_result, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  target_artist = Artist.query.get(artist_id)
  # render venue data only if venue exsists
  if (target_artist != None):
    past_shows = []
    upcoming_shows = []
    show_data = {}
    for show in target_artist.shows:
      show_data = {
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_date
      }
      if show.start_date > datetime.now():
        upcoming_shows.append(show_data)
      else:
        past_shows.append(show_data)
      #  debug
      print(show_data['start_time'])
    target_artist_data = {
      "id": target_artist.id,
      "name": target_artist.name,
      "genres": target_artist.genres.split(','),
      "city": target_artist.city,
      "state": target_artist.state,
      "phone": target_artist.phone,
      "website": None if target_artist.website_link == '' else target_artist.website,
      "facebook_link": target_artist.facebook_link,
      "seeking_venue": target_artist.seeking_venue,
      "seeking_description": target_artist.seeking_description,
      "image_link": target_artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=target_artist_data)
  # if venue doesn't exist in the database render home page and show corresponding notifications
  else:
    flash('The Artist with id:' + str(artist_id) + ' Doesnot Exist')
    return render_template('pages/home.html')


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_record = Artist.query.get(artist_id)
  if artist_record:
    artist_data={
      "id": artist_record.id,
      "name": artist_record.name,
      "genres": artist_record.genres.split(','),
      "city": artist_record.city,
      "state": artist_record.state,
      "phone":artist_record.phone,
      "website": artist_record.website_link,
      "facebook_link": artist_record.facebook_link,
      "seeking_venue": artist_record.seeking_venue,
      "seeking_description": artist_record.seeking_description,
      "image_link": artist_record.image_link
    }
    form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist_data)
  else:
    flash('The artist with id ' + str(artist_id)+' doesnt exist')
    return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    record = Artist.query.get(artist_id)

    record.name = request.form['name']
    record.city = request.form['city']
    record.state = request.form['state']
    record.phone = request.form['phone']
    record.genres = ','.join(request.form.getlist('genres'))
    record.facebook_link = request.form ['facebook_link']

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()


  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_record = Venue.query.get(venue_id)
  if venue_record:
    form = VenueForm()
    venue={
      "id": venue_record.id,
      "name": venue_record.name,
      "genres": venue_record.genres.split(','),
      "address":venue_record.address,
      "city": venue_record.city,
      "state": venue_record.state,
      "phone":venue_record.phone,
      "website": venue_record.website_link,
      "facebook_link": venue_record.facebook_link,
      "seeking_talent": venue_record.seeking_talent,
      "seeking_description": venue_record.seeking_description,
      "image_link": venue_record.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    flash('The venue with id ' + str(venue_id)+' doesnt exist')
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    record = Venue.query.get(venue_id)

    record.name = request.form['name']
    record.city = request.form['city']
    record.state = request.form['state']
    record.address = request.form['address']
    record.phone = request.form['phone']
    record.genres = ','.join(request.form.getlist('genres'))
    record.facebook_link = request.form ['facebook_link']

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # [DONE]
  error = False
  try:
    artist_attributes = request.get_json()
    new_artist = Artist(name=artist_attributes['name'], city=artist_attributes['city'],
                        state=artist_attributes['state'], phone=artist_attributes['phone'],
                        genres=artist_attributes['genres'],
                        facebook_link=artist_attributes['facebook_link'])

    # Debug
    print(new_artist)


    db.session.add(new_artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.get_json()['name'] + ' was successfully listed!')

  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # [DONE]
    error = True
    flash('An error occurred. Artist ' + artist_attributes.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    return jsonify({'status' : 'success'})
  else:
    return jsonify({'status' : 'failed'})


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  show_tuples = Show.query.all()
  shows_data = []
  for show in show_tuples:
    shows_data.append(
      {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_date
      }
    )
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=shows_data)


# create show
# ---------------------------------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # [DONE]
  try:
    new_show = Show(venue_id=request.form['venue_id'], artist_id=request.form['artist_id'],
                    start_date=request.form['start_time'])
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # [DONE]
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
