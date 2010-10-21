# Find Your Teammate
# (c) Dark Secret Software Inc, 2010
# Distributed under Apache Commons License.

import random
import unittest
import sys

from jinja2 import Template, Environment, FileSystemLoader

categories = { 
    'Song' : [
        'Happy Birthday', 'California Gurls', 'Alejandro', 'Break Your Heart', 
        'Hot and Cold', 'Bad Romance', 'Teenage Dream', 'Dynamite', 
        'Cooler Than Me', 'Animal', 'Tik Tok'
    ],
    'Movie' : [
        'Despicable Me', 'Diary of a Wimpy Kid', 'Harry Potter', 
        'Nanny McPhee Returns', 'Percy Jackson', 'Karate Kid', 'The Tooth Fairy',
        'Tinkerbell', 'Camp Rock 2', 'Wizards of Waverley Place'
    ],
    'Drink' : [
        'Milk', 'Water', 'Pop', 'Coffee', 'Tea', 'Orange Juice', 
        'Tomato Juice', 'Apple Juice', 'Fruitopia', 'Shirley Temple'
    ],
    'Sport' : [
        'Soccer', 'Hockey', 'Swimming', 'Basketball', 'Volleyball',
        'Dancing', 'Running', 'Ringette', 'Football',  'Tennis', 'Badmiton'
    ],
    'Book' : [
        'Harry Potter', 'Garfield', 'Calvin & Hobbes', 'Indiana Jones', 
        'Diary of a Wimpy Kid', 'Rainbow Magic', 'Captain Underpants', 
        'Geronimo Stilton', 'Magic Treehouse', 'Allie Finkle'
    ],
    'Restaurant' : [
        'McDonalds', 'Wendys', 'Pizza Delight', 'Mr Yee', 'Swiss Chalet',
        'Monster Pizza', 'KFC', 'Freak Lunchbox', 'Jack Astors', 'Dairy Queen',
        'Manchu Wok', 'Montanas', 'Boston Pizza'
    ],
    'Fruit' : [
        'Apple', 'Orange', 'Peach', 'Pear', 'Banana', 'Plum', 'Kiwi', 'Mango'
    ],
    'Color' : [
        'Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Indigo', 'Violet', 'Black'
    ],
    'Vegetable' : [
        'Potato', 'Carrot', 'Tomato', 'Corn', 'Celery', 
        'Cucumber', 'Sweet Potato', 'Brocolli', 'Califlower'
    ],
    'Word' : [
        'Apple', 'Baker', 'Charlie', 'Delta', 'Echo', 
        'Foxtrot', 'Gamma', 'Hotel', 'India'
    ],
    'Number' : range(1, 10),
    'Animal' : [
        'Dolphin', 'Horse', 'Dog', 'Cat', 'Fish', 'Monkey', 'Pig',
        'Cow', 'Bunny', 'Snake', 'Tarantula', 'Tiger' 
    ],
    'Toy' : [
        'American Girl', 'Basketball', 'Aquasand', 'Stuffed Dog', 
        'Silly Bandz', 'Dairy Queen Blizzard Maker', 'Wii', 'Barbie'
    ],
}

player_names = [ 'Erica', 'Kaleigh', 'Savannah', 'Eryka', 'Brooke', 'Blair', 
                  'Julia', 'Maya', 'Eliza', 'Katlyn', 'Hannah', 'Haylie']

class Player:
    def __init__(self, name):
        self.favorites = {} # { category : favorite }
        self.is_red_herring = {} # { category : bool }
        self.name = name

    def fake_code(self):
        x = {}
        for category, fake in self.is_red_herring.items():
            mark = ""
            if fake:
                mark = "*"
            x[category] = mark
        return x
        
    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
        
def get_other_teams(teams, team):
    other_teams = teams[:]
    del other_teams[other_teams.index(team)]
    return other_teams

def how_much_in_common(this_team, that_team):
    in_common = 0
    for category, favorite in this_team.favorites.items():
        if not that_team.favorites.has_key(category):
            continue
        if favorite == that_team.favorites[category]:
            in_common += 1
    return in_common

def get_in_common_threshold(number_of_categories):
    """ Members on the same team will have all in common. 
    But another team might have the same favorite, but 
    they won't have more than 3/4 in common."""
    return 3 * (number_of_categories / 4)

def has_too_much_in_common(this_team, that_team, number_of_categories):
    return how_much_in_common(this_team, that_team) > get_in_common_threshold(number_of_categories)

def is_overused(other_teams, team, number_of_categories):
    """ Find out how much we already have in common with this other team.
    If we have too much, don't permit this candidate."""
    for other_team in other_teams:
        if has_too_much_in_common(team, other_team, number_of_categories):
            return True
            
    return False

class Team:
    def __init__(self, id, members):
        self.favorites = {}
        self.id = id
        self.members = members

    def __str__(self):
        return str(self.members)
        
def allocate():
    # Populate the player list with Player objects ...
    players = [Player(player_name) for player_name in player_names]

    # Start sticking Players on Teams    
    teams = []
    player_copy = players[:] # shallow
    random.shuffle(player_copy)
    
    # Assume three players per team and an even multiple of players.
    while len(player_copy) >= 3:
        first = player_copy.pop(0)
        second = player_copy.pop(0)
        third = player_copy.pop(0)
        team = Team(id = len(teams), members = [first, second, third]) 
        teams.append(team)
    
    # But if we have an odd number remaining stick them on
    # a random team.
    while len(player_copy) > 0:
        random.choice(teams).members.append(player_copy[0])

    # Give each team some things in common
    # But not given to each individual team member yet
    # (it could change there)

    # At this stage we're only storing indices to favorites.
    # Later we'll use the actual favorite. 
    # We may pick the same favorite as another team, but we'll
    # be careful not to have the same favorite for too many teams.
    for category, choices in categories.items():
        for team in teams:
            other_teams = get_other_teams(teams, team)
            choice_indices = range(len(choices))
            random.shuffle(choice_indices)
            got_one = False

            for candidate in choice_indices:
                # Add it before we see if we've over-allocated.
                # If so, keep trying and overwrite this selection.
                team.favorites[category] = candidate
                if not is_overused(other_teams, team, len(categories)):
                    got_one = True
                    break

            if not got_one:
                raise Exception("Cannot find an candidate for '%s' that is not overused." % category)

    # Now place these choices specifically on 
    # each member of each team. 
    for team in teams:
        for category, choices in categories.items():
            favorite = team.favorites[category]
            for player in team.members:
                player.favorites[category] = choices[favorite]
                player.is_red_herring[category] = False
    return teams

def find_all_unused_choices(team, category):
    used_choices = set()
    for team in teams:
        for player in team.members:
            used_choices.add(player.favorites[category])

    all_choices = set(categories[category])
    unused_choices = all_choices - used_choices
    return list(unused_choices)

def shake_up(teams):
    """ Up to this point all the players on a team have
    *exactly* the same favorites. This function mixes that up
    a little. We take N (1/3?) of the favorites and change
    them to something unused by any other player. 
    Each player on the team is ensured to have the remaining
    favorites all match. The changed onces are marked as
    "red-herrings" """
    for team in teams:
        topics = categories.keys()
        random.shuffle(topics)

        for category in topics[:5]:
            choices = categories[category]

            for player in team.members:
                unused_choices = find_all_unused_choices(teams, category)

                if len(unused_choices) == 0:
                    continue

                player.favorites[category] = random.choice(unused_choices)
                player.is_red_herring[category] = True

def show_results(teams):

    colors = ["Blue", "Yellow", "Red", "Green", "Purple"]

    all_players = []
    for team in teams:
        for player in team.members:
            all_players.append(player)

    context = {
        "teams" : teams,
        "colors" : colors,
        "categories" : categories,
    }

    env = Environment(loader = FileSystemLoader('.'))
    template = env.get_template("Master.html")
    output = template.render(context)

    file = open("index.html", "w")        
    file.write(output)
    file.close()
   
    for player in all_players:
        # TODO: We need to shuffle this up so the output
        # doesn't list all teams members side-by-side!
        others = all_players[:]
        del others[all_players.index(player)]
        ordered = [player]
        ordered.extend(others) 

        template = env.get_template("Player.html")
        context = { "players" : ordered, "categories" : categories}
        output = template.render(context)

        file = open("%s.html" % player.name, "w")        
        file.write(output)
        file.close()

class Test(unittest.TestCase):
    def test_how_much_in_common(self):
        this_team = Team(1, [])
        that_team = Team(2, [])
        this_team.favorites = {1 : 'a', 2 : 'b', 3 : 'c', 4 : 'd', 5 : 'e', 6 : 'f'}
        that_team.favorites = {1 : 'a', 2 : 'b', 3 : 'c', 4 : 'd', 5 : 'e', 6 : 'f'}
        self.assertEqual(6, how_much_in_common(this_team, that_team))
        that_team.favorites = {1 : 'aa', 2 : 'b', 3 : 'c', 4 : 'd', 5 : 'e', 6 : 'ff'}
        self.assertEqual(4, how_much_in_common(this_team, that_team))
        that_team.favorites = {1 : 'a', 2 : 'b', 3 : 'cc', 4 : 'd', 5 : 'e', 6 : 'f'}
        self.assertEqual(5, how_much_in_common(this_team, that_team))
        that_team.favorites = {1 : 'aa', 2 : 'bb', 3 : 'c', 4 : 'dd', 5 : 'ee', 6 : 'ff'}
        self.assertEqual(1, how_much_in_common(this_team, that_team))
        that_team.favorites = {1 : 'aa', 2 : 'bb', 3 : 'cc', 4 : 'dd', 5 : 'ee', 6 : 'ff'}
        self.assertEqual(0, how_much_in_common(this_team, that_team))

    def test_final_allocation(self):
        teams = allocate()
        threshold = get_in_common_threshold(len(categories))
        for team in teams:
            other_teams = get_other_teams(teams, team)
            for other_team in other_teams:
                self.assertTrue(how_much_in_common(team, other_team) < threshold)

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)

    teams = allocate()
    shake_up(teams)
    show_results(teams)

