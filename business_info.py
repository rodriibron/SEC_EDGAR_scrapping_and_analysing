from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize



### FILTER AND SUMMARISE RELEVANT TEST ###
### THE FOLLOWING CODE IS USED TO OBTIAN THE RELEVANT PARTS OF THE DOCUMENT WHICH WE WANT TO SUMMARISE ##
### AND TO PERFORM SUCH SUMMARISATION USING THE NLP LIBRARY nltk ###





# class BusinessInfo

# ATRIBUTTES:
# 1. edgar_file: the already downloaded text file of the EDGAR report. This should be scraped first using text_scraper.py
# 2. text: the raw text. This is obtained with the getText() method
# 3. lines: a list of strings which are the text of each line in the document. This is obtained with the getLines() method



# METHODS AND THEIR ARGUMENTS:
# 1. getText: gets the text from the file and returns it in string format
# - only takes self


# 2. getLines: gets a list of strings which are the text of each line in the document
# - only takes self


# 3. infoLines: for us to effectively create business and industry summaries, we only need to summarise the first section of the document, 
#               which precisely contains this information. This functinos return the first and last line where relevant inormation is. With this, 
#               we then substract the text between those lines in string format. 
# - only takes self
# - output is a list wiht exactly the first and last relevant line


# 4. businessInfo: retrieves a string with precisely the relevant text mentioned before
# - indices: these are the first and last relevant line, which are obtained with the infoLines method


# 5. and 6. finLines and finInfo: similarly, for a financial summary, we only need to retrieve sections 7 and 8 of the text. These two methods have exactly
#           the same functionalities as the previous two, but for the financial summary.



class BusinessInfo:

    def __init__(self, edgar_file):
        self.edgar_file = edgar_file
        self.text = self.getText()
        self.lines = self.getLines()
  
    

    def getText(self) -> str:
        with open(self.edgar_file) as file:
            text = file.read()
        return text
    


    def getLines(self) -> list[str]:
        with open(self.edgar_file, 'r') as file:
            lines = file.readlines() 
        
        punctuation_chars = [",", ".", ":", ";", "-"]
        cleaned_lines = []
        for line in lines:
            cleaned_line = ''.join(char for char in line if char.isalnum() or char.isspace() or char in punctuation_chars)
            cleaned_lines.append(cleaned_line)
        
        return [word.strip() for word in cleaned_lines]
    
    def infoLines(self) -> list[int]:
        first_count = 0
        last_count = 0
        indices = []
        for i, line in enumerate(self.lines):
            if "item 1." and "business" in line.lower():
                first_count += 1
                if first_count == 3:
                    indices.append(i)
            if "item 1a" in line.lower(): #and "Risk Factors" in line:
                last_count += 1
                if last_count == 3:
                    indices.append(i)
        return indices
    
    def businessInfo(self, indices: list[str]) -> str:
        btext = "" 
        for j in range(indices[0] +1, indices[1]):
            btext += " " + self.lines[j]
        return btext
    
    def finLines(self) -> list[int]:
        first_count = 0       
        indices = []
        last_indices = []
        for i, line in enumerate(self.lines):
            if "item 7" and "discussion and analysis" in line.lower():
                first_count += 1
                if first_count == 4:
                    indices.append(i)
                
                
            if "item 9" and "disagreements" in line.lower():
                last_indices.append(i)
        
        last = last_indices[-1]
        indices.append(last)
        return indices
    
    def finInfo(self, indices: list[str]) -> str:
        btext = "" 
        for j in range(indices[0] +1, indices[1]):
            btext += " " + self.lines[j]
        return btext
    




# class BusinessSummary
# A child class of BusinessInfo used to sumamrise text


# ATRIBUTTES:
# 1. indices: the indices obtained with getLines in BusinessInfo
# 2. text: we override the text attribute and set it to precisely the sections of the text we are interested on. Obtained with BusinessInfo.businessInfo()
# 3. frequency_table: the frequency table for each word in the text. Of type dictionary, and obtained with _create_dictionary_table()
    


# METHODS AND THEIR ARGUMENTS:
# 1. _create_dictionary_table: creates the frequency table for words in the text
# - only takes self
    

# 2. _calculate_sentence_scores: this gives a score to each sentence by its words; that is, adding the frequency of each important word found in the sentence.
# - sentences: a list of strings with each sentence in the text. This list must be tokenised. For that, in main.py() and in the method get_edgar_summary(), we will use the
#              nltk.tokenize library built in functino sent_tokenise. Sentences is thus the tokenisation of the string text sent_tokenize(self.text). 
#              This will further tweak the kind of sentences eligible for summarization
# Note: Returns a dictionary of scores per sencence
    

# 3. _calculate_average_score: Calculates the average score of the sentences in the text
# - sentence_weight: the dictionary of sentence scores created with _calculate_sentence_scores()
    

# 4. _get_edgar_summary: Generates the summary for the text.
# - sentences: the aforementioned tokenised sentences obtained by input the string text into nltk.tokenize.sent_tokenize()
# - sentence_weight: the dictionary of sentence scores created with _calculate_sentence_scores()
# - threshold: a float which lets us change the threshold of sentences elegible for summarisation
    

# 5. get_edgar_summary: wraps up all the previous methods and returns the actual text summary.
# - text: the string of text we want to summarise.


class BusinessSummary(BusinessInfo):

    def __init__(self, edgar_file):
        super().__init__(edgar_file)
        self.indices = self.infoLines()
        self.text = self.businessInfo(self.indices)
        self.frequency_table = self._create_dictionary_table()
    


    def _create_dictionary_table(self) -> dict:
        stop_words = set(stopwords.words("english"))
        words = word_tokenize(self.text)
        #reducing words to their root form
        stem = PorterStemmer()
        
        frequency_table = dict()
        for wd in words:
            wd = stem.stem(wd)
            if wd in stop_words:
                continue
            if wd in frequency_table:
                frequency_table[wd] += 1
            else:
                frequency_table[wd] = 1
        
        return frequency_table
    


    # sentences = sent_tokenize(self.text)
    def _calculate_sentence_scores(self, sentences: list[str]) -> dict:   
        sentence_weight = dict()
        for sentence in sentences:
            sentence_wordcount = (len(word_tokenize(sentence)))
            sentence_wordcount_without_stop_words = 0
            for word_weight in self.frequency_table:
                if word_weight in sentence.lower():
                    sentence_wordcount_without_stop_words += 1
                    if sentence[:7] in sentence_weight:
                        sentence_weight[sentence[:7]] += self.frequency_table[word_weight]
                    else:
                        sentence_weight[sentence[:7]] = self.frequency_table[word_weight]

        sentence_weight[sentence[:7]] = sentence_weight[sentence[:7]] / sentence_wordcount_without_stop_words
        
        return sentence_weight
    


    def _calculate_average_score(self, sentence_weight: dict) -> int:
        sum_values = 0
        for entry in sentence_weight:
            sum_values += sentence_weight[entry]
        
        #getting sentence average value from source text
        average_score = (sum_values / len(sentence_weight))
        return average_score
    
    @staticmethod
    def _get_edgar_summary(sentences, sentence_weight, threshold):
        sentence_counter = 0
        article_summary = ''
        
        for sentence in sentences:
            if sentence[:7] in sentence_weight and sentence_weight[sentence[:7]] >= (threshold):
                article_summary += " " + sentence
                sentence_counter += 1
            
        return article_summary
    
    def get_edgar_summary(self, text: str) -> str:

        sentences = sent_tokenize(text)
        sentence_scores = self._calculate_sentence_scores(sentences)
        threshold = self._calculate_average_score(sentence_scores)
        article_summary = self._get_edgar_summary(sentences, sentence_scores, 1.5 * threshold)
        return article_summary
    

