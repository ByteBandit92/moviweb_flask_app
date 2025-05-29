# 🎬 MoviWeb - A Flask Movie Tracker

MoviWeb is a lightweight web app built with Flask and SQLite that allows users to:
- Create user profiles
- Add and update movies using the OMDb API
- View top-rated movies
- Manage user/movie data

---

## 🚀 Features

- User management (add/delete users)
- Movie management per user (add/update/delete)
- Automatically fetches movie data from [OMDb API](https://www.omdbapi.com/)
- Overview dashboard: total users, total movies, top 10 movies by rating

---

## ⚙️ Installation

### 1. Clone the repository

- bash
- git clone https://github.com/ByteBandit92/moviweb.git
- cd moviweb

### 2. Create and activate a virtual environment
- bash
- Kopieren
- Bearbeiten
- python -m venv venv
- source venv/bin/activate  # On Windows use `venv\Scripts\activate`

### 3. Install dependencies
- pip install -r requirements.txt


### 4. Set up environment variables
- You can optionally use a .env file to store your OMDb API key:
- OMDB_API_KEY=your_api_key_here
- SECRET_KEY=SOMEKEY

### 5. Run App
- flask run