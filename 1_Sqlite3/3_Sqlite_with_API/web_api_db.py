import sqlite3
import requests

def db_setup():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS Users")
    cursor.execute("DROP TABLE IF EXISTS UserAddresses")
    cursor.execute("DROP TABLE IF EXISTS UserPictures")
    cursor.execute("DROP TABLE IF EXISTS UserRelationships")
    
    cursor.execute("""
        CREATE TABLE Users (
            userId INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )"""
    )
    
    cursor.execute("""
        CREATE TABLE UserAddresses (
            userAddressId INTEGER PRIMARY KEY,
            street TEXT,
            city TEXT,
            country TEXT,
            postcode TEXT
        )"""
    )
    
    cursor.execute("""
        CREATE TABLE UserPictures (
            userPictureId INTEGER PRIMARY KEY,
            largeImg TEXT,
            mediumImg TEXT,
            thumbnailImg TEXT
        )"""
    )
    
    cursor.execute("""
        CREATE TABLE UserRelationships (
            relId INTEGER PRIMARY KEY,
            userId INTEGER,
            userAddressId INTEGER,
            userPictureId INTEGER,
            FOREIGN KEY (userId) REFERENCES Users(userId),
            FOREIGN KEY (userAddressId) REFERENCES UserAddresses(userAddressId),
            FOREIGN KEY (userPictureId) REFERENCES UserPictures(userPictureId)
        )"""
    )
    conn.commit()
    conn.close()
    
    
def fetch_and_store_users(num_users=20):
    response = requests.get(f'https://randomuser.me/api/?results={num_users}')
    data = response.json()
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    for user in data['results']:
        first_name = user['name']['first']
        last_name = user['name']['last']
        email = user['email']
        
        cursor.execute("""
            INSERT INTO Users (first_name, last_name, email)
            VALUES (?, ?, ?)""",
            (first_name, last_name, email)
        )
        user_id = cursor.lastrowid
        
        street = f"{user['location']['street']['number']} {user['location']['street']['name']}"
        city = user['location']['city']
        country = user['location']['country']
        postcode = user['location']['postcode']
        
        cursor.execute("""
            INSERT INTO UserAddresses (street, city, country, postcode)
            VALUES (?, ?, ?, ?)""",
            (street, city, country, postcode)
        )
        address_id = cursor.lastrowid
        
        large_img = user['picture']['large']
        medium_img = user['picture']['medium']
        thumbnail_img = user['picture']['thumbnail']
        
        cursor.execute("""
            INSERT INTO UserPictures (largeImg, mediumImg, thumbnailImg)
            VALUES (?, ?, ?)""",
            (large_img, medium_img, thumbnail_img)
        )
        picture_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO UserRelationships (userId, userAddressId, userPictureId)
            VALUES (?, ?, ?)""",
            (user_id, address_id, picture_id)
        )
    
    conn.commit()
    conn.close()
    

if __name__ == "__main__":
    db_setup()
    fetch_and_store_users(20)
    