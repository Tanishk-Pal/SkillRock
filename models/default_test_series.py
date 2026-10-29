"""
SkillRock — Default Test Series & Verified Question Bank Seeder
Seeds initial 4 Test Packs and 3 complete 30-question free tests with verified
mathematical formulas, algorithmic logic, output predictions, and detailed solutions.
"""

from models.test_series import Question, TestDefinition, TestPack

def get_aptitude_questions():
    """Returns 30 verified Aptitude & Logical Reasoning questions."""
    return [
        {
            "question_text": "A train running at 54 km/hr takes 20 seconds to cross a railway platform 180 meters long. What is the length of the train in meters?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Speed, Time & Distance",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "100 m"},
                {"id": "b", "text": "120 m"},
                {"id": "c", "text": "140 m"},
                {"id": "d", "text": "150 m"}
            ],
            "correct_answers": ["b"],
            "explanation": "Speed = 54 * (5/18) = 15 m/s. Total distance crossed = Speed * Time = 15 * 20 = 300 m. Since Total Distance = Length of Train + Platform Length (180 m), Train Length = 300 - 180 = 120 meters.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "If the price of sugar increases by 25%, by what percentage must a household reduce its consumption so that the expenditure on sugar remains unchanged?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Percentages",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "20%"},
                {"id": "b", "text": "25%"},
                {"id": "c", "text": "16.67%"},
                {"id": "d", "text": "15%"}
            ],
            "correct_answers": ["a"],
            "explanation": "Reduction % = [r / (100 + r)] * 100 = [25 / 125] * 100 = (1/5) * 100 = 20%.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A can do a piece of work in 12 days and B in 15 days. If they work together for 4 days, what fraction of the work remains unfinished?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Time & Work",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "1/5"},
                {"id": "b", "text": "2/5"},
                {"id": "c", "text": "3/5"},
                {"id": "d", "text": "4/5"}
            ],
            "correct_answers": ["b"],
            "explanation": "A's 1-day work = 1/12, B's 1-day work = 1/15. Together in 1 day = (1/12 + 1/15) = 9/60 = 3/20. In 4 days = 4 * (3/20) = 12/20 = 3/5. Remaining work = 1 - 3/5 = 2/5.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Two numbers are in the ratio 3 : 5. If 9 is subtracted from each, the new numbers are in the ratio 12 : 23. What is the smaller number?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Ratios & Proportions",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "27"},
                {"id": "b", "text": "33"},
                {"id": "c", "text": "45"},
                {"id": "d", "text": "55"}
            ],
            "correct_answers": ["b"],
            "explanation": "Let numbers be 3x and 5x. (3x - 9) / (5x - 9) = 12 / 23 => 23(3x - 9) = 12(5x - 9) => 69x - 207 = 60x - 108 => 9x = 99 => x = 11. Smaller number = 3 * 11 = 33.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "The average weight of 8 persons increases by 2.5 kg when a new person comes in place of one weighing 65 kg. What is the weight of the new person?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Averages",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "75 kg"},
                {"id": "b", "text": "80 kg"},
                {"id": "c", "text": "85 kg"},
                {"id": "d", "text": "90 kg"}
            ],
            "correct_answers": ["c"],
            "explanation": "Total weight increase = 8 * 2.5 = 20 kg. Weight of new person = Replaced weight + total increase = 65 + 20 = 85 kg.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Find the next term in the number series: 7, 14, 42, 168, 840, ?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Number Series",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "4200"},
                {"id": "b", "text": "5040"},
                {"id": "c", "text": "5880"},
                {"id": "d", "text": "6720"}
            ],
            "correct_answers": ["b"],
            "explanation": "The pattern is multiplicative: 7 * 2 = 14; 14 * 3 = 42; 42 * 4 = 168; 168 * 5 = 840; 840 * 6 = 5040.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In a certain code, 'COMPUTER' is written as 'RFUVQNPC'. How is 'MEDICINE' written in the same code?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Coding-Decoding",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "EOJDJEFM"},
                {"id": "b", "text": "EOJDEJFM"},
                {"id": "c", "text": "MFEJDJOE"},
                {"id": "d", "text": "EOJDJEFN"}
            ],
            "correct_answers": ["a"],
            "explanation": "First and last letters reverse places (C<->R, M<->E). Every intermediate letter is replaced by its next alphabetical letter and reversed in sequence: E(F), N(O), I(J), C(D), I(J), D(E) leading to EOJDJEFM.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Introducing a boy, a girl said, 'He is the son of the daughter of the father of my uncle.' How is the boy related to the girl?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Blood Relations",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "Brother"},
                {"id": "b", "text": "Uncle"},
                {"id": "c", "text": "Nephew"},
                {"id": "d", "text": "Father"}
            ],
            "correct_answers": ["a"],
            "explanation": "Father of my uncle = Girl's grandfather. Daughter of girl's grandfather = Girl's mother (or aunt). Son of girl's mother = Girl's brother.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A man walks 5 km East, turns right and walks 4 km, then turns left and walks 5 km. In which direction is he now from his starting point?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Direction Sense",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "South"},
                {"id": "b", "text": "East"},
                {"id": "c", "text": "South-East"},
                {"id": "d", "text": "North-East"}
            ],
            "correct_answers": ["c"],
            "explanation": "Starting at (0,0): East 5km -> (5,0). Right (South) 4km -> (5, -4). Left (East) 5km -> (10, -4). Position (10, -4) is South-East of origin.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A shopkeeper sells an article at a discount of 10% on the marked price and still gains 20%. If the cost price is ₹300, what is the marked price?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Profit & Loss",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "₹380"},
                {"id": "b", "text": "₹400"},
                {"id": "c", "text": "₹420"},
                {"id": "d", "text": "₹450"}
            ],
            "correct_answers": ["b"],
            "explanation": "Selling Price = CP * (1 + 0.20) = 300 * 1.2 = ₹360. Since SP is 90% of Marked Price (MP * 0.9 = 360), MP = 360 / 0.9 = ₹400.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Find the odd one out: 27, 64, 125, 216, 343, 512, 729",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Odd One Out",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "27"},
                {"id": "b", "text": "64"},
                {"id": "c", "text": "343"},
                {"id": "d", "text": "729"}
            ],
            "correct_answers": ["b"],
            "explanation": "All numbers are perfect cubes: 3^3=27, 4^3=64, 5^3=125, 6^3=216, 7^3=343, 8^3=512, 9^3=729. However, 64 is also a perfect square (8^2) as is 729 (27^2), but among basic odd/even cubes, 64 is the only power of 2 that is also a 6th power (2^6). Alternatively, in prime-cube classification, 64 is an even composite cube.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "At what time between 3 and 4 o'clock will the hands of a clock coincide?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Clocks & Calendars",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "16 minutes past 3"},
                {"id": "b", "text": "16 (4/11) minutes past 3"},
                {"id": "c", "text": "15 (5/11) minutes past 3"},
                {"id": "d", "text": "18 minutes past 3"}
            ],
            "correct_answers": ["b"],
            "explanation": "Angle between hands = |30H - (11/2)M|. Coincide means angle = 0: 30(3) = (11/2)M => 90 * 2 = 11M => M = 180 / 11 = 16 (4/11) minutes past 3.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What was the day of the week on 15th August 1947?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Clocks & Calendars",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "Thursday"},
                {"id": "b", "text": "Friday"},
                {"id": "c", "text": "Saturday"},
                {"id": "d", "text": "Sunday"}
            ],
            "correct_answers": ["b"],
            "explanation": "1600 years = 0 odd days. 300 years = 1 odd day. 46 years (11 leap + 35 ordinary) = 11*2 + 35 = 57 odd days = 1 odd day. Days in 1947 up to Aug 15: Jan(3)+Feb(0)+Mar(3)+Apr(2)+May(3)+Jun(2)+Jul(3)+Aug(15) = 31 days = 3 odd days. Total = 1 + 1 + 3 = 5 odd days. Day 5 is Friday.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A box contains 5 red, 4 green, and 3 blue balls. If 2 balls are drawn at random, what is the probability that both are red?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Probability",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "5/33"},
                {"id": "b", "text": "1/6"},
                {"id": "c", "text": "5/66"},
                {"id": "d", "text": "10/33"}
            ],
            "correct_answers": ["a"],
            "explanation": "Total balls = 5 + 4 + 3 = 12. Total ways to draw 2 = 12C2 = (12 * 11) / 2 = 66. Favorable ways (both red) = 5C2 = (5 * 4) / 2 = 10. Probability = 10 / 66 = 5 / 33.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "How many words can be formed from the letters of the word 'LEADING' so that the vowels always come together?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Permutations & Combinations",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "360"},
                {"id": "b", "text": "480"},
                {"id": "c", "text": "720"},
                {"id": "d", "text": "1440"}
            ],
            "correct_answers": ["c"],
            "explanation": "Word LEADING has 7 distinct letters. Vowels are E, A, I (3 vowels). Consonants are L, D, N, G (4 consonants). Treat (E,A,I) as 1 bundle + 4 consonants = 5 units. Ways to arrange 5 units = 5! = 120. Internal arrangements of 3 vowels = 3! = 6. Total = 120 * 6 = 720.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Statements: (1) All mangoes are golden. (2) No golden things are cheap. Conclusions: (I) All mangoes are costly. (II) Golden mangoes are not cheap.",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Syllogisms",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Only conclusion I follows"},
                {"id": "b", "text": "Only conclusion II follows"},
                {"id": "c", "text": "Either I or II follows"},
                {"id": "d", "text": "Both I and II follow"}
            ],
            "correct_answers": ["d"],
            "explanation": "Since all mangoes are golden and no golden things are cheap, mangoes cannot be cheap (i.e. they are not cheap / costly). Conclusion II is directly entailed by the premises.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A sum of ₹12,500 amounts to ₹15,500 in 4 years at the rate of simple interest. What is the annual rate of interest?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Simple & Compound Interest",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "5%"},
                {"id": "b", "text": "6%"},
                {"id": "c", "text": "7%"},
                {"id": "d", "text": "8%"}
            ],
            "correct_answers": ["b"],
            "explanation": "SI = Amount - Principal = 15,500 - 12,500 = ₹3,000. R = (SI * 100) / (P * T) = (3000 * 100) / (12500 * 4) = 300,000 / 50,000 = 6%.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "The compound interest on ₹30,000 at 7% per annum is ₹4,347. What is the time period in years?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Simple & Compound Interest",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "2 years"},
                {"id": "b", "text": "2.5 years"},
                {"id": "c", "text": "3 years"},
                {"id": "d", "text": "4 years"}
            ],
            "correct_answers": ["a"],
            "explanation": "Amount = 30000 + 4347 = 34347. 34347 / 30000 = (1 + 7/100)^n => 11449 / 10000 = (107/100)^n. Notice (107)^2 = 11449 and (100)^2 = 10000, so n = 2 years.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A boat can travel with a speed of 13 km/hr in still water. If the speed of the stream is 4 km/hr, find the time taken by the boat to go 68 km downstream.",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Boats & Streams",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "3 hours"},
                {"id": "b", "text": "4 hours"},
                {"id": "c", "text": "5 hours"},
                {"id": "d", "text": "5.5 hours"}
            ],
            "correct_answers": ["b"],
            "explanation": "Downstream speed = Speed of boat + Speed of stream = 13 + 4 = 17 km/hr. Time = Distance / Speed = 68 / 17 = 4 hours.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Pipe A can fill a tank in 20 hours while Pipe B can fill it in 30 hours. Both pipes are opened together. How long will they take to fill the tank?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Pipes & Cisterns",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "10 hours"},
                {"id": "b", "text": "12 hours"},
                {"id": "c", "text": "15 hours"},
                {"id": "d", "text": "25 hours"}
            ],
            "correct_answers": ["b"],
            "explanation": "Part filled in 1 hr = 1/20 + 1/30 = (3 + 2)/60 = 5/60 = 1/12. Time taken = 12 hours.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "If 6 men and 8 boys can do a piece of work in 10 days, while 26 men and 48 boys can do the same in 2 days, what time will be taken by 15 men and 20 boys to complete it?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Time & Work",
            "difficulty": "Advanced",
            "options": [
                {"id": "a", "text": "4 days"},
                {"id": "b", "text": "5 days"},
                {"id": "c", "text": "6 days"},
                {"id": "d", "text": "7 days"}
            ],
            "correct_answers": ["a"],
            "explanation": "10(6M + 8B) = 2(26M + 48B) => 60M + 80B = 52M + 96B => 8M = 16B => 1M = 2B. 6M + 8B = 6(2B) + 8B = 20 boys. 20 boys take 10 days => Total work = 200 boy-days. 15M + 20B = 15(2B) + 20B = 50 boys. Days = 200 / 50 = 4 days.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Complete the analogy: Light : Blind :: Speech : ?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Verbal Analogies",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Deaf"},
                {"id": "b", "text": "Dumb"},
                {"id": "c", "text": "Sound"},
                {"id": "d", "text": "Vibration"}
            ],
            "correct_answers": ["b"],
            "explanation": "A person devoid of sight/light is blind; a person unable to produce speech is mute/dumb.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In a row of 40 children, P is thirteenth from the left end and Q is ninth from the right end. How many children are there between P and R if R is fourth to the left of Q?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Seating & Ordering",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "12"},
                {"id": "b", "text": "13"},
                {"id": "c", "text": "14"},
                {"id": "d", "text": "15"}
            ],
            "correct_answers": ["c"],
            "explanation": "Total = 40. P is 13th from left. Q is 9th from right, meaning Q is 40 - 9 + 1 = 32nd from left. R is 4th to the left of Q, so R is 32 - 4 = 28th from left. Children strictly between P (13) and R (28) = 28 - 13 - 1 = 14.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "If A + B means A is the brother of B; A - B means A is the sister of B; A * B means A is the father of B, which of the following means that C is the son of M?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Blood Relations",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "M * C"},
                {"id": "b", "text": "M * C + N"},
                {"id": "c", "text": "M - C + N"},
                {"id": "d", "text": "N * M - C"}
            ],
            "correct_answers": ["b"],
            "explanation": "M * C means M is the father of C. C + N means C is the brother of N (confirming C is male, hence a son). Therefore, M * C + N proves C is the son of M.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the angle between the hands of a clock at 8:30?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Clocks & Calendars",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "65 degrees"},
                {"id": "b", "text": "75 degrees"},
                {"id": "c", "text": "80 degrees"},
                {"id": "d", "text": "85 degrees"}
            ],
            "correct_answers": ["b"],
            "explanation": "Angle = |30H - (11/2)M| = |30(8) - 5.5(30)| = |240 - 165| = 75 degrees.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A vendor bought toffees at 6 for a rupee. How many for a rupee must he sell to gain 20%?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Profit & Loss",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "3"},
                {"id": "b", "text": "4"},
                {"id": "c", "text": "5"},
                {"id": "d", "text": "6"}
            ],
            "correct_answers": ["c"],
            "explanation": "CP of 6 toffees = ₹1 => CP of 1 toffee = ₹(1/6). Desired SP of 1 toffee = (1/6) * 1.20 = 1.2/6 = ₹(1/5). For ₹1, number of toffees sold = 5.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which number replaces the question mark in the sequence: 4, 9, 25, 49, 121, ?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Number Series",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "144"},
                {"id": "b", "text": "169"},
                {"id": "c", "text": "196"},
                {"id": "d", "text": "225"}
            ],
            "correct_answers": ["b"],
            "explanation": "The terms are squares of consecutive prime numbers: 2^2=4, 3^2=9, 5^2=25, 7^2=49, 11^2=121. The next prime number is 13, and 13^2 = 169.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A batsman makes a score of 87 runs in the 17th inning and thus increases his average by 3. Find his average after 17th inning.",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Averages",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "36"},
                {"id": "b", "text": "39"},
                {"id": "c", "text": "42"},
                {"id": "d", "text": "45"}
            ],
            "correct_answers": ["b"],
            "explanation": "Let old average be x. Total runs in 16 innings = 16x. 16x + 87 = 17(x + 3) => 16x + 87 = 17x + 51 => x = 36. New average = x + 3 = 39.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Point A is 10 m South of B. Point C is 12 m East of B. Point D is 6 m North of C. What is the shortest distance between A and D?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Direction Sense",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "18 m"},
                {"id": "b", "text": "20 m"},
                {"id": "c", "text": "22 m"},
                {"id": "d", "text": "24 m"}
            ],
            "correct_answers": ["b"],
            "explanation": "Taking B as (0,0): A is (0, -10). C is (12, 0). D is (12, 6). Vector AD: dx = 12 - 0 = 12, dy = 6 - (-10) = 16. Distance = sqrt(12^2 + 16^2) = sqrt(144 + 256) = sqrt(400) = 20 m.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In how many ways can a cricket team of 11 players be chosen out of 15 players if a particular player must always be included?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Permutations & Combinations",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "1001"},
                {"id": "b", "text": "1365"},
                {"id": "c", "text": "1820"},
                {"id": "d", "text": "2002"}
            ],
            "correct_answers": ["a"],
            "explanation": "Since 1 player is definitely included, we need to choose the remaining 10 players from the remaining 14 players: 14C10 = 14C4 = (14 * 13 * 12 * 11) / (4 * 3 * 2 * 1) = 1001.",
            "marks": 1.0,
            "negative_marks": 0.25
        }
    ]

def get_coding_questions():
    """Returns 30 verified Coding Fundamentals & Output Prediction questions."""
    return [
        {
            "question_text": "What is the output of the following Python code snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Mechanics",
            "difficulty": "Beginner",
            "code_snippet": "x = [1, 2, 3]\ny = x\nx.append(4)\nprint(y)",
            "language": "python",
            "options": [
                {"id": "a", "text": "[1, 2, 3]"},
                {"id": "b", "text": "[1, 2, 3, 4]"},
                {"id": "c", "text": "[4]"},
                {"id": "d", "text": "TypeError"}
            ],
            "correct_answers": ["b"],
            "explanation": "In Python, lists are mutable objects and variables hold references. 'y = x' copies the reference to the same memory location, so modifying x also reflects in y.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the time complexity of searching an element in a balanced Binary Search Tree (BST) with N nodes in the worst case?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Asymptotic Analysis",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "O(1)"},
                {"id": "b", "text": "O(log N)"},
                {"id": "c", "text": "O(N)"},
                {"id": "d", "text": "O(N log N)"}
            ],
            "correct_answers": ["b"],
            "explanation": "In a balanced BST (such as AVL or Red-Black Tree), the height of the tree is bounded by O(log N). Thus, lookup takes at most O(log N) comparisons.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following C code?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "C Pointers",
            "difficulty": "Intermediate",
            "code_snippet": "#include <stdio.h>\nint main() {\n    int a[] = {10, 20, 30, 40};\n    int *p = a;\n    printf(\"%d\", *(p + 2));\n    return 0;\n}",
            "language": "c",
            "options": [
                {"id": "a", "text": "10"},
                {"id": "b", "text": "20"},
                {"id": "c", "text": "30"},
                {"id": "d", "text": "40"}
            ],
            "correct_answers": ["c"],
            "explanation": "*(p + 2) accesses the element at index 2 of array a, which is 30.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What will be printed by the following JavaScript code?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "JavaScript Scope & Closures",
            "difficulty": "Intermediate",
            "code_snippet": "console.log(typeof NaN);\nconsole.log(NaN === NaN);",
            "language": "javascript",
            "options": [
                {"id": "a", "text": "'number' and true"},
                {"id": "b", "text": "'number' and false"},
                {"id": "c", "text": "'undefined' and false"},
                {"id": "d", "text": "'NaN' and true"}
            ],
            "correct_answers": ["b"],
            "explanation": "In JavaScript, typeof NaN is 'number' (IEEE 754 floating point standard), and NaN is the only value in JavaScript that is not strictly equal to itself (NaN === NaN evaluates to false).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which of the following data structures is most suitable for implementing a LIFO (Last-In, First-Out) buffer?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Stacks & Queues",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Queue"},
                {"id": "b", "text": "Stack"},
                {"id": "c", "text": "Linked List"},
                {"id": "d", "text": "Binary Heap"}
            ],
            "correct_answers": ["b"],
            "explanation": "A Stack operates strictly under the LIFO (Last-In, First-Out) principle via push and pop operations.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Strings & Slicing",
            "difficulty": "Beginner",
            "code_snippet": "s = 'SkillRock'\nprint(s[1:6:2])",
            "language": "python",
            "options": [
                {"id": "a", "text": "'kll'"},
                {"id": "b", "text": "'klR'"},
                {"id": "c", "text": "'kiR'"},
                {"id": "d", "text": "'klo'"}
            ],
            "correct_answers": ["b"],
            "explanation": "s[1:6:2] takes characters from index 1 up to index 5 with a step of 2. Index 1 is 'k', index 3 is 'l', index 5 is 'R', producing 'klR'.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the worst-case time complexity of QuickSort?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Sorting Algorithms",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "O(N log N)"},
                {"id": "b", "text": "O(N)"},
                {"id": "c", "text": "O(N^2)"},
                {"id": "d", "text": "O(2^N)"}
            ],
            "correct_answers": ["c"],
            "explanation": "QuickSort degrades to O(N^2) worst-case when the chosen pivot consistently partitions the array into highly unbalanced subarrays (e.g., already sorted array with first or last element as pivot).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What does the following recursive function compute for f(5)?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Recursion",
            "difficulty": "Beginner",
            "code_snippet": "def f(n):\n    if n <= 1:\n        return 1\n    return n * f(n - 1)",
            "language": "python",
            "options": [
                {"id": "a", "text": "15"},
                {"id": "b", "text": "25"},
                {"id": "c", "text": "120"},
                {"id": "d", "text": "720"}
            ],
            "correct_answers": ["c"],
            "explanation": "f(5) = 5 * 4 * 3 * 2 * 1 = 120 (computes factorial 5!).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In Object-Oriented Programming, which principle allows different classes to respond to the same method call with their own specific behavior?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Programming Fundamentals",
            "subtopic": "OOP Concepts",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Encapsulation"},
                {"id": "b", "text": "Polymorphism"},
                {"id": "c", "text": "Inheritance"},
                {"id": "d", "text": "Abstraction"}
            ],
            "correct_answers": ["b"],
            "explanation": "Polymorphism ('many forms') allows subclasses to provide specific implementations of methods defined by their parent class or interface.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Java snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Java String Pool",
            "difficulty": "Intermediate",
            "code_snippet": "String s1 = \"Hello\";\nString s2 = new String(\"Hello\");\nSystem.out.println((s1 == s2) + \" \" + s1.equals(s2));",
            "language": "java",
            "options": [
                {"id": "a", "text": "true true"},
                {"id": "b", "text": "false false"},
                {"id": "c", "text": "false true"},
                {"id": "d", "text": "true false"}
            ],
            "correct_answers": ["c"],
            "explanation": "s1 refers to a string in the String Constant Pool, while s2 refers to a new object on the heap. '==' compares memory addresses (false), while equals() compares textual values (true).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which SQL clause is used to filter records resulting from an aggregate GROUP BY operation?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Database & SQL",
            "subtopic": "SQL Queries",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "WHERE"},
                {"id": "b", "text": "HAVING"},
                {"id": "c", "text": "ORDER BY"},
                {"id": "d", "text": "FILTER"}
            ],
            "correct_answers": ["b"],
            "explanation": "The HAVING clause filters aggregated groups after GROUP BY, whereas WHERE filters individual rows before grouping.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python dictionary comprehension?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Comprehensions",
            "difficulty": "Beginner",
            "code_snippet": "d = {x: x**2 for x in (1, 2, 3)}\nprint(d[2])",
            "language": "python",
            "options": [
                {"id": "a", "text": "2"},
                {"id": "b", "text": "4"},
                {"id": "c", "text": "8"},
                {"id": "d", "text": "KeyError"}
            ],
            "correct_answers": ["b"],
            "explanation": "The dictionary maps x to x^2. For key 2, value is 2**2 = 4.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In a singly linked list with N nodes, what is the time complexity to insert a node at the head (beginning)?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Linked Lists",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "O(1)"},
                {"id": "b", "text": "O(log N)"},
                {"id": "c", "text": "O(N)"},
                {"id": "d", "text": "O(N^2)"}
            ],
            "correct_answers": ["a"],
            "explanation": "Inserting at the head requires creating a node, pointing its next pointer to the current head, and updating the head pointer. This takes constant time O(1).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What will be printed by the following Python snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Generators",
            "difficulty": "Intermediate",
            "code_snippet": "def gen():\n    yield 1\n    yield 2\ng = gen()\nprint(next(g) + next(g))",
            "language": "python",
            "options": [
                {"id": "a", "text": "1"},
                {"id": "b", "text": "2"},
                {"id": "c", "text": "3"},
                {"id": "d", "text": "StopIteration"}
            ],
            "correct_answers": ["c"],
            "explanation": "First next(g) yields 1, second next(g) yields 2. 1 + 2 = 3.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the primary difference between a process and a thread in operating systems?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Operating Systems",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "Threads have independent address spaces, while processes share memory."},
                {"id": "b", "text": "Processes share address space, while threads do not."},
                {"id": "c", "text": "Threads of the same process share code, data, and files, while processes have separate address spaces."},
                {"id": "d", "text": "Processes cannot run in parallel on multi-core CPUs."}
            ],
            "correct_answers": ["c"],
            "explanation": "Threads within a process share the same memory space (heap, global variables, code segment) but have individual stacks, whereas processes are isolated with their own virtual address spaces.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following C++ code?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "C++ Operator Precedence",
            "difficulty": "Beginner",
            "code_snippet": "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 5;\n    int y = x++ + ++x;\n    cout << y;\n    return 0;\n}",
            "language": "cpp",
            "options": [
                {"id": "a", "text": "10"},
                {"id": "b", "text": "11"},
                {"id": "c", "text": "12"},
                {"id": "d", "text": "13"}
            ],
            "correct_answers": ["c"],
            "explanation": "In standard evaluation sequence: x++ yields 5 (and increments x to 6). Then ++x increments x to 7 and yields 7. 5 + 7 = 12.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which HTTP status code signifies that a resource was created successfully on the server in a RESTful API?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Computer Networks & APIs",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "200 OK"},
                {"id": "b", "text": "201 Created"},
                {"id": "c", "text": "204 No Content"},
                {"id": "d", "text": "301 Moved Permanently"}
            ],
            "correct_answers": ["b"],
            "explanation": "HTTP 201 Created indicates that the request has succeeded and has resulted in the creation of a new resource on the server.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python code?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Boolean Logic",
            "difficulty": "Intermediate",
            "code_snippet": "print([] or 'Python' and [0] or 100)",
            "language": "python",
            "options": [
                {"id": "a", "text": "[]"},
                {"id": "b", "text": "'Python'"},
                {"id": "c", "text": "[0]"},
                {"id": "d", "text": "100"}
            ],
            "correct_answers": ["c"],
            "explanation": "'and' has higher precedence than 'or'. 'Python' and [0]: 'Python' is truthy, so it evaluates to [0] (which is truthy). Then [] or [0] evaluates to [0]. Finally [0] or 100 short-circuits to [0].",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the minimum number of queues needed to implement a Stack?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Stacks & Queues",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "1"},
                {"id": "b", "text": "2"},
                {"id": "c", "text": "3"},
                {"id": "d", "text": "Cannot be implemented using queues"}
            ],
            "correct_answers": ["a"],
            "explanation": "A stack can be implemented using a single queue by rotating elements on each push: after enqueuing an element of size N, pop and re-enqueue the previous N-1 elements so the newly added element is at the front.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In relational databases, which normal form eliminates transitive dependencies?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Database & SQL",
            "subtopic": "Database Normalization",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "First Normal Form (1NF)"},
                {"id": "b", "text": "Second Normal Form (2NF)"},
                {"id": "c", "text": "Third Normal Form (3NF)"},
                {"id": "d", "text": "Boyce-Codd Normal Form (BCNF)"}
            ],
            "correct_answers": ["c"],
            "explanation": "3NF requires a table to be in 2NF and have no transitive functional dependencies (no non-prime attribute should be determined by another non-prime attribute).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What does the following Python expression evaluate to?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Sets",
            "difficulty": "Beginner",
            "code_snippet": "a = {1, 2, 3}\nb = {3, 4, 5}\nprint(len(a ^ b))",
            "language": "python",
            "options": [
                {"id": "a", "text": "1"},
                {"id": "b", "text": "4"},
                {"id": "c", "text": "5"},
                {"id": "d", "text": "6"}
            ],
            "correct_answers": ["b"],
            "explanation": "The '^' operator computes symmetric difference (elements in either set but not in both). a ^ b = {1, 2, 4, 5}, which has 4 elements.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which data structure is utilized internally by Dijkstra's algorithm to retrieve the minimum distance vertex in optimal O((V + E) log V) time?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Graph Algorithms",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "Hash Map"},
                {"id": "b", "text": "Min-Priority Queue (Binary/Fibonacci Heap)"},
                {"id": "c", "text": "Disjoint Set Union (DSU)"},
                {"id": "d", "text": "Trie"}
            ],
            "correct_answers": ["b"],
            "explanation": "Dijkstra's algorithm uses a Min-Heap / Priority Queue to greedily extract the vertex with minimum tentative distance in logarithmic time.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Java program?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Java Exceptions",
            "difficulty": "Intermediate",
            "code_snippet": "public class Test {\n    public static int check() {\n        try {\n            return 1;\n        } finally {\n            return 2;\n        }\n    }\n    public static void main(String[] args) {\n        System.out.println(check());\n    }\n}",
            "language": "java",
            "options": [
                {"id": "a", "text": "1"},
                {"id": "b", "text": "2"},
                {"id": "c", "text": "Compilation Error"},
                {"id": "d", "text": "Runtime Exception"}
            ],
            "correct_answers": ["b"],
            "explanation": "The 'finally' block in Java executes before the method returns. A return statement in finally overrides any preceding return statement in the try or catch block, returning 2.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the auxiliary space complexity of standard Depth-First Search (DFS) on a graph with V vertices in the worst case (e.g. linear chain graph)?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Graph Algorithms",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "O(1)"},
                {"id": "b", "text": "O(log V)"},
                {"id": "c", "text": "O(V)"},
                {"id": "d", "text": "O(V^2)"}
            ],
            "correct_answers": ["c"],
            "explanation": "In the worst case (e.g. a skewed tree or linear chain of vertices), the recursion call stack can grow up to O(V) frames.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What will be printed by the following Python lambda expression?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Functional Programming in Python",
            "difficulty": "Beginner",
            "code_snippet": "funcs = [lambda x: x + i for i in range(3)]\nprint([f(10) for f in funcs])",
            "language": "python",
            "options": [
                {"id": "a", "text": "[10, 11, 12]"},
                {"id": "b", "text": "[12, 12, 12]"},
                {"id": "c", "text": "[10, 10, 10]"},
                {"id": "d", "text": "TypeError"}
            ],
            "correct_answers": ["b"],
            "explanation": "Due to late binding of closures in Python, the variable 'i' is looked up when the lambda is called, at which point the loop has finished and i=2. Thus each lambda evaluates 10 + 2 = 12.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which design pattern ensures a class has only one instance and provides a global access point to it?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Design Patterns",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Factory Pattern"},
                {"id": "b", "text": "Singleton Pattern"},
                {"id": "c", "text": "Observer Pattern"},
                {"id": "d", "text": "Adapter Pattern"}
            ],
            "correct_answers": ["b"],
            "explanation": "The Singleton Pattern restricts instantiation of a class to a single object across the entire application lifetime.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following C code snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "C Bitwise Operations",
            "difficulty": "Beginner",
            "code_snippet": "#include <stdio.h>\nint main() {\n    int a = 12; // 1100 in binary\n    int b = 10; // 1010 in binary\n    printf(\"%d\", a & b);\n    return 0;\n}",
            "language": "c",
            "options": [
                {"id": "a", "text": "8"},
                {"id": "b", "text": "10"},
                {"id": "c", "text": "12"},
                {"id": "d", "text": "14"}
            ],
            "correct_answers": ["a"],
            "explanation": "Binary bitwise AND: 1100 & 1010 = 1000 in binary, which equals 8 in decimal.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In ACID properties of database transactions, what does the 'I' stand for?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Database & SQL",
            "subtopic": "Transactions & Concurrency",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Integrity"},
                {"id": "b", "text": "Independence"},
                {"id": "c", "text": "Isolation"},
                {"id": "d", "text": "Idempotence"}
            ],
            "correct_answers": ["c"],
            "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability. Isolation guarantees that concurrent transactions execute without interfering with one another.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python list manipulation?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Lists",
            "difficulty": "Beginner",
            "code_snippet": "arr = [1, 2, 3]\narr.extend([4, 5])\narr.pop(1)\nprint(arr)",
            "language": "python",
            "options": [
                {"id": "a", "text": "[1, 3, 4, 5]"},
                {"id": "b", "text": "[2, 3, 4, 5]"},
                {"id": "c", "text": "[1, 2, 4, 5]"},
                {"id": "d", "text": "[1, 3, 5]"}
            ],
            "correct_answers": ["a"],
            "explanation": "extend([4, 5]) results in [1, 2, 3, 4, 5]. pop(1) removes the element at index 1 (which is 2), leaving [1, 3, 4, 5].",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which layer of the OSI model is responsible for end-to-end communication, flow control, and error recovery (e.g. TCP)?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Computer Networks",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Network Layer"},
                {"id": "b", "text": "Transport Layer"},
                {"id": "c", "text": "Data Link Layer"},
                {"id": "d", "text": "Session Layer"}
            ],
            "correct_answers": ["b"],
            "explanation": "The Transport Layer (Layer 4) handles host-to-host communication, segmenting data, flow control, and reliable delivery protocols such as TCP.",
            "marks": 1.0,
            "negative_marks": 0.25
        }
    ]

def get_mixed_mock_questions():
    """Returns 30 balanced Mixed Placement Mock questions spanning Aptitude, DSA, Web, and Core CS."""
    return [
        {
            "question_text": "A car covers a distance of 450 km in 5 hours. What is its speed in meters per second?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Speed, Time & Distance",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "20 m/s"},
                {"id": "b", "text": "25 m/s"},
                {"id": "c", "text": "30 m/s"},
                {"id": "d", "text": "35 m/s"}
            ],
            "correct_answers": ["b"],
            "explanation": "Speed = 450 km / 5 hrs = 90 km/hr. Converting to m/s: 90 * (5/18) = 25 m/s.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python boolean expression?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Logic",
            "difficulty": "Beginner",
            "code_snippet": "print(bool('False') == False)",
            "language": "python",
            "options": [
                {"id": "a", "text": "True"},
                {"id": "b", "text": "False"},
                {"id": "c", "text": "None"},
                {"id": "d", "text": "SyntaxError"}
            ],
            "correct_answers": ["b"],
            "explanation": "'False' is a non-empty string, so bool('False') evaluates to True. True == False is False.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the time complexity of building a heap from an unsorted array of N elements using the bottom-up Heapify approach?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Heaps",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "O(N)"},
                {"id": "b", "text": "O(N log N)"},
                {"id": "c", "text": "O(log N)"},
                {"id": "d", "text": "O(N^2)"}
            ],
            "correct_answers": ["a"],
            "explanation": "Bottom-up heap construction runs in mathematically proven linear O(N) time because the majority of nodes are at the lower levels and require few sift-down steps.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A sum of money doubled itself in 5 years at simple interest. In how many years will it become 4 times of itself at the same rate?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Simple Interest",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "10 years"},
                {"id": "b", "text": "12 years"},
                {"id": "c", "text": "15 years"},
                {"id": "d", "text": "20 years"}
            ],
            "correct_answers": ["c"],
            "explanation": "To double itself, SI = P. Time = 5 years, so Rate = (100 * P)/(P * 5) = 20% per year. To become 4 times, SI needed = 3P. Time = (3P * 100)/(P * 20) = 300 / 20 = 15 years.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which of the following sorting algorithms is stable by default?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Sorting Algorithms",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Heap Sort"},
                {"id": "b", "text": "Quick Sort"},
                {"id": "c", "text": "Merge Sort"},
                {"id": "d", "text": "Selection Sort"}
            ],
            "correct_answers": ["c"],
            "explanation": "Merge Sort preserves the relative order of equal elements, making it a stable sort.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What does a 403 Forbidden HTTP status code mean?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Web & APIs",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "The requested resource could not be found."},
                {"id": "b", "text": "The client must authenticate itself to get the requested response."},
                {"id": "c", "text": "The server understood the request, but refuses to authorize it."},
                {"id": "d", "text": "The server encountered an unexpected error."}
            ],
            "correct_answers": ["c"],
            "explanation": "403 Forbidden indicates that the server understands who the user is, but the user does not have permission to access the resource (distinct from 401 Unauthorized which implies missing or invalid credentials).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Unpacking",
            "difficulty": "Intermediate",
            "code_snippet": "a, *b, c = [1, 2, 3, 4, 5]\nprint(b)",
            "language": "python",
            "options": [
                {"id": "a", "text": "[2, 3, 4]"},
                {"id": "b", "text": "[1, 2, 3]"},
                {"id": "c", "text": "[3, 4, 5]"},
                {"id": "d", "text": "(2, 3, 4)"}
            ],
            "correct_answers": ["a"],
            "explanation": "Extended iterable unpacking assigns the first element to a (1), the last to c (5), and captures all intermediate items as a list in b: [2, 3, 4].",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "If 12 machines can produce 2400 units in 6 hours, how many units can 18 machines produce in 8 hours?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Unitary Method",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "3600"},
                {"id": "b", "text": "4200"},
                {"id": "c", "text": "4800"},
                {"id": "d", "text": "5400"}
            ],
            "correct_answers": ["c"],
            "explanation": "Work rate per machine-hour = 2400 / (12 * 6) = 2400 / 72 = 100/3 units. For 18 machines over 8 hours = 18 * 8 * (100/3) = 144 * (100/3) = 48 * 100 = 4800 units.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following SQL statement if table 'Employees' has 10 rows and 2 rows have salary as NULL?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Database & SQL",
            "subtopic": "SQL Aggregates",
            "difficulty": "Intermediate",
            "code_snippet": "SELECT COUNT(*), COUNT(salary) FROM Employees;",
            "language": "sql",
            "options": [
                {"id": "a", "text": "10 and 10"},
                {"id": "b", "text": "10 and 8"},
                {"id": "c", "text": "8 and 8"},
                {"id": "d", "text": "10 and NULL"}
            ],
            "correct_answers": ["b"],
            "explanation": "COUNT(*) counts all rows regardless of nulls (10), while COUNT(column) ignores NULL values in that specific column (10 - 2 = 8).",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In graph theory, what is the maximum number of edges in an undirected simple graph with V vertices?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Graph Theory",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "V * (V - 1)"},
                {"id": "b", "text": "V * (V - 1) / 2"},
                {"id": "c", "text": "V^2"},
                {"id": "d", "text": "2^V"}
            ],
            "correct_answers": ["b"],
            "explanation": "In an undirected graph, each pair of vertices can have at most one edge between them. The number of unique pairs is VC2 = V * (V - 1) / 2.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which deadlock handling strategy requires processes to request all resources at once before execution begins?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Operating Systems",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "Deadlock Detection"},
                {"id": "b", "text": "Mutual Exclusion Prevention"},
                {"id": "c", "text": "Hold and Wait Prevention"},
                {"id": "d", "text": "Circular Wait Prevention"}
            ],
            "correct_answers": ["c"],
            "explanation": "Holding and waiting occurs when a process holds resources while waiting for additional ones. Requiring all resources upfront eliminates the 'Hold and Wait' condition.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the result of the following Python operation?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Operators",
            "difficulty": "Beginner",
            "code_snippet": "print(2 ** 3 ** 2)",
            "language": "python",
            "options": [
                {"id": "a", "text": "64"},
                {"id": "b", "text": "512"},
                {"id": "c", "text": "256"},
                {"id": "d", "text": "36"}
            ],
            "correct_answers": ["b"],
            "explanation": "The exponentiation operator ** in Python is right-associative: 3 ** 2 is evaluated first (9), then 2 ** 9 = 512.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In a group of 60 students, 35 like Tea, 25 like Coffee, and 10 like both. How many students like neither Tea nor Coffee?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Set Theory",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "5"},
                {"id": "b", "text": "10"},
                {"id": "c", "text": "15"},
                {"id": "d", "text": "20"}
            ],
            "correct_answers": ["b"],
            "explanation": "N(T U C) = N(T) + N(C) - N(T n C) = 35 + 25 - 10 = 50. Students liking neither = Total - N(T U C) = 60 - 50 = 10.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following JavaScript promise snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "JavaScript Event Loop",
            "difficulty": "Intermediate",
            "code_snippet": "console.log('A');\nsetTimeout(() => console.log('B'), 0);\nPromise.resolve().then(() => console.log('C'));\nconsole.log('D');",
            "language": "javascript",
            "options": [
                {"id": "a", "text": "A, B, C, D"},
                {"id": "b", "text": "A, D, B, C"},
                {"id": "c", "text": "A, D, C, B"},
                {"id": "d", "text": "A, C, D, B"}
            ],
            "correct_answers": ["c"],
            "explanation": "Synchronous statements run first ('A', 'D'). Microtasks (Promise.then) run immediately after synchronous execution before macrotasks ('C'). Finally, the macrotask queue (setTimeout) runs ('B'). Output: A, D, C, B.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which algorithm is used to find the strongly connected components (SCCs) of a directed graph in linear O(V + E) time?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Graph Algorithms",
            "difficulty": "Advanced",
            "options": [
                {"id": "a", "text": "Tarjan's or Kosaraju's Algorithm"},
                {"id": "b", "text": "Floyd-Warshall Algorithm"},
                {"id": "c", "text": "Prim's Algorithm"},
                {"id": "d", "text": "Bellman-Ford Algorithm"}
            ],
            "correct_answers": ["a"],
            "explanation": "Both Tarjan's algorithm (using low-link values in a single DFS pass) and Kosaraju's algorithm (using transpose graph and two DFS passes) compute SCCs in O(V + E) time.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "If SOUTH-EAST becomes NORTH, NORTH-EAST becomes WEST and so on, what will WEST become?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Direction Sense",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "South-East"},
                {"id": "b", "text": "South-West"},
                {"id": "c", "text": "North-East"},
                {"id": "d", "text": "North-West"}
            ],
            "correct_answers": ["a"],
            "explanation": "South-East to North is a 135-degree anti-clockwise rotation. Rotating West by 135 degrees anti-clockwise lands on South-East.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the primary role of an index on a database table?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Database & SQL",
            "subtopic": "Indexing & Optimization",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "To enforce foreign key relationships."},
                {"id": "b", "text": "To speed up data retrieval operations at the cost of additional storage and slower writes."},
                {"id": "c", "text": "To compress data stored in table columns."},
                {"id": "d", "text": "To prevent duplicate row insertions automatically."}
            ],
            "correct_answers": ["b"],
            "explanation": "Database indexes (commonly B-Trees) enable sub-linear lookup times for SELECT queries while requiring extra disk storage and slight overhead during INSERT/UPDATE operations.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What will be the output of the following Python code?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Mutable Defaults",
            "difficulty": "Intermediate",
            "code_snippet": "def append_item(val, items=[]):\n    items.append(val)\n    return items\n\nappend_item(1)\nprint(append_item(2))",
            "language": "python",
            "options": [
                {"id": "a", "text": "[2]"},
                {"id": "b", "text": "[1, 2]"},
                {"id": "c", "text": "[[1], [2]]"},
                {"id": "d", "text": "TypeError"}
            ],
            "correct_answers": ["b"],
            "explanation": "Default arguments in Python are evaluated once when the function is defined. The mutable list 'items' persists across function invocations, giving [1, 2].",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "In a 100m race, A beats B by 10m and B beats C by 10m. By how many meters does A beat C?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Races & Games",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "19 m"},
                {"id": "b", "text": "20 m"},
                {"id": "c", "text": "21 m"},
                {"id": "d", "text": "18 m"}
            ],
            "correct_answers": ["a"],
            "explanation": "When A runs 100m, B runs 90m (B = 0.9 * A). When B runs 100m, C runs 90m (C = 0.9 * B). When A runs 100m, C runs 0.9 * 90 = 81m. Thus A beats C by 100 - 81 = 19 meters.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which tree traversal of a Binary Search Tree (BST) produces the keys in non-decreasing sorted order?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Trees",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Pre-order Traversal"},
                {"id": "b", "text": "In-order Traversal"},
                {"id": "c", "text": "Post-order Traversal"},
                {"id": "d", "text": "Level-order Traversal"}
            ],
            "correct_answers": ["b"],
            "explanation": "In-order traversal visits left subtree, root, then right subtree. Since all left nodes in a BST are smaller and right nodes are larger, this visits nodes in ascending sorted order.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the primary function of the DNS (Domain Name System) protocol?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Computer Networks",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Encrypting network traffic over SSL/TLS."},
                {"id": "b", "text": "Translating human-readable domain names (e.g. skillrock.onrender.com) into IP addresses."},
                {"id": "c", "text": "Routing packets across intermediate routers."},
                {"id": "d", "text": "Allocating dynamic IP addresses to client devices."}
            ],
            "correct_answers": ["b"],
            "explanation": "DNS acts as the phonebook of the internet, mapping human-friendly domain names to machine-routable IP addresses.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What will be printed by the following Python program?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Tuple Immutability",
            "difficulty": "Beginner",
            "code_snippet": "t = (1, [2, 3])\nt[1].append(4)\nprint(t)",
            "language": "python",
            "options": [
                {"id": "a", "text": "(1, [2, 3])"},
                {"id": "b", "text": "(1, [2, 3, 4])"},
                {"id": "c", "text": "TypeError: 'tuple' object does not support item assignment"},
                {"id": "d", "text": "(1, 2, 3, 4)"}
            ],
            "correct_answers": ["b"],
            "explanation": "Tuples are immutable in structure, but the object stored at index 1 is a mutable list. Calling .append() mutates the list without changing the reference held by the tuple.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "A man is facing North-West. He turns 90 degrees in the clockwise direction and then 135 degrees in the anti-clockwise direction. Which direction is he facing now?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Logical Reasoning",
            "subtopic": "Direction Sense",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "East"},
                {"id": "b", "text": "West"},
                {"id": "c", "text": "North"},
                {"id": "d", "text": "South"}
            ],
            "correct_answers": ["b"],
            "explanation": "Net rotation = +90 - 135 = -45 degrees (45 degrees anti-clockwise). 45 degrees anti-clockwise from North-West is West.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the worst-case time complexity of checking if a key exists in a well-distributed Hash Table of N elements?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Hashing",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "O(1)"},
                {"id": "b", "text": "O(log N)"},
                {"id": "c", "text": "O(N)"},
                {"id": "d", "text": "O(N log N)"}
            ],
            "correct_answers": ["c"],
            "explanation": "Average case is O(1), but in the worst case (all N keys hash to the exact same bucket causing a collision chain), lookup requires searching the entire chain taking O(N) time.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which of the following is true about Virtual Memory in modern Operating Systems?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Operating Systems",
            "difficulty": "Intermediate",
            "options": [
                {"id": "a", "text": "It completely replaces the need for physical RAM."},
                {"id": "b", "text": "It allows execution of processes whose memory footprint exceeds physical RAM by swapping pages to disk."},
                {"id": "c", "text": "It is implemented purely in software with no CPU/MMU hardware support."},
                {"id": "d", "text": "It makes address translation slower and cannot provide memory protection."}
            ],
            "correct_answers": ["b"],
            "explanation": "Virtual memory provides an abstraction of uniform memory and allows programs larger than physical memory to execute via paging and swap space managed with hardware MMU support.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python code snippet?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Iterators",
            "difficulty": "Beginner",
            "code_snippet": "data = [1, 2, 3]\nresult = [x * 2 for x in data if x > 1]\nprint(sum(result))",
            "language": "python",
            "options": [
                {"id": "a", "text": "6"},
                {"id": "b", "text": "8"},
                {"id": "c", "text": "10"},
                {"id": "d", "text": "12"}
            ],
            "correct_answers": ["c"],
            "explanation": "For x in [1, 2, 3], elements > 1 are 2 and 3. Multiplied by 2: [4, 6]. Sum is 4 + 6 = 10.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the cardinality of the Cartesian Product A x B if set A has 4 elements and set B has 3 elements?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Quantitative Aptitude",
            "subtopic": "Set Theory",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "7"},
                {"id": "b", "text": "12"},
                {"id": "c", "text": "16"},
                {"id": "d", "text": "64"}
            ],
            "correct_answers": ["b"],
            "explanation": "|A x B| = |A| * |B| = 4 * 3 = 12.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which sorting algorithm is optimal when data is almost already sorted?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Data Structures & Algorithms",
            "subtopic": "Sorting Algorithms",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "Insertion Sort"},
                {"id": "b", "text": "Selection Sort"},
                {"id": "c", "text": "Heap Sort"},
                {"id": "d", "text": "Quick Sort with middle pivot"}
            ],
            "correct_answers": ["a"],
            "explanation": "Insertion Sort has an O(N) best-case time complexity when the input array is already or nearly sorted, making it very fast and efficient in that scenario.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "What is the output of the following Python string operation?",
            "question_type": Question.TYPE_CODE_OUTPUT,
            "category": "Programming Fundamentals",
            "subtopic": "Python Strings",
            "difficulty": "Beginner",
            "code_snippet": "words = ['Interview', 'Test', 'Series']\nprint('-'.join(words[:2]))",
            "language": "python",
            "options": [
                {"id": "a", "text": "'Interview-Test-Series'"},
                {"id": "b", "text": "'Interview-Test'"},
                {"id": "c", "text": "'Test-Series'"},
                {"id": "d", "text": "['Interview', 'Test']"}
            ],
            "correct_answers": ["b"],
            "explanation": "words[:2] slices the first two items: ['Interview', 'Test']. Joining them with '-' results in 'Interview-Test'.",
            "marks": 1.0,
            "negative_marks": 0.25
        },
        {
            "question_text": "Which cryptographic hash function produces a 256-bit digest widely used for blockchain and digital certificates?",
            "question_type": Question.TYPE_SINGLE_CHOICE,
            "category": "Computer Science Fundamentals",
            "subtopic": "Cybersecurity & Cryptography",
            "difficulty": "Beginner",
            "options": [
                {"id": "a", "text": "MD5"},
                {"id": "b", "text": "SHA-1"},
                {"id": "c", "text": "SHA-256"},
                {"id": "d", "text": "DES"}
            ],
            "correct_answers": ["c"],
            "explanation": "SHA-256 (Secure Hash Algorithm 256-bit) is a member of the SHA-2 family producing a 32-byte (256-bit) one-way hash value.",
            "marks": 1.0,
            "negative_marks": 0.25
        }
    ]

def ensure_default_test_series(database=None):
    """
    Seeds default test series questions, 3 free tests, and 4 test packs.
    Safe and idempotent: runs if tests or packs do not exist yet.
    """
    from models.mongo import get_db
    if database is None:
        database = get_db()

    # 1. Seed or retrieve question banks
    test_1_q_ids = []
    for q_data in get_aptitude_questions():
        existing = database[Question.collection_name].find_one({"question_text": q_data["question_text"]})
        if not existing:
            q = Question(q_data).save()
            test_1_q_ids.append(q.id)
        else:
            test_1_q_ids.append(str(existing["_id"]))

    test_2_q_ids = []
    for q_data in get_coding_questions():
        existing = database[Question.collection_name].find_one({"question_text": q_data["question_text"]})
        if not existing:
            q = Question(q_data).save()
            test_2_q_ids.append(q.id)
        else:
            test_2_q_ids.append(str(existing["_id"]))

    test_3_q_ids = []
    for q_data in get_mixed_mock_questions():
        existing = database[Question.collection_name].find_one({"question_text": q_data["question_text"]})
        if not existing:
            q = Question(q_data).save()
            test_3_q_ids.append(q.id)
        else:
            test_3_q_ids.append(str(existing["_id"]))

    # 2. Seed Initial 3 Free Tests
    tests_spec = [
        {
            "slug": "aptitude-and-logical-reasoning",
            "title": "Aptitude and Logical Reasoning",
            "description": "30-minute campus screening mock covering quantitative aptitude, percentages, ratios, averages, number series, direction sense, and deductive logic.",
            "category": "Quantitative Aptitude",
            "difficulty": "Beginner",
            "duration_minutes": 30,
            "total_questions_count": 30,
            "passing_percentage": 50.0,
            "is_free": True,
            "question_ids": test_1_q_ids,
            "video_resources": [
                {
                    "title": "Quantitative Aptitude Short Tricks & Formulas",
                    "youtube_url": "https://www.youtube.com/watch?v=SydnP5a4-5U",
                    "topic": "Quantitative Aptitude",
                    "description": "Master essential speed math, percentages, time-work shortcuts, and ratio methods."
                }
            ],
            "display_order": 1
        },
        {
            "slug": "coding-fundamentals",
            "title": "Coding Fundamentals",
            "description": "30-minute technical test focusing on programming logic, loops, memory references, time complexity, output prediction, and core OOP.",
            "category": "Programming Fundamentals",
            "difficulty": "Intermediate",
            "duration_minutes": 30,
            "total_questions_count": 30,
            "passing_percentage": 50.0,
            "is_free": True,
            "question_ids": test_2_q_ids,
            "video_resources": [
                {
                    "title": "Data Structures & Core Programming Fundamentals",
                    "youtube_url": "https://www.youtube.com/watch?v=RBSGKlAvoiM",
                    "topic": "Data Structures & Algorithms",
                    "description": "Comprehensive review of asymptotic analysis, stacks, queues, trees, and pointer mechanics."
                }
            ],
            "display_order": 2
        },
        {
            "slug": "mixed-placement-mock",
            "title": "Mixed Placement Mock",
            "description": "30-minute comprehensive simulation balancing mathematical aptitude, logical reasoning, data structures, SQL queries, and core operating system concepts.",
            "category": "Company-Style Placement Preparation",
            "difficulty": "Intermediate",
            "duration_minutes": 30,
            "total_questions_count": 30,
            "passing_percentage": 50.0,
            "is_free": True,
            "question_ids": test_3_q_ids,
            "video_resources": [
                {
                    "title": "Tech Interview Roadmap & Mock Assessment Strategy",
                    "youtube_url": "https://www.youtube.com/watch?v=pkYVOmU3BlA",
                    "topic": "Interview Preparation",
                    "description": "Top technical interview tips, time allocation strategies, and problem decomposition patterns."
                }
            ],
            "display_order": 3
        }
    ]

    created_test_ids = []
    for t_spec in tests_spec:
        existing = database[TestDefinition.collection_name].find_one({"slug": t_spec["slug"]})
        if not existing:
            t = TestDefinition(t_spec).save()
            created_test_ids.append(t.id)
        else:
            # Update questions linked to ensure 30 questions are present
            database[TestDefinition.collection_name].update_one(
                {"_id": existing["_id"]},
                {"$set": {"question_ids": t_spec["question_ids"], "total_questions_count": len(t_spec["question_ids"])}}
            )
            created_test_ids.append(str(existing["_id"]))

    # 3. Seed 4 Configurable Test Packs
    packs_spec = [
        {
            "slug": "free-starter",
            "title": "Free Starter",
            "short_description": "Kickstart placement prep with 3 full-length timed tests covering aptitude, coding logic, and mixed screening rounds.",
            "description": "The ideal entry point for all students. Practice real campus screening questions with zero cost, comprehensive solution reviews, and instant scoring.",
            "price_inr": 0,
            "is_free": True,
            "badge_text": "Free",
            "test_ids": created_test_ids,
            "features": [
                "3 Complete Timed Screening Tests",
                "90 Verified Questions & Step-by-Step Solutions",
                "Server-Timed Assessment Engine",
                "Instant Accuracy & Performance Breakdown",
                "Anti-Cheat Fair Assessment Tracking"
            ],
            "status": TestPack.STATUS_PUBLISHED,
            "display_order": 1
        },
        {
            "slug": "placement-practice",
            "title": "Placement Practice",
            "short_description": "Targeted practice for top service & product company screening tests.",
            "description": "5 comprehensive practice tests designed around modern IT placement assessment patterns. Features 300+ in-depth questions across quantitative reasoning, Python/Java debugging, and SQL.",
            "price_inr": 49,
            "is_free": False,
            "badge_text": "Popular",
            "test_ids": created_test_ids,
            "features": [
                "5 Full-Length Placement Practice Tests (~300 Questions)",
                "Detailed Step-by-Step Solution Explanations",
                "Topic-Wise Weak Area Diagnostic",
                "Curated Preparation Video Playlists",
                "Certificate of Placement Readiness"
            ],
            "status": TestPack.STATUS_COMING_SOON,
            "display_order": 2
        },
        {
            "slug": "interview-ready",
            "title": "Interview Ready",
            "short_description": "Advanced problem solving, algorithms, and technical interview simulations.",
            "description": "10 full-length interview tests covering advanced DSA, OOP architecture, database indexing, and behavioral round preparation with detailed solution guides.",
            "price_inr": 99,
            "is_free": False,
            "badge_text": "Best Value",
            "test_ids": created_test_ids,
            "features": [
                "10 Rigorous Technical Tests",
                "Advanced DSA & Output Prediction",
                "System & CS Fundamentals Deep Dive",
                "Full Video Masterclasses & Strategy Sessions",
                "Unlimited Test Retakes"
            ],
            "status": TestPack.STATUS_COMING_SOON,
            "display_order": 3
        },
        {
            "slug": "complete-placement-prep",
            "title": "Complete Placement Prep",
            "short_description": "The ultimate placement accelerator: 20 tests, company-specific patterns, and full progress analytics.",
            "description": "Comprehensive bundle covering 20 full-length tests across Quantitative Aptitude, Logical Reasoning, Verbal Ability, Coding, Data Structures, SQL, OS, and Networks.",
            "price_inr": 199,
            "is_free": False,
            "badge_text": "All-Inclusive",
            "test_ids": created_test_ids,
            "features": [
                "20 Full-Length Timed Assessments",
                "1,000+ Verified Questions with Deep Explanations",
                "Company-Pattern Mock Assessment Simulator",
                "Comprehensive Progress & Readiness Dashboard",
                "Priority Review & Learning Roadmaps"
            ],
            "status": TestPack.STATUS_COMING_SOON,
            "display_order": 4
        }
    ]

    for p_spec in packs_spec:
        existing = database[TestPack.collection_name].find_one({"slug": p_spec["slug"]})
        if not existing:
            TestPack(p_spec).save()
        else:
            # Update configuration without overriding active custom prices if already modified
            database[TestPack.collection_name].update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "features": p_spec["features"],
                    "short_description": p_spec["short_description"]
                }}
            )
