from flask import Flask, render_template, request, redirect, url_for, abort, flash
from datamanager.sqlite_data_manager import SQLiteDataManager
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages
data_manager = SQLiteDataManager('moviweb.db')
omdb_api_key = "d8406326"


@app.route('/')
def index():
    try:
        total_users = data_manager.get_total_users()
        total_movies = data_manager.get_total_movies()
        top_movies = data_manager.get_top_rated_movies()
    except Exception as e:
        app.logger.error(f"Error loading index: {e}")
        abort(500)
    return render_template('index.html', total_users=total_users, total_movies=total_movies, top_movies=top_movies)


@app.route('/users')
def list_users():
    try:
        users = data_manager.get_all_users()
    except Exception as e:
        app.logger.error(f"Error loading users: {e}")
        abort(500)
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = data_manager.get_user(user_id)
    if not user:
        abort(404, description="User not found")
    try:
        movies = data_manager.get_user_movies(user_id)
    except Exception as e:
        app.logger.error(f"Error fetching movies for user {user_id}: {e}")
        abort(500)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash("Name is required", "danger")
            return redirect(url_for('add_user'))
        try:
            data_manager.add_user(name)
            flash("User added successfully", "success")
            return redirect(url_for('list_users'))
        except Exception as e:
            app.logger.error(f"Failed to add user: {e}")
            abort(500)
    return render_template('forms.html', form_type='add_user')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        name = request.form['name']
        director = ""
        year = 0
        rating = 0.0

        try:
            response = requests.get("http://www.omdbapi.com/", params={
                "t": name,
                "apikey": omdb_api_key
            }).json()
        except requests.RequestException as e:
            app.logger.error(f"OMDb API request failed: {e}")
            return "Failed to fetch movie data.", 500

        if response.get("Response") == "True":
            name = response.get("Title", name)
            director = response.get("Director", director)
            try:
                year = int(response.get("Year", "0").split("–")[0])
            except ValueError:
                year = 0
            try:
                rating = float(response.get("imdbRating", "0"))
            except ValueError:
                rating = 0.0

        try:
            data_manager.add_movie(user_id, name, director, year, rating)
            flash("Movie added successfully", "success")
        except Exception as e:
            app.logger.error(f"Failed to add movie for user {user_id}: {e}")
            abort(500)

        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('forms.html', form_type='add_movie', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    movie = data_manager.get_movie(movie_id)
    if not movie:
        abort(404, description="Movie not found")
    if request.method == 'POST':
        movie.name = request.form['name']
        movie.director = request.form['director']
        try:
            movie.year = int(request.form['year'])
        except ValueError:
            movie.year = 0
        try:
            movie.rating = float(request.form['rating'])
        except ValueError:
            movie.rating = 0.0
        try:
            data_manager.update_movie(movie)
            flash("Movie updated successfully", "success")
        except Exception as e:
            app.logger.error(f"Error updating movie {movie_id}: {e}")
            abort(500)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('forms.html', form_type='update_movie', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    try:
        data_manager.delete_movie(movie_id)
        flash("Movie deleted", "info")
    except Exception as e:
        app.logger.error(f"Failed to delete movie {movie_id}: {e}")
        abort(500)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        data_manager.delete_user(user_id)
        flash("User deleted", "info")
    except Exception as e:
        app.logger.error(f"Failed to delete user {user_id}: {e}")
        abort(500)
    return redirect(url_for('list_users'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=str(e)), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html', error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True)
