from sqlalchemy import select, delete, and_, or_, not_, func
from database import *

# INSERTING DATA


def add_one_car(manufacturer, model):
    with Session() as session:
        car = Car(manufacturer=manufacturer, model=model)
        session.add(car)
        session.commit()
        print(f"Added car with ID: {car.car_id}")


def add_multiple_cars(cars: list[Car]):
    with Session() as session:
        session.add_all(cars)
        session.commit()
    for car in cars:
        print(f"Car with car_id{car.car_id} has been added")

# Fetching data (scalar, scalars, session.execute)
# scalar is used to fetch one row and scalars can be used to fetch multiple cars
# session.execute is used to fetch individual columns


def get_one_car_by_manufacturer(manufacturer):
    with Session() as session:
        stmt = select(Car).where(Car.manufacturer == manufacturer)
        car = session.scalar(stmt)
        print(f"found {car.manufacturer} model {car.model}")


def get_multiple_car_by_manufacturer(manufacturer):
    with Session() as session:
        stmt = select(Car).where(Car.manufacturer == manufacturer)
        cars = session.scalars(stmt)
        for car in cars:
            print(f"found {car.manufacturer} model {car.model}")
            

def get_car_models_manufacturers():
    with Session() as session:
        stmt = select(Car.manufacturer, Car.model)
        results = session.execute(stmt).all() # This will get data in tuples
        for manufacturer, model in results:
            print(f"found {manufacturer} model {model}")
            

# This delets all the data from the database (This is the recomended because this is faster if you want to remove whole data)
def remove_all_cars():
    with Session() as session:
        stmt = delete(Car) # we can also put the where filter to delete the specific data
        session.execute(stmt)
        session.commit()
        
# Deleting the data manually one by one
def delete_all_cars():
    with Session() as session:
        stmt = select(Car)
        cars = session.scalars(stmt).all()
        for car in cars:
            session.delete(car)
        session.commit()
        
# Removing or deleting the single car ()
def remove_car(manufacturer):
    with Session() as session:
        stmt = select(Car).where(Car.manufacturer==manufacturer)
        car = session.scalar(stmt)
        if car:
            session.delete(car)
            session.commit()
            print(f"The car with manufacturer {car.manufacturer} has been removed.")
        else:
            print("No car with this manufacturer")

# Updating only one item
def update_car_model(old_model, new_model):
    with Session() as session:
        stmt = select(Car).where(Car.model == old_model)
        car = session.scalar(stmt)
        if car:
            car.model = new_model
            session.commit()
            print(f"Updated model {old_model} to {new_model}")
        else:
            print("No car with this model")
            
# Update multiple models
def update_all_car_models(manufacturer, old_model, new_model):
    with Session() as session:
        stmt = select(Car).where(Car.manufacturer==manufacturer, Car.model==old_model)
        cars = session.scalars(stmt).all()
        if cars:
            for car in cars:
                car.model = new_model
                print(f"Updated{old_model} to {new_model}")
            session.commit()
        else:
            print("No cars found")
            
            


# ---------Filtering Data----------------------

def filter_comparisions():
    with Session() as session:
        # stmt = select(Car).where(Car.manufacturer=='Toyota')
        # stmt = select(Car).where(Car.manufacturer!='Toyota')
        # stmt = select(Car).where(Car.car_id>=0)
        stmt = select(Car).where(Car.car_id>=2)
        
        cars = session.scalars(stmt).all()
        for car in cars:
            print(f"{car.car_id} {car.manufacturer}")
            
def filter_and_or_not():
    with Session() as session:
        # and: using comma (Which means inlace of 'AND' we use ',')
        # stmt = select(Car).where(Car.manufacturer == 'Toyota', Car.model=='yaris')
        
        # and: using and_
        # stmt = select(Car).where(and_(Car.manufacturer == 'Toyota', Car.model=='yaris'))
        
        # or_
        # stmt = select(Car).where(or_(Car.manufacturer == 'Toyota', Car.model=='yaris'))
        
        # not_
        # stmt = select(Car).where(not_(Car.manufacturer == 'Toyota'))
        
        # and_ and or_
        stmt = select(Car).where(or_(
            and_(Car.manufacturer=='Toyota', Car.model=='yaris'),
            and_(Car.manufacturer=='Volkswagon', Car.model=='polo')
        ))
          
        
        cars = session.scalars(stmt).all()
        for car in cars:
            print(f"{car.car_id} {car.manufacturer}")
            
            
def filter_in_like():
    with Session() as session:
        # in
        # stmt = select(Car).where(Car.manufacturer.in_(['Volkswagon', 'Toyota']))
        
        # not_ in
        # stmt = select(Car).where(Car.manufacturer.not_in(['Volkswagon', 'Toyota']))
        
        # like
        stmt = select(Car).where(Car.manufacturer.like('%wag%'))
        
        cars = session.scalars(stmt).all()
        for car in cars:
            print(f"{car.car_id} {car.manufacturer}")


def filter_bool_null():
    with Session() as session:
        # Boolean is True (Here is_sold in database is boolean so we are checking if the car is sold or not.)
        # stmt = select(Car).where(Car.is_sold.is_(True))
        
        # Boolean is False (Here we are checking if the is not sold.)
        # stmt = select(Car).where(Car.is_sold.is_(False))
        
        # Checking if the data is null
        # stmt = select(Car).where(Car.updated_at.is_(None))
        
        # Checking if the data is not null
        stmt = select(Car).where(Car.updated_at.is_not(None))
        
        cars = session.scalars(stmt).all()
        for car in cars:
            print(f"{car.car_id} {car.manufacturer}")
            
            
def filter_ordering_pagination():
    with Session() as session:
        # Ordering the data in ascending (You can also limit the result)
        # stmt = select(Car).order_by(Car.manufacturer.asc())
                
        # Ordering the data in descending (You can also limit the result)
        # stmt = select(Car).order_by(Car.manufacturer.desc())
        
        # Ordering the data in descending (You can also limit the result)
        # stmt = select(Car).order_by(Car.manufacturer.desc()).limit(2)
        
        # Pagination using the (offset)
        stmt = select(Car).order_by(Car.manufacturer.asc()).offset(3).limit(2)
        
        cars = session.scalars(stmt).all()
        for car in cars:
            print(f"{car.car_id} {car.manufacturer}")
            
            

# ------------------Relationships----------------------
# So this is the function for adding the invoice but we can also remove, find invoice
def add_invoice_for_car():
    with Session() as session:
        stmt = (select(Car)
                .where(and_(Car.manufacturer=='Volkswagon', Car.model=='polo')))
        car = session.scalar(stmt)
        if car:
            car.invoice.append(Invoice(description='Fixed brakes', amount=452.23))
            session.commit()
            print(f"Added invoice for car {car.manufacturer}")
        else:
            print("Car not found.")
            
            
# Find the invoice for car
def find_car_invoices():
    with Session() as session:
        stmt = (
            select(Car)
            .where(and_(Car.manufacturer=='Volkswagon', Car.model=='polo'))
        )
        car = session.scalar(stmt)
        if car:
            print('Invoices for car {car.manufacturer}')
            for invoice in car.invoices:
                print(f"Invoice amount:{invoice.amount} - {invoice.description}")
        else:
            print('No car found')        
            

# Delete all invoices at once
def remove_all_invoices():
    with Session() as session:
        stmt = delete(Invoice) # we can also put the where filter to delete the specific data
        session.execute(stmt)
        session.commit()
        


# -----------------Manually creating the relationships ----------------------------
# This we only do when we need to optimize the code for faster result.
# And this we also do if we don't have the relationship defined on the database.
def join_cars_invoices():
    with Session() as session:
        stmt = (
            select(Car.manufacturer, Car.model, Invoice.description, Invoice.amount)
            .join(Invoice, Invoice.car_id==Car.car_id)
        )
        results = session.execute(stmt).all()
        for manufacturer, model, description, amount in results:
            print(f"{manufacturer} {model} {description} {amount}")


# Full relation many to many example is in the database.py file (User, Car, UserCar)

def full_many_to_many_example():
    # 1 Create user associated with the car
    with Session() as session:
        # Creating new user
        new_user = User(username="David")
        session.add(new_user)
        session.commit()
        
        # Find the car
        stmt = select(Car).where(Car.model=='polo')
        car = session.scalar(stmt)
        
        if car is None:
            print('No car found')
            return
        session.add(UserCar(user=new_user, car=car))
        session.commit()
    
    # Fetch all users and display their cars
    with Session() as session:
        stmt = select(User)
        users = session.execute(stmt).scalars().all()
        for user in users:
            print(f"{user.username} owns {len(user.user_cars)} cars")
            for user_car in user.user_cars:
                print(f" - {user_car.car.manufacturer} {user_car.car.model}")
                
    # clean up
    with Session() as session:
        stmt = select(User)
        users = session.execute(stmt).scalars().all()
        for user in users:
            session.delete(user)
        session.commit()



# Aggregation functions, group by, having, subqueries, cte's, window functions, etc. are also there but I have not added here because I want to keep this file simple and easy to understand.

def aggreation_functions():
    with Session() as session:
        # Count
        # stmt = select(func.count(Car.car_id))
        
        # Count with filter
        # stmt = select(func.count(Car.car_id)).where(Car.manufacturer=='Toyota')
        
        # Sum
        # stmt = select(func.sum(Invoice.amount))
        
        # Avergae
        # stmt = select(func.average(Invoice.amount))
        
        # Min
        # stmt = select(func.min(Invoice.amount))
        
        # Max
        # stmt = select(func.max(Invoice.amount))
        
        # result = session.scalar(stmt)
        # print(f"Total invoice: {result}")
        
        # If we want to find all the aggreagations at once we can do like this
        stmt = select(
            func.count(Car.car_id),
            func.sum(Invoice.amount),
            func.avg(Invoice.amount),
            func.min(Invoice.amount),
            func.max(Invoice.amount)
        ).join(Invoice, Invoice.car_id==Car.car_id)
        
        result = session.execute(stmt).one()
        
        print(f"Total cars: {result[0]}, Total invoice: {result[1]}, Average invoice: {result[2]}, Min invoice: {result[3]}, Max invoice: {result[4]}")