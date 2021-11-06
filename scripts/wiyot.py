import collections
import pandas as pd


_isna = lambda x: x.isna()

def split_words(wordlist,sep = '    '):
    return wordlist.split(sep)

def splitStory(story):
    splitbyWord = []
    for i in range(0,len(story),4):
        wiyot = story.iloc[i][0]
        englishGloss = story.iloc[i+1][0]
        englishTranslation = story.iloc[i+2][0]
        splitbyWord.append((wiyot,englishGloss,englishTranslation))
    return splitbyWord

def story2words(story):
    story_list = [_.split() for _ in story]
    return sum(story_list,[])

def readPreverbHierarchy(path='../data/preverbhierarchy.tsv'):
    preverbhierarchy = pd.read_csv(path,sep='\t')
    preverb2level = dict(zip(preverbhierarchy['preverb'],preverbhierarchy['Level']))
    preverb2class = dict(zip(preverbhierarchy['preverb'],preverbhierarchy['Class']))
    return preverbhierarchy, preverb2level, preverb2class

preverbhierarchy, preverb2level, preverb2class = readPreverbHierarchy()

### PreProcess story
def getStory(data,storyname):
    story = data[storyname]
    story = story.iloc[:,1:] #Skip empty column
    return story

### Further split
def reformatStory(splitstory):
    allwiyot = [_[0] for _ in splitstory]
    allenglish = [_[1] for _ in splitstory]
    fullstory = [_[2] for _ in splitstory]
    return  allwiyot,allenglish,fullstory        

getLevel = lambda preverb2level,x: preverb2level[x] if preverb2level.get(x) is not None else 0
getClass = lambda preverb2class,x: preverb2class[x] if preverb2class.get(x) is not None else 0

def testClass(english_words,preverb2level,preverb2class):
    #### Each word is separated by a space
    ### Elements of the word are separated by dashes ('-')
    x = [[ (getLevel(preverb2level,_),getClass(preverb2class,_)) for _ in word.split('-')] for word in english_words]
    english2levelclass = [[[_, [getClass(preverb2class,_)], [getLevel(preverb2level,_)]] for _ in word.split('-')] for word in english_words]
    english2levelclass = sum(english2levelclass,[])
    return english2levelclass

checkpos = lambda x,y: x <= y
removeZero = lambda x: [_ for _ in x if _ != 0]
### checkpos(1,2),checkpos(5,2) #test
def checkSequenceClass(classseq):
    classseq = removeZero(classseq)
    if len(classseq) > 1:
        res = all([checkpos(classseq[i-1],classseq[i]) for i in range(1,len(classseq))])
    else:
        res = None
    return res


def processStory(story,preverb2class=preverb2class,preverb2level=preverb2level):
    story_split = splitStory(story)
    ###
    wiyot_english_class = []
    for _ in story_split:
        translation = _[2]
        wiyot,eng = split_words(_[0]), split_words(_[1])
        eng_class = [[preverb2class[_] if preverb2class.get(_) is not None else 0 for _ in word.split('-')] for word in eng]
        eng_class = sum(eng_class,[])
        eng_level = [[preverb2level[_] if preverb2level.get(_) is not None else 0 for _ in word.split('-')] for word in eng]
        eng_level = sum(eng_level,[])
        wiyot_english_class.append([wiyot,eng,eng_class,eng_level])
    ###
    story_Wi2Eng_Hierachy = pd.DataFrame(wiyot_english_class,columns=['wiyot','english','class','class_num'])
    story_Wi2Eng_Hierachy['result'] = list(map(checkSequenceClass,story_Wi2Eng_Hierachy['class_num']))
    return story_Wi2Eng_Hierachy