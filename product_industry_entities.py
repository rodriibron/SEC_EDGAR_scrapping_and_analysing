import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk



### INDUSTRY AND PRODUCT ENTITY RECOGNITION ###

### THE CODE BELOW ALLOWS US TO CLASSIFY A COMPANY BY INDUSTRY BASED ON THEIR EDGAR REPORT TEXT, AND OBTAIN THE NAMES OF THE ###
### MOST RELEVANT PRODUCTS ###

### FOR THE INDUSTRY CLASSIFICATION, WE CREATED A DICTIONARY OF KEYWORDS FOR EACH MAIN INDUSTRY, WITH WHICH WE THEN ANALYSE THE TEXT ###
### TO LOOK FOR COINCIDENCES. A MAJORITY VOTE IS THEN PERFORMED AND THE COMPANY IS CLASSIFIED TO BE PART OF THE INDUSTRY WITH MORE RELEVANT ###
### KEYWORDS IN THE TEXT. WE ALSO RETURN THE OTHER TOP 3 POTENTIAL INDUSTRIES WHERE THE COMPANY BELONGS ###


### IMPORTANT: WE NEED TO DOWNLOAD SOME PRETRAINED MODELS FROM nltk FOR ENTITY RECOGNITION. THOSE ARE THE FOLLOWING: ###

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')



# The dictionary of keywords
INDUSTRY_KEYWORDS = {
        "technology": ['technology', 'telecommunications', 'IT', 'electronics', 'software', 'hardware'],
        "finance": ['finance', 'banking', 'investment', 'financial', 'insurance', 'wealth management'],
        "advertisement": ['advertisement', 'marketing', 'advertising', 'media', 'promotion'],
        "construction": ['construction', 'building', 'architecture', 'engineering', 'infrastructure'],
        "insurance": ['insurance', 'coverage', 'policy', 'underwriting', 'risk management'],
        "retail": ['retail', 'shopping', 'store', 'commerce', 'merchandise', 'consumer'],
        "education": ['education', 'school', 'learning', 'teaching', 'academy'],
        "transport": ['transport', 'transportation', 'logistics', 'shipping', 'delivery'],
        "manufacturing": ['manufacturing', 'production', 'factory', 'industry', 'assembly'],
        "defence and security": ['defence', 'security', 'military', 'army', 'defense', 'safety'],
        "healthcare": ['healthcare', 'health', 'medical', 'hospital', 'medicine'],
        "energy": ['energy', 'power', 'electricity', 'fuel', 'renewable', 'oil', 'gas'],
        "entertainment": ['entertainment', 'media', 'film', 'music', 'arts', 'culture'],
        "engineering": ['engineering', 'technology', 'design', 'innovation', 'development']
        # Add more industries and their associated keywords as needed
}




# class Entities
# A class of static methods where we wrap up the two functions we use for product and industry entity recognition


# 1. productEntities: searches the text for keywords which can be labeled to be a product, by making use of the pos_tag and ne_chunk libraries from nltk
# - text: the relevant text we want to analyse, in string format
# Returns a list of strings with the product names


# 2. industryEntities: performs the search of industry keywords for classification of the text. A majority vote is conducted and the top 3 potential 
#                      industries where the company could belong
# - text: the relevant text we want to analyse, in string format
# Returns a list of strings with the top 3 industries and their scores



class Entities:

    @staticmethod
    def productEntities(text: str) -> list[str]:

        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        named_entities = ne_chunk(pos_tags)
        
        products = []
        for entity in named_entities:
            if isinstance(entity, nltk.tree.Tree):
                # Filter entities to include only those tagged as 'ORGANIZATION'
                if entity.label() == 'ORGANIZATION':
                    # Further filtering based on specific criteria
                    entity_name = " ".join([word for word, tag in entity.leaves()])
                    if len(entity_name.split()) <= 3:  # Consider only entities with up to 3 words
                        products.append(entity_name)
        GENERAL_WORDS = ["Company", "Companys", "Business", "Securities", "Exchange", "SEC", "Workplace", "Reports"]
        unique_products = list(set(products))
        output = [prod for prod in unique_products if not any(gen in prod.split() for gen in GENERAL_WORDS)]
        return output
    


    @staticmethod
    def industryEntities(text: str) -> list[str]:
        tokens = word_tokenize(text.lower())  
        thematic_words_count = {industry: sum(1 for word in tokens if word in keywords)
                            for industry, keywords in INDUSTRY_KEYWORDS.items()}
        
        top_industries = sorted(thematic_words_count.items(), key=lambda x: x[1], reverse=True)[:3]

        output = []
        for industry, count in top_industries:
            print(industry, ":", count)
            output.append(industry)
        
        return output