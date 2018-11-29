#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from database_setup import Base, Restaurant, MenuItem
from mcmodel import Base, User, Media
import hashlib
import string
import random


session = ""

# connect to DB (call session.close at end of views)
def connectDB():
    global session
    engine = create_engine("sqlite:///mcollector.sqlite3")
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

def emptyDatabase():
    connectDB()
    query = session.query(User).all()
    if query:
        for row in query:
            session.delete(row)
        session.commit()

    query = None

    query = session.query(Media).all()
    if query:
        for row in query:
            session.delete(row)
        session.commit()
    session.close()

    print("Tables emptied...")



def addUsers():
    users = [
            ("Aidyn", "Abbott", "a@abbott.lan"),
            ("Ethan", "Huffman", "e@huffman.lan"),
            ("Jaydan", "Booker", "j@booker.lan"),
            ("Nyla", "Rubio", "n@rubio.lan"),
            ("Chaim", "Herman", "c@herman.lan"),
            ("Kathryn", "Barber", "k@barber.lan"),
            ("Cayden", "Gillespie", "c@gillespie.lan"),
            ("Taniya", "Roth", "t@roth.lan"),
            ("Cindy", "Pugh", "c@pugh.lan"),
            ("Tatiana", "Daniels", "t@daniels.lan"),
            ("Anabel", "Barnes", "a@barnes.lan"),
            ("Eddie", "Mercado", "e@mercado.lan"),
        ]
    password = "secret"
    authtype = "mc"

    media = [
        ("album", "rock", "cd", "Rammstein", "Rammstein"),
        ("album", "rock", "cd", "Rammstein", "Unfinished Rammstein"),
        ("album", "rock", "cd", "Rammstein", "Compil Rammstein"),
        ("album", "rock", "cd", "Rammstein", "Rammstein Best Of"),
        ("single", "rock", "cd", "Rammstein", "Du hast"),
        ("single", "rock", "cd", "Rammstein", "Mutter"),
        ("album", "rock", "cd", "Rammstein", "Bizarre Sehnsucht"),
        ("album", "rock", "cd", "Korn", "Untouchables"),
        ("album", "rock", "cd", "Korn", "See You on the Other Side"),
        ("album", "rock", "cd", "Korn", "Take A Look In The Mirror"),
        ("album", "rock", "cd", "Korn", "Issues"),
        ("album", "rock", "cd", "Korn", "Life Is Peachy"),
        ("single", "rock", "cd", "Korn", "Did my Time (Pock It)"),
        ("single", "rock", "cd", "Korn", "Make Me Bad (single)"),
        ("album", "rock", "cd", "Korn", "Follow the leader"),
        ("album", "rock", "cd", "Korn", "Ultra Rare Trax"),
        ("album", "rock", "cd", "Spineshank", "Synthetic"),
        ("single", "rock", "cd", "Spineshank", "New Disease CD-Single"),
        ("album", "rock", "cd", "Spineshank", "The Height of Callousness"),
        ("album", "rock", "cd", "Spineshank", "Self Destructive Pattern"),
        ("album", "rock", "cd", "Spineshank", "The Height of Callousness"),
        ("album", "rock", "cd", "Spineshank", "Strictly Diesel"),
        ("album", "rock", "cd", "Spineshank", "Spinshank"),
        ("album", "rock", "cd", "Spineshank", "Self-Destructive Pattern (Japanese Edition)"),
        ("album", "rock", "cd", "Killswitch Engage", "The End Of Heartache"),
        ("album", "rock", "cd", "Killswitch Engage", "As Daylight Dies"),
        ("album", "rock", "cd", "Killswitch Engage", "Alive or Just Breathing"),
        ("album", "rock", "cd", "Killswitch Engage", "(Set This) World Ablaze"),
        ("album", "blues", "vinyl", "The Smiths", "The Queen is Dead"),
        ("album", "blues", "vinyl", "The Smiths", "Play Guitar With..."),
        ("album", "blues", "vinyl", "The Smiths", "The Final Gig"),
        ("album", "blues", "vinyl", "The Smiths", "Louder Than Bombs"),
        ("album", "blues", "vinyl", "The Smiths", "Hatful Of Hollow"),
        ("single", "blues", "vinyl", "The Smiths", "How Soon Is Now?"),
        ("album", "blues", "vinyl", "The Smiths", "Asleep"),
        ("album", "blues", "vinyl", "The Smiths", "Genius Steals"),
        ("album", "blues", "vinyl", "The Smiths", "The Cradle Snatchers"),
        ("album", "blues", "vinyl", "Queen", "News of the world"),
        ("album", "blues", "vinyl", "Queen", "Greatest Hits I II & III (The Platinum Collection)"),
        ("album", "blues", "vinyl", "Queen", "Queen II"),
        ("album", "blues", "vinyl", "Queen", "A Night at the Opera"),
        ("album", "blues", "vinyl", "Queen", "The Game"),
        ("album", "blues", "vinyl", "Queen", "A Kind Of Magic"),
        ("album", "blues", "vinyl", "Queen", "The Miracle"),
        ("album", "blues", "vinyl", "Queen", "A Day At The Races"),
        ("album", "blues", "vinyl", "Queen", "God Save The Queen"),
        ("album", "blues", "vinyl", "Queen", "Innunedo"),
        ("album", "blues", "vinyl", "Queen", "The Works"),
        ("album", "blues", "vinyl", "Queen", "heer Heart Attack"),
        ("album", "blues", "vinyl", "Queen", "Jazz"),
        ("album", "blues", "vinyl", "Queen", "Sheer Heart Attack"),
        ("album", "blues", "cassette", "T. Rex", "Dandy In The Underworld"),
        ("album", "blues", "cassette", "T. Rex", "In Concert"),
        ("album", "blues", "cassette", "T. Rex", "Tanx (1973)"),
        ("album", "blues", "cassette", "T. Rex", "Futuristic Dragon Special"),
        ("album", "blues", "cassette", "T. Rex", "Electric Warrior"),
        ("album", "blues", "cassette", "T. Rex", "The Unobtainable T Rex"),
        ("album", "blues", "cassette", "T. Rex", "I Danced Myself Out of the Womb"),
        ("album", "blues", "cassette", "T. Rex", "Zip-Gun"),
        ("album", "blues", "cd", "Morrissey", "You Are The Quarry"),
        ("single", "blues", "cd", "Morrissey", "First Of The Gang To Die"),
        ("album", "blues", "cd", "Morrissey", "Ringleader Of The Tormentors"),
        ("single", "blues", "cd", "Morrissey", "The Youngest Was The Most Loved"),
        ("single", "blues", "cd", "Morrissey", "You Have Killed Me"),
        ("album", "blues", "cd", "Morrissey", "Angelic Upstart"),
        ("single", "blues", "cd", "Morrissey", "Hold On To Your Friends"),
        ("album", "blues", "cd", "Morrissey", "Practising Troublemaker"),
        ("single", "blues", "cd", "Morrissey", "Satan Rejected My Soul (Single)"),
        ("album", "blues", "vinyl", "David Bowie", "Low"),
        ("album", "blues", "vinyl", "David Bowie", "outside"),
        ("album", "blues", "vinyl", "David Bowie", "BBC Radio Theatre, London 06-27-00"),
        ("album", "blues", "vinyl", "David Bowie", "he singles collection"),
        ("album", "blues", "vinyl", "David Bowie", "The Rise And Rise Of Ziggy Stardust"),
        ("album", "blues", "vinyl", "David Bowie", "Jump They Say"),
        ("album", "blues", "vinyl", "David Bowie", "The Freakiest Show"),
        ("album", "blues", "vinyl", "David Bowie", "American Daydream 1973"),
        ("album", "blues", "vinyl", "David Bowie", "Friars Club Aylesbury 18-07-72"),
        ("album", "blues", "vinyl", "David Bowie", "ChangesTwoBowie"),
        ("album", "blues", "vinyl", "David Bowie", "Capitol Theatre New York City 14-10-97"),
        ("album", "blues", "vinyl", "David Bowie", "The Buddha Of Suburbia"),
        ("album", "blues", "vinyl", "David Bowie", "Toys from the Attic"),
        ("album", "blues", "vinyl", "Black Sabbath", "Satan Rejected My Soul (Single)"),
        ("album", "blues", "vinyl", "Black Sabbath", "Blackest Sabbath"),
        ("album", "blues", "vinyl", "Black Sabbath", "Bloody Wizard"),
        ("album", "blues", "vinyl", "Black Sabbath", "Reincarnation"),
        ("album", "blues", "vinyl", "Black Sabbath", "Mob Rules"),
        ("album", "blues", "vinyl", "Black Sabbath", "Born Again"),
        ("album", "blues", "vinyl", "Black Sabbath", "Master Of Reality"),
        ("album", "blues", "vinyl", "Black Sabbath", "Tyr"),
        ("album", "blues", "vinyl", "Black Sabbath", "Sixth Star"),
        ("album", "blues", "vinyl", "Black Sabbath", "War Pigs"),
        ("album", "blues", "cd", "Depeche Mode", "Know How"),
        ("lp", "blues", "vinyl", "Depeche Mode", "101"),
        ("album", "blues", "vinyl", "Depeche Mode", "Bestseller"),
        ("album", "blues", "vinyl", "Depeche Mode", "Depeche Mode"),
        ("album", "blues", "vinyl", "Depeche Mode", "Some Great Reward"),
        ("album", "blues", "vinyl", "Depeche Mode", "Inside"),
        ("album", "blues", "vinyl", "Depeche Mode", "I´ll Never Get Enough"),
        ("album", "blues", "cd", "Depeche Mode", "Playing The Angel"),
        ("album", "blues", "cd", "Radiohead", "Oxford Devils"),
        ("album", "blues", "cd", "Radiohead", "You can scream"),
        ("album", "blues", "cd", "Radiohead", "OK Computer"),
        ("album", "blues", "cd", "Radiohead", "Pablo Honey"),
        ("album", "blues", "cd", "Radiohead", "Amnesiac"),
        ("album", "blues", "cd", "Radiohead", "Kid A"),
        ("lp", "blues", "cd", "Radiohead", "There, There"),
        ("album", "blues", "cd", "Radiohead", "the bends"),
        ("album", "blues", "cd", "Radiohead", "Hovering Above The Tower")
    ]

    connectDB()
    for i in users:
        # generate 16 char password salt
        chars = string.ascii_letters + string.digits
        salt = "".join(random.choice(chars) for i in range(16))
        # add salt to end of password
        salted = password + salt
        hashed = hashlib.sha256(str.encode(salted)).hexdigest()
        print(hashed)
        adduser = User(
            first_name=i[0],
            last_name=i[1],
            email=i[2],
            auth_type=authtype,
            password_hash=hashed,
            password_salt=salt
        )
        session.add(adduser)

    session.commit()

    users = session.query(User.id).all()
    userids = []
    for row in users:
        userids.append(row.id)
    for row in media:
        addmedia = Media(
            user_id=random.choice(userids),
            type=row[0],
            genre=row[1],
            medium=row[2],
            artist=row[3],
            title=row[4]
        )
        session.add(addmedia)
    session.commit()
    session.close()

    print("Dummy records created...")


if __name__ == '__main__':
    emptyDatabase()
    addUsers()
