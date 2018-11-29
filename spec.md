# Music Collector - Udacity Catalogue Project
##### Robin Edmunds 2018

## Description
A web application for cataloguing and sharing personal music collections held on physical media, categorised by User.

New users will have the option to create an app managed user profile, or use Google's or Facebook's OAuth2 to login.

The application will provide API endpoints to allow for the integration of Music Collector data in third-party applications.

## Database Design

### Users
- id
- auth_type (google, facebook, native)
- first_name
- last_name
- email
- password_hash (sha256)
- password_salt (8 random alpha-numeric chars)
- auth_token
- description (of collection)
- picture

### Media
- id
- user_id (foreign key)
- type (album, lp, single)
- genre
- medium (vinyl, cassette, cd, etc)
- artist
- title

## Pages

### READ
1. Landing page (List of user collections on left, 10 latest entries right)
1. Show collection page (Show list of collection entries)
1. Show entry page (details of entry, media table info)

### POST/PUT/DELETE
1. Login page with google and facebook oauth
1. Registration page (for creating native accounts)
1. Edit collection description page (collection name the user's name)
1. Delete collection with confirmation
1. Add entry page
1. Edit entry page
1. Delete entry page with confirmation

### API - JSON
1. Show media item detail (public)
1. List collections with description (public) - not essential
1. List collection items (public) - not essential
