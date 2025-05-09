from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datamanager.data_manager_interface import DataManagerInterface

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    movies = relationship('Movie', back_populates='user', cascade='all, delete-orphan')

class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    director = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='movies')

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_filename):
        self.engine = create_engine(f'sqlite:///{db_filename}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_all_users(self):
        with self.Session() as session:
            return session.query(User).all()

    def get_user(self, user_id):
        with self.Session() as session:
            return session.query(User).get(user_id)

    def get_user_movies(self, user_id):
        with self.Session() as session:
            user = session.query(User).get(user_id)
            return user.movies if user else []

    def add_user(self, name):
        with self.Session() as session:
            user = User(name=name)
            session.add(user)
            session.commit()

    def add_movie(self, user_id, name, director, year, rating):
        with self.Session() as session:
            movie = Movie(user_id=user_id, name=name, director=director, year=year, rating=rating)
            session.add(movie)
            session.commit()

    def delete_movie(self, movie_id):
        with self.Session() as session:
            movie = session.query(Movie).get(movie_id)
            if movie:
                session.delete(movie)
                session.commit()

    def get_movie(self, movie_id):
        with self.Session() as session:
            return session.query(Movie).get(movie_id)
        
    def update_movie(self, movie):
        with self.Session() as session:
            existing = session.query(Movie).get(movie.id)
            if existing:
                existing.name = movie.name
                existing.director = movie.director
                existing.year = movie.year
                existing.rating = movie.rating
                session.commit()

    def delete_user(self, user_id):
        with self.Session() as session:
            user = session.query(User).get(user_id)
            if user:
                session.delete(user)
                session.commit()

    def get_total_users(self):
        with self.Session() as session:
            return session.query(User).count()

    def get_total_movies(self):
        with self.Session() as session:
            return session.query(Movie).count()

    def get_top_rated_movies(self, limit=10):
        with self.Session() as session:
            results = (
                session.query(
                    Movie.name,
                    func.round(func.avg(Movie.rating), 1).label("avg_rating"),
                    func.min(Movie.year).label("year"),  # Optional: get a representative year
                    func.min(Movie.director).label("director")  # Optional: a representative director
                )
                .group_by(Movie.name)
                .order_by(func.avg(Movie.rating).desc())
                .limit(limit)
                .all()
            )
            return results
        
