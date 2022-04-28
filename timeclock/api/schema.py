from multiprocessing import context
import graphene
from graphene_django import DjangoObjectType
from graphene_django.utils.testing import GraphQLTestCase
from django.db import IntegrityError
from .models import User, TimeClock, TimeSheet
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from graphql_jwt import ObtainJSONWebToken
import datetime


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)

class ClockType(DjangoObjectType):
    class Meta:
        model = TimeSheet

class ClockedHours(graphene.ObjectType):
    today = graphene.Int()
    currentWeek = graphene.Int()
    currentMonth = graphene.Int()

class UserInput(graphene.InputObjectType):
    username = graphene.String()
    password = graphene.String()
    email = graphene.String()

class Query(graphene.ObjectType):
    # Define available GraphQL queries
    me = graphene.Field(UserType)
    currentClock = graphene.Field(ClockType)
    clockedHours = graphene.Field(ClockedHours) 

    @login_required
    # Return the currently authenticated user
    def resolve_me(self, info):
        user = info.context.user
        return user

    @login_required
    # Show current clock status, including the date and time the user clocked in
    def resolve_currentClock(self, info):
        user = info.context.user
        clock = TimeSheet.objects.get(user=user)
        if clock.active == False:
            # If the user is not currently clocked in, return null
            pass
        else:
            return clock

    @login_required
    # Return the amount of hours the user has clocked for today, this week and this month
    def resolve_clockedHours(self, info):
        # Get the current date to be used in Django Object queries
        day = datetime.datetime.now().date()
        user = info.context.user

        # Initialise values
        today = 0
        currentWeek = 0
        currentMonth = 0
        
        # Filter TimeClock model for entries matching today's date and the currently authenticated user
        todayClock = TimeClock.objects.filter(user=user, date__date=day)
        # Get today's hours
        # Iterate through records, calling the returnhour method and adding the reponse to today variable
        for item in todayClock:
            hours = item.returnhours()
            today += hours

        # GET THIS WEEKS HOURS
        # Find date for start of the week (Monday)
        weekstart = day - datetime.timedelta(days=day.weekday())
        # Use timedelta(hours=24) to also include results from the current day, otherwise range is inclusive
        week = TimeClock.objects.filter(user=user, date__range=[weekstart,day+datetime.timedelta(hours=24)])
        # Iterate through records, calling returnhour and adding hours to currentWeek variable
        for item in week:
            hours = item.returnhours()
            currentWeek += hours

        # GET THIS MONTHS HOURS
        # Create new datetime object set to the beginning of current month.
        monthstart = datetime.datetime(day.year, day.month, 1)
        month = TimeClock.objects.filter(user=user, date__range=[monthstart,day+datetime.timedelta(hours=24)])
        # Iterate through records, calling returnhour and adding hours to currentMonth variable
        for item in month:
            hours = item.returnhours()
            currentMonth += hours

        # Return values
        ClockedHours.today = today
        ClockedHours.currentWeek = currentWeek
        ClockedHours.currentMonth = currentMonth
        return ClockedHours

class CreateUser(graphene.Mutation):
    # Set required arguments for creating a user
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(UserType)

    @staticmethod
    def mutate(root, info, username, password, email):
        # Use try to validate input and ensure the username provided is unique
        try:
            newuser = User.objects.create_user(username=username, email=email)
            newuser.set_password(password)
            newuser.save()
            # Create timesheet for new user
            sheet = TimeSheet.objects.create(user=newuser, active=False)
            sheet.save()
            # Create initial TimeClock for new user
            clock = TimeClock.objects.create(user=newuser)
            clock.save()
        # Return error if username is already in use
        except IntegrityError:
            raise GraphQLError("That user already exists")

        # Return user details
        return CreateUser(user=newuser)

class clockIn(graphene.Mutation):
    sheet = graphene.Field(ClockType)

    @login_required
    @staticmethod
    def mutate(root, info):
        user = info.context.user
        # Retrieve current user's timesheet
        sheet = TimeSheet.objects.get(user=user)
        # Check if user is already clocked in, and return an error if so.
        if sheet.active == True:
            raise GraphQLError("You are already clocked in!")
        else:
            # Call the clockin method to update timesheet with currenttime and clock user in
            sheet.clockin()
            return clockIn(sheet=sheet)

class clockOut(graphene.Mutation):
    sheet = graphene.Field(ClockType)  

    @login_required
    @staticmethod
    def mutate(root, info):
        # Check the current user is clocked in.  If not, return an error
        user = info.context.user
        # Retrieve current user's timesheet
        sheet = TimeSheet.objects.get(user=user)
        # Return an error if the user is not clocked in
        if sheet.active == False:
            raise GraphQLError("You are not currently clocked in!  Can not clock you out!")
        else:
            # Call the clockin method to update timesheet with currenttime and clock user out
            sheet.clockout()
            return clockOut(sheet=sheet)

# Define mutations
class Mutation(graphene.ObjectType):
    createUser = CreateUser.Field()
    obtainToken = ObtainJSONWebToken.Field()
    clockIn = clockIn.Field()
    clockOut = clockOut.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# Define tests
class TestCase(GraphQLTestCase):
    def test_clockIn(self):
        response = self.query(
            '''
            mutation {
	            clockIn {
		            sheet   {
			                active
		                    }
	                    }
                    }
            ''',
            op_name='clockIn'
        )

        # Confirm no errors on response
        self.assertResponseNoErrors(response)

    def test_clockOut(self):
        response = self.query(
            '''
            mutation {
	            clockOut {
		            sheet   {
			                active
		                    }
	                    }
                    }
            ''',
            op_name='clockOut'
        )

        # Confirm no errors on response
        self.assertResponseNoErrors(response)

    def test_clockedHours(self):
        response = self.query(
            '''
            query {
	            clockedHours {
		                    today
		                    currentWeek
		                    currentMonth
	                        }
                    }
            ''',
            op_name='clockedHours'
        )      

        # Confirm no errors on response
        self.assertResponseNoErrors(response)

