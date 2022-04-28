# GraphQL Timeclock in Django

## How to install
Clone respository
```
git clone https://github.com/tds455/GraphQL-API.git
cd GraphQL-API
```

Create and activate virtual environment
```
python3 -m venv venv
source venv/Scripts/activate
```

Install dependencies
```
pip install -r requirements.txt
```

Open project folder and perform migrations
```
cd timeclock
python manage.py makemigrations api
python manage.py migrate
```

Start development server
```
python manage.py runserver
```

Navigate to 127.0.0.1:8000/graphql in browser or client of choice.


## Mutations

The following mutations are available.

### createUser
Create a mutation in the following format, entering a username, password and email in order to create a new user. <br>
If a username already in use is provided, an error will be returned

```
mutation {
	createUser(username:"username", password:"password", email:"email") {
	user {
    id
    username
    email
  }
  }
}
```

### obtainToken
Provide the username and password for an existing account and retrieve a JWT access token.
```
mutation {
	obtainToken(username:"", password:"") {
    token
  }
}
```

### clockIn
- Requires JWT access token <br>
Clock in the currently authenticated user.  If the user is already clocked in an error will occur.
```
mutation {
	clockIn {
		sheet {
			active
		}
	}
}
```

### clockOut
- Requires JWT access token <br>
Clock out the currently authenticated user.  If the user is not currently clocked in an error will occur.
```
mutation {
	clockOut {
		sheet {
			active
		}
	}
}
```

## Queries

The following queries are available.

### me
- Requires JWT access token <br>
Returns the currently authenticated user
```
query {
  me {
    username
  }
}
```

### currentClock
- Requires JWT access token <br>
Returns info on the currently running clock.  If the user is not currently clocked in "null" will be returned
```
query {
	currentClock {
		id
		active
		clockedIn
		clockedOut
	}
}
```

### clockedHours
- Requires JWT access token <br>
Returns the hours worked for today, this week and this month
```
query {
	clockedHours {
		today
		currentWeek
		currentMonth
	}
}
```

## Notes
This was my first project working with graphQL.  In some places best practices may not be followed and I learnt a lot on the go, so I'm especially grateful for any feedback!
