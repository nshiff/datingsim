import time

#GAme States
class EngineDisabled(object):
    def __repr__(self):
        return "disabled_state"
        
    def idle_engine(self, engine):
        engine.state = EngineIdle()
        
    def enable_dialogue(self, engine):
        engine.state = DialogueEnabled()
    
    def enable_day(self, engine):
        engine.state = DayEnabled()

class EngineIdle(EngineDisabled):
    def __repr__(self):
        return "idle_state"
        
class DialogueEnabled(EngineDisabled):
    def __repr__(self):
        return "dialogue_state"

    def disable_dialogue(self, engine):
        engine.state = EngineIdle()
        
class DayEnabled(EngineDisabled):
    def __repr__(self):
        return "day_state"

    def disable_day(self, engine):
        engine.state = EngineIdle()
    
#Game object
class Engine(object):
    def __init__(self):
        self.game_over = False
        self.current_location = None
        self.locations = {}
        self.girls = {}
        self.state = EngineDisabled()
    
    #State Functions
    def idle_engine(self):
        self.state.idle_engine(self)
    def start_dialogue(self):
        self.state.enable_dialogue(self)
    def start_day(self):
        self.state.enable_day(self)
        
    def introduction(self, text):
        time.sleep(0.5)
        print text
        
    def build_locations(self, location_list):
        for key, value in location_list.iteritems():
            obj = Location(key, value['destinations'], value['description'], value['date_description'], value['verbs'], value['nouns'], value['inactive_verbs'])
            self.locations[key] = obj
            
    def build_girls(self, girl_list):
        for key, value in girl_list.iteritems():
            obj = Girl(key, value['love'], value['prude'], value['location'], value['opinion'], value['dialogue_tree'])
            self.girls[key] = obj
            
    def activate_location(self, destination, inputobj, character):
        if self.current_location:
            print "my current location is", self.current_location.name
            new_location = self.current_location.destinations[destination]
            self.current_location = self.locations[new_location]
        else:
            self.current_location = self.locations[destination]
            
        print "I am currently at the "+ str(self.current_location.name)+"."
        self.current_location.describe()
        
        character.known_locations.append(self.current_location.name)

        #clear the list of directions you can go    
        #repopulate list of available directions based on current location
        del inputobj.direction[:]
        for k, v in self.current_location.destinations.iteritems():
            inputobj.direction.append(k)

        #add location verbs to inputobject verb list
        del inputobj.verb[:]
        inputobj.verb = ['go','give','leave','use','look', 'talk']
        for k, v in self.current_location.verbs.iteritems():
            inputobj.verb.append(k)
            
        #add location nouns to inputobject verb list
        del inputobj.noun[:]
        for k, v in self.current_location.nouns.iteritems():
            inputobj.noun.append(k)
            
        #add location inactive verbs to inputobjects inactive verb list
        del inputobj.inactive_verb[:]
        for k, v in self.current_location.inactive_verbs.iteritems():
            inputobj.inactive_verb.append(k)
        
        #update Input Object's "Vocab" lists
        inputobj.vocab['verb'] = inputobj.verb
        inputobj.vocab['direction'] = inputobj.direction
        inputobj.vocab['noun'] = inputobj.noun
        inputobj.vocab['inactive_verb'] = inputobj.inactive_verb
        
    #maybe come back and use this
    #def check_state(self, inputobj, character):
    #    #print self.state
    #    if str(self.state) == 'day_state':
    #        self.get_input(inputobj, character)
    #    elif self.state == 'dialogue_state':
    #        self.get_dialogue(inputobj, character)

        
    def get_input(self, inputobj, character):
        s = inputobj.scan(raw_input("> "), inputobj)
        #print s
        
        x = inputobj.parse_sentence(s)
        #for i in dir(x):
        #    print i
        #print x.subject
        
        if x.subject == 'error':
            inputobj.error_msg()
        
        if x.subject == 'inactive_player':
            print self.current_location.inactive_verbs[x.verb]
        
        if x.verb == "?":
            inputobj.help()
            
        if x.verb.lower() == 'go':
            if x.object.lower() == 'error':
                inputobj.error_msg()
            else:
                self.activate_location(x.object.lower(), inputobj, character)
        
        if x.verb.lower() == "talk":
            self.start_dialogue()
            
        if x.verb.lower() == "reflect":
            character.reflect()
        
        if x.verb.lower() == "look":
            if x.object == "none":
                self.current_location.describe()
            else:
                self.current_location.describe_thing(x.object)
    
    def get_dialogue(self, d, main_character, character):
        print """
        %s stands in front of you.
        """ % character.name
        
        print "Enter your choice."
        for k,v in character.dialogue_tree[d.level]['statement'].iteritems():
            print k, '-', v

        d1 = raw_input("> ")

        if d1 == 1:
            print character.dialogue_tree[d.level]['reply'][1]
            character.opinion += 1
        elif d1 == 2:
            print character.dialogue_tree[d.level]['reply'][2]
            character.opinion += 0
        elif d1 == 3:
            print character.dialogue_tree[d.level]['reply'][3]
        #d.level +=1
        
                
class Location(object):
    def __init__(self, name, destinations, description, date_description, verbs, nouns, inactive_verbs):
        self.name = name
        self.destinations = destinations
        self.description = description
        self.date_description = date_description        
        self.verbs = verbs
        self.nouns = nouns
        self.inactive_verbs = inactive_verbs

    def describe(self):
        print self.description

    def describe_thing(self, thing):
        print self.nouns[thing]

class Character(object):
    def __init__(self):
        self.name = ""
        self.known_locations = []

    def get_name(self, name=""):
        if name:
            self.name = "Kosek"
        else:
            print "What is your name?"
            self.name = raw_input("> ")

    def reflect(self):
        print "My name is", self.name
        print "My known locations are: "+str(self.known_locations)

class Girl(object):
    def __init__(self, name, fall_in_love, prude, prefer_location, opinion, dialogue_tree):
        self.name = name
        self.fall_in_love = fall_in_love
        self.prude = prude
        self.prefer_location = prefer_location
        self.opinion = opinion
        self.dialogue_tree = dialogue_tree
        
class Dialogue(object):
    def __init__(self):
        self.level = 1