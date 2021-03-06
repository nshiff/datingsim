from locationobj import activate_location

#Parser Error Function  
class ParserError(Exception):
    pass

#The final Sentence Class outputted by the parser functions
class Sentence(object):
    def __init__(self, subject, verb, obj):
        self.subject = subject[1]
        self.verb = verb[1]
        self.object = obj[1]

#Input Object
class Input(object):
    def __init__(self):
        #self.verb=['go','give','leave','use','look','reflect']
        #self.direction=['north','south','east','west','inside', 'outside']
        self.verb = []
        self.direction = []
        self.command = ['reflect', '?']
        self.noun=['condom','flowers']
        self.character = []
        self.inactive_verb = ['masturbate']
        self.stop=['the','in','of','to', 'at']
        self.vocab={
            'verb':self.verb,
            'direction':self.direction,
            'noun':self.noun,
            'character':self.character,
            'stop':self.stop,
            'command':self.command,
            'inactive_verb':self.inactive_verb
        }
    
    def error_msg(self):
        print "I didn't understand you. Try again or type '?'."
        
    def help(self):
        if not self.vocab['inactive_verb']:
            print "I can do the following", self.vocab['verb']
        else:
            print "I can do the following", self.vocab['verb'], "or", self.vocab['inactive_verb']
        print "I can go in the following directions", self.vocab['direction']
        print "The following are in this scene", self.vocab['noun']
        
    def scan(self, sentence, inputobj):
        """Input the raw text --> Output a List of Tuples which correspond to the categories above"""
        wordlist=sentence.split()
        result=[]
        for word in wordlist:
            found=False
            for key,value in inputobj.vocab.items():
                if word.lower() in value:
                    result.append((key,word))
                    found=True
                    break
            if not found:
                try:
                    word=int(word)
                    result.append(('number',word))
                except ValueError:
                    result.append(('error',word))
        return result
                
    def peek(self, word_list):
        if word_list:
            word = word_list[0]
            return word[0]
        else:
            return None
                
    def match(self, word_list, expecting):
        if word_list:
            word = word_list.pop(0)
            
            if word[0] == expecting:
                return word
            else:
                return None
        else:
            return None
        
    def skip(self, word_list, word_type):
        while self.peek(word_list) == word_type:
            self.match(word_list, word_type)
    
    def parse_subject(self, word_list):
        if not word_list:
            return ('noun', 'none')
        else:
            self.skip(word_list, 'stop')
            next_word = self.peek(word_list)
        
            if next_word == 'noun':
                return self.match(word_list, 'noun')
            elif next_word == 'verb' or next_word == 'command':
                return ('noun', 'player')
            elif next_word == 'inactive_verb':
                return ('noun', 'inactive_player')
            elif next_word == 'error':
                return ('noun', 'error')
            else:
                return('noun', 'none')
                #raise ParserError("(parsing subject) Expected a verb next.")
                
    def parse_verb(self, word_list):
        if not word_list:
            return ('verb', 'none')
        else:
            self.skip(word_list, 'stop')
            
            if self.peek(word_list) == 'verb':
                return self.match(word_list, 'verb')
            elif self.peek(word_list) == 'command':
                return self.match(word_list, 'command')
            elif self.peek(word_list) == 'inactive_verb':
                return self.match(word_list, 'inactive_verb')
            elif self.peek(word_list) == 'error':
                return ('verb', 'error')
            else:
                return ('verb', 'none')
                #raise ParserError("(parsing verb) Expected a verb next.")
                
    def parse_object(self, word_list):
        if not word_list:
            return ('noun', 'none')
        else:
            self.skip(word_list, 'stop')
            next_word = self.peek(word_list)
        
            if next_word == 'noun':
                return self.match(word_list, 'noun')
            elif next_word == 'direction':
                return self.match(word_list, 'direction')
            elif next_word == 'character':
                return self.match(word_list, 'character')
            elif next_word == 'error':
                return('noun', 'error')
            else:
                return('noun', 'none')
                #raise ParserError("(parsing object) Expected a noun or direction next.")
            
    def parse_sentence(self, word_list):
        subj = self.parse_subject(word_list)
        verb = self.parse_verb(word_list)
        obj = self.parse_object(word_list)
        return Sentence(subj, verb, obj)
        
    def get_input(self, engine, character):
        s = self.scan(raw_input("> "), self)
        #print s
        
        x = self.parse_sentence(s)
        #for i in dir(x):
        #    print i
        #print x.subject, x.verb, x.object
        
        if x.subject == 'error' or x.subject == 'none':
            self.error_msg()
        
        if x.subject == 'inactive_player':
            print engine.current_location.inactive_verbs[x.verb]
        
        if x.verb == "?":
            self.help()
            
        if x.verb.lower() == 'go':
            if x.object.lower() == 'none':
                self.error_msg()
            elif x.object.lower() == 'error':
                print "I'm not sure where that is or if it even exists."
            else:
                activate_location(engine, x.object.lower(), self, character)
                
        if x.verb.lower() == 'leave':
            if x.object == 'none':
                if 'outside' in engine.current_location.destinations:
                    activate_location(engine, 'outside', self, character)
                else:
                    print "Where do you want to leave to?"
            else:
                activate_location(engine, x.object, self, character)
        
        if x.verb.lower() == "talk":
            if x.object == 'none':
                self.error_msg()
            else:
                if x.object not in engine.current_location.characters:
                    print "I don't see that person here."
                else:
                    character.focus(engine.girls[x.object])
                    engine.start_dialogue()
            
        if x.verb.lower() == "reflect":
            character.reflect()
        
        if x.verb.lower() == "look":
            if x.object == "none":
                engine.current_location.describe()
            else:
                engine.current_location.describe_thing(x.object)