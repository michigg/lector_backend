# BA_Backend
## Installation Guide
- 0. Optional: CHANGE ENVS in `docker/lector/dev.env` for Customation (e.g. change univis semester
- 1. RUN `docker-compose up -d`
- 2. OPEN Browser on `localhost:8888` for Backend API or for Graphhopper `localhost:8989` 

## Run Tests
- 1. RUN `docker-compose up -d`
- 2. RUN `docker-compose exec lector sh`
- 3. RUN `python3 manage.py tests`

