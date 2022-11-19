
import codecs
import glob
from tqdm import tqdm
from bs4 import BeautifulSoup
import slate3k as slate

# lists of words to indicate a syllabus' discipline
# created through iterative runs over syllabi dataset to identify keywords
science = ['natural science', 'cosc','environmental science', 'engineering', 'physics', 'geology', 'geography',
           'chemistry', 'computer science', 'programming', 'comp', 'operating system',
           'aeronautics', 'astronautics', 'mathematic', 'math', 'biology', 'accounting']
social_science = ['social science','communication', 'admnistration', 'administrative studies', 'political science',
                  'economics', 'econ', 'business', 'psychology', 'public policy', 'anthropology', 'marketing',
                  'sociology']
humanities = ['humanities', 'arthist', 'history', 'music', 'drama', 'literature', 'classics', 'english',
              'philosophy', 'archaeological','archaeology', 'art', 'language',
              'religious', 'theatre', 'theater' ]

# code name for analysts, segmented into two languages
frenchgr = ['Gr', 'Va', 'Av', 'Sa', 'Bu','Al']
englishgr = ['Vi', 'Ja', 'Ha', 'Ba', 'Ri', 'Ma', 'Ni',
             'Sa', 'Ale', 'Be', 'Do', 'Cl']

# reads html files of syllabi and classifies their discipline
def htmltotxt_tocate():
    # create categories for summary of syllabi disciplines
    catetofile = {'science': [], 'social science': [],'humanities': [],'other': []}

    # search directory for the names of files
    types = ('FINISHED/**/*.htm', 'FINISHED/**/*.mhtml', 'FINISHED/**/*.html')  # the tuple of file types (.mthml, .html)
    files = []

    for htmlfiles in types:
        files.extend(glob.glob(htmlfiles, recursive=True))

    # go through each file in html file list
    for file in tqdm(files):
        # read html file into text
        try:
            with codecs.open(file, "r","utf-8") as f:
                soup = BeautifulSoup(f.read(), features="html.parser")
                str = soup.get_text()
        except:
            with codecs.open(file, "r") as f:
                soup = BeautifulSoup(f.read(), features="html.parser")
                str = soup.get_text()
        # return syllabi with predicted discipline and reading status
        print(file, ',', get_category(str), ',', get_reading(str))
        # add name of html file to the discipline dict
        catetofile[get_category(str)].append(file)
    # print the number of files in each discipline
    for key, value in catetofile.items():
        print(key, len([item for item in value if item]))

# reads pdf files of syllabi and classifies their discipline
def pdftotxt_tocate():
    #create dict of categories
    catetofile = {'science': [], 'social science': [], 'humanities': [], 'other': [], 'error':[]}

    #read pdf files recursively in folder
    pdffiles = glob.glob('FINISHED/**/*.pdf', recursive = True)

    for pdffile in tqdm(pdffiles):
        # set empty string in case pdf is not readable
        extracted_text = ''

        with open(pdffile, 'rb') as f:
            # use slate to read pdf file
            try:
                extracted_text = slate.PDF(f)
            except:
                pass
            finally:
                # get category and reading status for pdf
                category = get_category(str(extracted_text))
                reading = get_reading(str(extracted_text))

        # if the pdf file cannot be read, set category and reading error
        if len(extracted_text) == 0:
            category = 'error'
            reading = 'error'

        #print out the category and reading status of the pdf file
        print(pdffile.encode("ascii","replace"), ',', category, ',', reading )

        # add name of pdf file to the discipline dict
        catetofile[category].append(pdffile)

    # print the number of files in each discipline category
    for key, value in catetofile.items():
        print(key, len([item for item in value if item]))

# returns different discipline categories for the syllabi
def get_category(str):
    word_set = set(str.lower().split())
    for word in science:
        if word in word_set:
            return 'science'
    for word in social_science:
        if word in word_set:
            return 'social science'
    for word in humanities:
        if word in word_set:
            return 'humanities'
    return 'other'

# classify the types of readings in syllabi
def get_reading(str):
    # separates syllabi into different lines
    lines = str.lower().split('\n')

    # sets keywords to find mentions of readings of different kinds
    keywords = ['course text', 'textbook', 'issn', 'isbn', 'editor', 'editors', 'edition', ' ed.', ' eds.', 'reading',
                'course material', 'text', 'matériel', 'édition', 'auteur', 'éditeur',
                'références','ouvrages','extraits','livre']
    requireds = ['require', 'mandatory', 'necessary', 'obligatory', 'obligatoire']

    # go through each line in syllabi
    for line in lines:
        #go through each word in keywords
        for keyword in keywords:
            if keyword in line:
                for required in requireds:
                    if required in line:
                        return 'Required'
                return 'General'
    # return None if no reading words are found
    return 'None'

# assigns the analysts a roughly equal number of syllabi, segmented into two language groups
def assignperfile():
    # retrieve all files
    types = ('FINISHED/**/*.pdf','FINISHED/**/*.htm','FINISHED/**/*.mhtml',
             'FINISHED/**/*.html','FINISHED/**/*.doc','FINISHED/**/*.docx') # the tuple of file types
    allfiles = []
    for files in types:
        allfiles.extend(glob.glob(files,recursive=True))

    # create a set to fill in file spec
    filedict = {}
    # loop through the file to assign type and language
    for file in allfiles:
        if file not in filedict:
            filedict[file] = [assign_type(file),assign_language(file)]

    # assign readers to different files in filedict
    # the 'threshold' parameter, which is syllabi per analyst, came about through iterative testing
    assign_reader(filedict, 'english', englishgr, 323)
    assign_reader(filedict, 'french', frenchgr, 259)
    assign_reader(filedict, 'english', frenchgr, 64)

    engcount = 0
    frcount = 0
    avg_english = 0
    avg_french = 0
    empty = 0

    # loop through filedict to check for the number of syllabi in either French or English language
    for filename in filedict:
        #print(filename,filedict[filename])
        if 'english' in filedict[filename]:
            engcount += 1
        if 'french' in filedict[filename]:
            frcount += 1
        if len(filedict[filename]) == 2:
            empty += 1
            #print(filename.encode("ascii","replace"), ',', filedict[filename][0], ',',filedict[filename][1], ',', 'None')
        if 'Cl' in filedict[filename]:
            avg_english += 1
        if 'Sa' in filedict[filename]:
            avg_french += 1

    # calculate the total number of syllabuses already assigned to analysts
    sumreads = (avg_english * len(englishgr)) + (avg_french * len(frenchgr))

    print('english total:',engcount,', # of english readers:',len(englishgr),', average read:',engcount/len(englishgr))
    print('french total:',frcount,', # of french readers:',len(frenchgr),', average read:',frcount/len(frenchgr))
    print('english avg read actual:', avg_english ,'french avg read actual:', avg_french)
    print('total readings should be:' , sumreads)
    print('missing:', empty)

# assigns a reader to a syllabus
def assign_reader(dict,lang, langgr, threshold):
    i = 0
    count = 0
    for filename in tqdm(dict):
        list = dict[filename]
        # check if the file's list already has a reader assigned
        if len(list) == 3:
            # skip to the next file
            continue

        # check if syllabus is english
        if lang in list:
            # move on to next person if quota reached
            if count == threshold:
                # next person's loc
                i += 1
                # next person's count docs
                count = 0

            # add person to file information
            if i < len(langgr):
                list.append(langgr[i])
                print(filename.encode("ascii","replace"), ',', list[0], ',', list[1], ',', list[2])
                count += 1

            # exit if ran through all in language group
            if i >= len(langgr):
                break

# helps determine what file type a syllabus is
def assign_type(file):
    if '.htm' in file:
        return 'html'
    if '.doc' in file:
        return 'doc'
    if '.pdf' in file:
        return 'pdf'
    return 'other'

# helps determine what language a syllabus is
# using university name as a proxy
def assign_language(file):
    # list of univerities in Canada assumed to have French as dominant language instruction
    french = ['uqam', 'ulaval', 'umontreal', 'usherbrooke']

    for fr in french:
        if fr in file:
            return 'french'
    return 'english'

# optional code
# use to check for nursing syllabi
def medical(filename, str):
    word_set = set(str.lower().split())
    if 'nursing' in word_set:
        print(filename)

# runs the code
def main():
    htmltotxt_tocate()
    #pdftotxt_tocate()
    #assignperfile()
    #assign_reader()

if __name__ == '__main__':
    main()
