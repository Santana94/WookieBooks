## Wookie Books

### How to set up

You will need docker installed to build the application:

https://www.docker.com/

Create a `.env` file providing the following attributes:

```
secret_key=some_secre_key
algorith=HS256
sql_alchemy_database_url=sqlite:///./wookie_books.db
```

With Docker running, execute the following command in a terminal:

`docker-compose up -d --build`

Once the command is finished, open your browser and paste the 
url `http://0.0.0.0:80/docs` to check the application.

To run the tests, execute the following command:

`docker-compose exec web pytest`
