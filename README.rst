OnBot
=====
| I originally designed this bot to be a funny joke for my friends. Its purpose was to reduce the amount of times
  I would see the message 'who's on?' from someone. It does have that functionality now and will respond with a helpful,
  although slightly rude, message informing the asker who is on and what they are doing. Although the bots main purpose
  is still this, my friends and I have been able to come up with additional functionality.
|  
| Added the ability for my friend to check the status of his car that he ordered. Uses a GET request to fetch the status
  then displays in a simple manner.
|
| I built a `NAS <https://en.wikipedia.org/wiki/Network-attached_storage>`_ that runs `Unraid <https://unraid.net/>`_ \
  which I use to store files and run dockers or VMs. I use an application called `Plex <https://www.plex.tv/>`_ to host movies that I own or
  which are part of the `public domain <https://en.wikipedia.org/wiki/List_of_films_in_the_public_domain_in_the_United_States>`_.
  I also use `Radarr <https://radarr.video/>`_ and `Sonarr <https://sonarr.tv/>`_ to monitor and manage my movie and 
  series collections respectively. Utilizing `IMDbpy <https://imdbpy.github.io/>`_ anyone is able to search and request
  movies or shows all from within discord. They are able to search with IMDb IDs directly or by name and then choose the
  correct one. Their choice will then be sent to either Radarr or Sonarr to be monitored. I also store logs of each request
  and who made them using `MariaDB <https://mariadb.org/>`_ which I host on my server.

Commands
--------
| Any use of both words ``who`` and ``on`` in the same message to see who is on
|
| ``whip`` gets the status of the car
|
| The bot is also able to add requests for my Plex server using:
| ``request movie <IMDb ID or keyword>`` to make a movie request
| ``request series <keyword>`` to make a series request

Acknowledgements
----------------
| This project was built using the `Discord Python API <https://discordpy.readthedocs.io/en/latest/api.html#member>`_ 
  and influenced by `this <https://www.youtube.com/watch?v=SPTfmiYiuok>`_ video from `freeCodeCamp.org <https://www.youtube.com/channel/UC8butISFwT-Wl7EV0hUK0BQ>`_ on youtube.
