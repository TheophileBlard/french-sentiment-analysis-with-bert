class AllocineReview:
    def __init__(self, rating: float, review_text: str, date, helpful):
        self.rating = rating
        self.review_text = review_text
        self.date = date
        self.helpful = helpful

    def __str__(self):              
        output = "Rating: {} / 5.0, Date: {}, Helpful: {} / Unhelpful: {}\n".format(
            self.rating, 
            self.date, 
            self.helpful[0],  
            self.helpful[1]
        )
        # Display review text in frame
        width = 100
        def chunkstring(string, length):
            return (string[0+i:length+i] for i in range(0, len(string), length))        
        output += '+-' + '-' * width + '-+' + '\n'
        for line in chunkstring(self.review_text, width):
            output += "| {0:^{1}} |".format(line, width) + '\n'
        output += '+-' + '-' * width + '-+'       

        return output       