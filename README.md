# Partyspace New Technology Testing Repo
- Pyramid framework
- Mustache templates to allow sharing with client side JS
  - Requires a custom renderer
  - Add back in helper methods and free objects
  - Will need caching and minification for deployment
- MongoDb for flexible document storage
  - Basically replaces the need for an ORM
  - Uses a SON transform to convert records to python objects automatically
  - Objects have a save method that can be used to flush their Mongo dictionary back to the database